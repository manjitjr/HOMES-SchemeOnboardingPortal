import uuid
import io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from openpyxl import Workbook

from app.config import get_db
from app.auth import get_current_user
from app.models import (
    User, SchemeOverview, SchemeSubmission, SchemeMTParameters,
    TransactionDetails, HOMESFunctions, MTBands, APIBatchInterfaces,
    ChangeLog, Comment, SubmissionStatus, OnboardingSlot,
)

router = APIRouter(prefix="/api/schemes", tags=["schemes"])

# ── Pydantic schemas ────────────────────────────────────────────

class SchemeCreate(BaseModel):
    agency: str | None = None
    scheme_name: str
    scheme_code: str | None = None
    legislated_or_consent: str | None = None
    consent_scope: str | None = None
    background_info: dict | None = None

class SchemeUpdate(BaseModel):
    agency: str | None = None
    scheme_name: str | None = None
    scheme_code: str | None = None
    legislated_or_consent: str | None = None
    consent_scope: str | None = None
    background_info: dict | None = None

class TabUpdate(BaseModel):
    data: dict

class CommentCreate(BaseModel):
    text: str
    stage: str | None = None

class RejectBody(BaseModel):
    comment: str | None = None

class SlotSelection(BaseModel):
    year: int
    slot_month: int  # 1=Jan, 4=Apr, 7=Jul, 11=Nov
    technical_go_live: str  # ISO date string YYYY-MM-DD
    business_go_live: str  # ISO date string YYYY-MM-DD
    justification: str | None = None  # Required for is_additional=True

# ── Helpers ──────────────────────────────────────────────────────

TAB_MODEL_MAP = {
    "mt_parameters": SchemeMTParameters,
    "transactions": TransactionDetails,
    "homes_functions": HOMESFunctions,
    "mt_bands": MTBands,
    "api_interfaces": APIBatchInterfaces,
}

TAB_REL_MAP = {
    "mt_parameters": "mt_parameters",
    "transactions": "transactions",
    "homes_functions": "homes_functions",
    "mt_bands": "mt_bands",
    "api_interfaces": "api_interfaces",
}


def _require_role(user: User, *roles: str):
    if not user.has_role(*roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Roles {user.roles} not allowed")


def _assert_agency_access(user: User, sub: SchemeSubmission):
    if user.is_admin():
        return
    if not sub.overview or not user.agency or sub.overview.agency != user.agency:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this agency")


def _can_edit_submission(user: User, sub: SchemeSubmission) -> bool:
    if user.has_role("mto_admin"):
        return True
    status_val = sub.status
    if user.has_role("agency_creator") and status_val in (SubmissionStatus.draft.value, SubmissionStatus.rejected.value):
        return True
    if user.has_role("agency_approver") and status_val in (SubmissionStatus.pending_review.value, SubmissionStatus.rejected.value):
        return True
    return False


async def _get_submission(db: AsyncSession, scheme_id: str) -> SchemeSubmission:
    result = await db.execute(
        select(SchemeSubmission)
        .options(
            selectinload(SchemeSubmission.overview),
            selectinload(SchemeSubmission.mt_parameters),
            selectinload(SchemeSubmission.transactions),
            selectinload(SchemeSubmission.homes_functions),
            selectinload(SchemeSubmission.mt_bands),
            selectinload(SchemeSubmission.api_interfaces),
            selectinload(SchemeSubmission.creator),
            selectinload(SchemeSubmission.onboarding_slots),
        )
        .where(SchemeSubmission.id == scheme_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return sub


def _sub_to_dict(sub: SchemeSubmission) -> dict:
    ov = sub.overview
    slots = []
    if sub.onboarding_slots:
        for slot in sorted(sub.onboarding_slots, key=lambda x: (x.is_additional, x.slot_month)):
            slots.append({
                "id": slot.id,
                "year": slot.year,
                "slot_month": slot.slot_month,
                "slot_month_name": slot.slot_month_name,
                "is_additional": slot.is_additional,
                "technical_go_live": slot.technical_go_live.isoformat() if slot.technical_go_live else None,
                "business_go_live": slot.business_go_live.isoformat() if slot.business_go_live else None,
                "justification": slot.justification,
                "approval_status": slot.approval_status,
                "approver_comment": slot.approver_comment,
                "booked_at": slot.booked_at.isoformat() if slot.booked_at else None,
            })
    
    return {
        "id": sub.id,
        "agency": ov.agency if ov else None,
        "scheme_name": ov.scheme_name if ov else None,
        "scheme_code": ov.scheme_code if ov else None,
        "legislated_or_consent": ov.legislated_or_consent if ov else None,
        "consent_scope": ov.consent_scope if ov else None,
        "background_info": ov.background_info if ov else None,
        "status": sub.status,
        "version": sub.version,
        "created_by": sub.creator.display_name if sub.creator else None,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
        "updated_at": sub.updated_at.isoformat() if sub.updated_at else None,
        "overview": {
            "id": ov.id,
            "agency": ov.agency,
            "scheme_name": ov.scheme_name,
            "scheme_code": ov.scheme_code,
            "legislated_or_consent": ov.legislated_or_consent,
            "consent_scope": ov.consent_scope,
            "background_info": ov.background_info,
        } if ov else None,
        "onboarding_slots": slots,
        "mt_parameters": sub.mt_parameters.data if sub.mt_parameters else None,
        "transactions": sub.transactions.data if sub.transactions else None,
        "homes_functions": sub.homes_functions.data if sub.homes_functions else None,
        "mt_bands": sub.mt_bands.data if sub.mt_bands else None,
        "api_interfaces": sub.api_interfaces.data if sub.api_interfaces else None,
    }

# ── CRUD ─────────────────────────────────────────────────────────

@router.get("")
async def list_schemes(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    query = (
        select(SchemeSubmission)
        .options(selectinload(SchemeSubmission.overview), selectinload(SchemeSubmission.creator), selectinload(SchemeSubmission.onboarding_slots))
        .order_by(SchemeSubmission.created_at.desc())
    )
    # Agency-scoped: non-admin users only see their own agency's schemes
    if not user.is_admin() and user.agency:
        query = query.join(SchemeOverview, SchemeSubmission.scheme_overview_id == SchemeOverview.id).where(SchemeOverview.agency == user.agency)
    result = await db.execute(query)
    subs = result.scalars().all()
    return [
        {
            "id": s.id,
            "scheme_name": s.overview.scheme_name if s.overview else None,
            "scheme_code": s.overview.scheme_code if s.overview else None,
            "agency": s.overview.agency if s.overview else None,
            "status": s.status,
            "version": s.version,
            "created_by": s.creator.display_name if s.creator else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "primary_slot": next(
                ({"year": slot.year, "slot_month": slot.slot_month, "slot_month_name": slot.slot_month_name}
                 for slot in (s.onboarding_slots or []) if not slot.is_additional),
                None
            ),
        }
        for s in subs
    ]


@router.post("", status_code=201)
async def create_scheme(body: SchemeCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    _require_role(user, "agency_creator")
    if body.agency and body.agency != user.agency:
        raise HTTPException(status_code=403, detail="Creators can only create schemes for their own agency")
    overview = SchemeOverview(
        agency=body.agency or user.agency,
        scheme_name=body.scheme_name,
        scheme_code=body.scheme_code,
        legislated_or_consent=body.legislated_or_consent,
        consent_scope=body.consent_scope,
        background_info=body.background_info,
    )
    db.add(overview)
    await db.flush()

    submission = SchemeSubmission(
        scheme_overview_id=overview.id,
        status=SubmissionStatus.draft.value,
        created_by=user.id,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return {"id": submission.id, "scheme_name": overview.scheme_name, "status": submission.status}


@router.get("/{scheme_id}")
async def get_scheme(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    return _sub_to_dict(sub)


@router.put("/{scheme_id}")
async def update_scheme(scheme_id: str, body: SchemeUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    if not _can_edit_submission(user, sub):
        raise HTTPException(400, "You are not allowed to edit this scheme in its current status")

    ov = sub.overview
    changes = []
    for field in ("agency", "scheme_name", "scheme_code", "legislated_or_consent", "consent_scope", "background_info"):
        new_val = getattr(body, field, None)
        if new_val is not None:
            old_val = getattr(ov, field)
            if old_val != new_val:
                changes.append({"field": field, "old": str(old_val), "new": str(new_val)})
                setattr(ov, field, new_val)

    if changes:
        db.add(ChangeLog(submission_id=sub.id, changed_by=user.id, tab_name="overview", changes=changes))

    sub.updated_at = datetime.utcnow()
    await db.commit()
    return {"ok": True, "changes": len(changes)}


@router.put("/{scheme_id}/tab/{tab_name}")
async def update_tab(scheme_id: str, tab_name: str, body: TabUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if tab_name not in TAB_MODEL_MAP:
        raise HTTPException(400, f"Invalid tab: {tab_name}. Must be one of {list(TAB_MODEL_MAP.keys())}")

    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    if not _can_edit_submission(user, sub):
        raise HTTPException(400, "You are not allowed to edit this scheme in its current status")

    model_cls = TAB_MODEL_MAP[tab_name]
    rel_name = TAB_REL_MAP[tab_name]
    existing = getattr(sub, rel_name)

    old_data = existing.data if existing else None
    changes = [{"field": tab_name, "old": old_data, "new": body.data}]

    if existing:
        existing.data = body.data
    else:
        new_obj = model_cls(submission_id=sub.id, data=body.data)
        db.add(new_obj)

    db.add(ChangeLog(submission_id=sub.id, changed_by=user.id, tab_name=tab_name, changes=changes))
    sub.updated_at = datetime.utcnow()
    await db.commit()
    return {"ok": True, "tab": tab_name}


# ── Workflow ─────────────────────────────────────────────────────

@router.post("/{scheme_id}/submit")
async def submit_scheme(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    _require_role(user, "agency_creator")
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    if sub.status not in (SubmissionStatus.draft.value, SubmissionStatus.rejected.value):
        raise HTTPException(400, f"Cannot submit from status {sub.status}")
    sub.status = SubmissionStatus.pending_review.value
    sub.updated_at = datetime.utcnow()
    db.add(Comment(submission_id=sub.id, user_id=user.id, text="Submitted for agency review", stage="submitted"))
    await db.commit()
    return {"ok": True, "status": sub.status}


@router.post("/{scheme_id}/approve")
async def approve_scheme(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    _require_role(user, "agency_approver")
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    if sub.status not in (SubmissionStatus.pending_review.value, SubmissionStatus.rejected.value):
        raise HTTPException(400, f"Cannot approve/send from status {sub.status}")
    sub.status = SubmissionStatus.pending_final.value
    sub.updated_at = datetime.utcnow()
    db.add(Comment(submission_id=sub.id, user_id=user.id, text="Approved by agency approver and sent to MTO", stage="approved"))
    await db.commit()
    return {"ok": True, "status": sub.status}


@router.post("/{scheme_id}/final-approve")
async def final_approve_scheme(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    _require_role(user, "mto_admin")
    sub = await _get_submission(db, scheme_id)
    if sub.status != SubmissionStatus.pending_final.value:
        raise HTTPException(400, f"Cannot final-approve from status {sub.status}")
    sub.status = SubmissionStatus.approved.value
    sub.updated_at = datetime.utcnow()
    db.add(Comment(submission_id=sub.id, user_id=user.id, text="Final approval granted", stage="approved"))
    await db.commit()
    return {"ok": True, "status": sub.status}


@router.post("/{scheme_id}/reject")
async def reject_scheme(scheme_id: str, body: RejectBody = RejectBody(), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)

    if user.has_role("agency_approver"):
        if sub.status != SubmissionStatus.pending_review.value:
            raise HTTPException(400, f"Agency approver cannot reject from status {sub.status}")
    elif user.has_role("mto_admin"):
        if sub.status != SubmissionStatus.pending_final.value:
            raise HTTPException(400, f"MTO admin cannot reject from status {sub.status}")
    else:
        raise HTTPException(status_code=403, detail="Only agency approver or MTO admin can reject")

    sub.status = SubmissionStatus.rejected.value
    sub.updated_at = datetime.utcnow()
    comment_text = body.comment or "Rejected"
    db.add(Comment(submission_id=sub.id, user_id=user.id, text=comment_text, stage="rejected"))
    await db.commit()
    return {"ok": True, "status": sub.status}


# ── Comments & Changes ───────────────────────────────────────────

@router.get("/{scheme_id}/comments")
async def list_comments(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    result = await db.execute(
        select(Comment).where(Comment.submission_id == scheme_id).order_by(Comment.created_at.desc())
    )
    comments = result.scalars().all()
    out = []
    for c in comments:
        u = await db.get(User, c.user_id) if c.user_id else None
        out.append({
            "id": c.id, "text": c.text, "stage": c.stage,
            "user": u.display_name if u else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return out


@router.post("/{scheme_id}/comments", status_code=201)
async def add_comment(scheme_id: str, body: CommentCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    c = Comment(submission_id=scheme_id, user_id=user.id, text=body.text, stage=body.stage)
    db.add(c)
    await db.commit()
    return {"id": c.id, "text": c.text}


@router.get("/{scheme_id}/changes")
async def list_changes(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    result = await db.execute(
        select(ChangeLog).where(ChangeLog.submission_id == scheme_id).order_by(ChangeLog.timestamp.desc())
    )
    logs = result.scalars().all()
    out = []
    for log in logs:
        u = await db.get(User, log.changed_by) if log.changed_by else None
        out.append({
            "id": log.id, "tab_name": log.tab_name, "changes": log.changes,
            "changed_by": u.display_name if u else None,
            "changed_by_username": u.username if u else None,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        })
    return out


# ── Excel Export ─────────────────────────────────────────────────

@router.get("/{scheme_id}/export")
async def export_excel(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    wb = Workbook()

    # Tab 1: Overview
    ws = wb.active
    ws.title = "Scheme Overview"
    ov = sub.overview
    if ov:
        for i, (k, v) in enumerate([
            ("Agency", ov.agency), ("Scheme Name", ov.scheme_name), ("Scheme Code", ov.scheme_code),
            ("Legislated/Consent", ov.legislated_or_consent), ("Consent Scope", ov.consent_scope),
        ], 1):
            ws.cell(row=i, column=1, value=k)
            ws.cell(row=i, column=2, value=str(v) if v else "")
        if ov.background_info:
            row = 7
            for k, v in ov.background_info.items():
                ws.cell(row=row, column=1, value=k)
                ws.cell(row=row, column=2, value=str(v) if v else "")
                row += 1

    # Tabs 2-6: JSON data tabs
    tab_data = [
        ("MT Parameters", sub.mt_parameters),
        ("Transactions", sub.transactions),
        ("HOMES Functions", sub.homes_functions),
        ("MT Bands", sub.mt_bands),
        ("API Interfaces", sub.api_interfaces),
    ]
    for title, obj in tab_data:
        ws = wb.create_sheet(title)
        if obj and obj.data:
            _write_json_sheet(ws, obj.data)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"scheme_{sub.overview.scheme_name if sub.overview else scheme_id}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _write_json_sheet(ws, data: dict, start_row: int = 1):
    """Flatten a dict/list into worksheet rows."""
    row = start_row
    if isinstance(data, dict):
        for k, v in data.items():
            ws.cell(row=row, column=1, value=str(k))
            if isinstance(v, (dict, list)):
                ws.cell(row=row, column=2, value=str(v))
            else:
                ws.cell(row=row, column=2, value=str(v) if v is not None else "")
            row += 1
    elif isinstance(data, list):
        for i, item in enumerate(data):
            ws.cell(row=row, column=1, value=f"Item {i+1}")
            ws.cell(row=row, column=2, value=str(item))
            row += 1


@router.delete("/{scheme_id}", status_code=200)
async def delete_scheme(scheme_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    _require_role(user, "mto_admin")
    sub = await _get_submission(db, scheme_id)
    overview = sub.overview

    await db.delete(sub)
    if overview:
        await db.delete(overview)
    await db.commit()
    return {"ok": True, "deleted_scheme_id": scheme_id}


# ── ONBOARDING SLOT APPROVAL ────────────────────────────────────

class SlotApprovalBody(BaseModel):
    approval_status: str  # "approved" or "rejected"
    approver_comment: str | None = None


@router.post("/{scheme_id}/slot/approve")
async def approve_slot(
    scheme_id: str,
    body: SlotApprovalBody,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Approve or reject the onboarding slot for a scheme submission.
    
    Approvers can approve, or reject with a comment (e.g., "Please pick July instead").
    """
    _require_role(user, "agency_approver", "mto_admin")
    
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)

    if user.has_role("agency_approver") and sub.status != SubmissionStatus.pending_review.value:
        raise HTTPException(status_code=400, detail="Agency approver can only review slot at pending_review stage")
    if user.has_role("mto_admin") and sub.status != SubmissionStatus.pending_final.value:
        raise HTTPException(status_code=400, detail="MTO admin can only review slot at pending_final stage")
    
    # Get primary slot
    primary_slot = next((s for s in (sub.onboarding_slots or []) if not s.is_additional), None)
    if not primary_slot:
        raise HTTPException(status_code=404, detail="No onboarding slot found for this submission")
    
    if body.approval_status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")
    
    primary_slot.approval_status = body.approval_status
    primary_slot.approver_comment = body.approver_comment
    sub.updated_at = datetime.utcnow()
    
    await db.commit()
    return {"message": f"Slot {body.approval_status}"}

# ── ONBOARDING SLOT MANAGEMENT ──────────────────────────────────

from datetime import date

def _get_month_name(month: int) -> str:
    """Convert month number to name."""
    names = {1: "January", 4: "April", 7: "July", 11: "November"}
    return names.get(month, "Unknown")


@router.put("/{scheme_id}/slot", status_code=200)
async def set_scheme_slot(
    scheme_id: str,
    body: SlotSelection,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Set or update the primary onboarding slot for a scheme submission.
    
    Only allowed for draft or rejected submissions.
    Validates:
    - Cannot select past quarters
    - Go-live dates must not be before the slot month
    - If scheme already has a slot, updates it (unless approved)
    """
    _require_role(user, "agency_creator", "agency_approver", "mto_admin")
    
    # Get submission with all slots
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    
    # Check submission is in editable state
    if not _can_edit_submission(user, sub):
        raise HTTPException(status_code=400, detail="Cannot edit slot in current workflow stage")
    
    # Check slot month is valid (only Jan, Apr, Jul, Nov)
    if body.slot_month not in [1, 4, 7, 11]:
        raise HTTPException(status_code=400, detail="Invalid slot month. Must be January(1), April(4), July(7), or November(11)")
    
    # Parse dates
    try:
        tech_date = date.fromisoformat(body.technical_go_live)
        biz_date = date.fromisoformat(body.business_go_live)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Prevent backdating: cannot select a slot in a past quarter
    today = date.today()
    slot_quarter_start = date(body.year, body.slot_month, 1)
    if slot_quarter_start < today.replace(day=1):
        raise HTTPException(status_code=400, detail=f"Cannot select a slot in the past (slot month: {_get_month_name(body.slot_month)} {body.year})")
    
    # Go-live dates cannot be before the selected slot month
    slot_month_date = date(body.year, body.slot_month, 1)
    if tech_date < slot_month_date or biz_date < slot_month_date:
        raise HTTPException(status_code=400, detail=f"Go-live dates cannot be before {_get_month_name(body.slot_month)} {body.year}")
    
    # Find or create primary slot
    primary_slot = next((s for s in (sub.onboarding_slots or []) if not s.is_additional), None)
    
    if primary_slot:
        # Update existing primary slot
        primary_slot.year = body.year
        primary_slot.slot_month = body.slot_month
        primary_slot.slot_month_name = _get_month_name(body.slot_month)
        primary_slot.technical_go_live = tech_date
        primary_slot.business_go_live = biz_date
        primary_slot.approval_status = "pending"  # Reset to pending when changed
        primary_slot.approver_comment = None
    else:
        # Create new primary slot
        primary_slot = OnboardingSlot(
            scheme_submission_id=scheme_id,
            year=body.year,
            slot_month=body.slot_month,
            slot_month_name=_get_month_name(body.slot_month),
            is_additional=False,
            technical_go_live=tech_date,
            business_go_live=biz_date,
            booked_by_id=user.id,
            approval_status="pending",
        )
        db.add(primary_slot)
    
    sub.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Slot updated successfully"}


@router.get("/{scheme_id}/slot")
async def get_scheme_slot(
    scheme_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get the onboarding slot(s) for a scheme submission."""
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    
    slots = []
    if sub.onboarding_slots:
        for slot in sorted(sub.onboarding_slots, key=lambda x: (x.is_additional, x.slot_month)):
            slots.append({
                "id": slot.id,
                "year": slot.year,
                "slot_month": slot.slot_month,
                "slot_month_name": slot.slot_month_name,
                "is_additional": slot.is_additional,
                "technical_go_live": slot.technical_go_live.isoformat() if slot.technical_go_live else None,
                "business_go_live": slot.business_go_live.isoformat() if slot.business_go_live else None,
                "justification": slot.justification,
                "approval_status": slot.approval_status,
                "approver_comment": slot.approver_comment,
            })
    
    return {"slots": slots}


@router.delete("/{scheme_id}/slot/{slot_id}", status_code=200)
async def delete_additional_slot(
    scheme_id: str,
    slot_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Remove a slot from a submission.

    - agency_creator/agency_approver: can remove additional slots only
    - mto_admin: can remove any slot (including primary)
    """
    _require_role(user, "agency_creator", "agency_approver", "mto_admin")
    
    sub = await _get_submission(db, scheme_id)
    _assert_agency_access(user, sub)
    
    if not _can_edit_submission(user, sub):
        raise HTTPException(status_code=400, detail="Cannot delete slot in current workflow stage")
    
    slot = next((s for s in (sub.onboarding_slots or []) if s.id == slot_id), None)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if not slot.is_additional and not user.has_role("mto_admin"):
        raise HTTPException(status_code=400, detail="Cannot delete primary slot. Use PUT to update it.")
    
    await db.delete(slot)
    sub.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Slot deleted successfully"}
