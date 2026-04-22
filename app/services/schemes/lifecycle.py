from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    APIBatchInterfaces,
    Comment,
    HOMESFunctions,
    MTBands,
    SchemeMTParameters,
    SchemeOverview,
    SchemeSubmission,
    SubmissionStatus,
    TransactionDetails,
    sg_now,
)


class SchemeLifecycleService:
    """Encapsulates scheme version lifecycle and workflow transitions."""

    async def list_versions(self, db: AsyncSession, scheme_master_id: str, effective_status_fn):
        res = await db.execute(
            select(SchemeSubmission)
            .options(selectinload(SchemeSubmission.master), selectinload(SchemeSubmission.overview))
            .where(SchemeSubmission.scheme_master_id == scheme_master_id)
            .order_by(SchemeSubmission.version.asc())
        )
        versions = res.scalars().all()
        return [
            {
                "id": v.id,
                "version": v.version,
                "version_label": f"v{v.version}",
                "status": effective_status_fn(v),
                "valid_from": v.valid_from.isoformat() if v.valid_from else None,
                "valid_to": v.valid_to.isoformat() if v.valid_to else None,
            }
            for v in versions
        ]

    async def clone_version(
        self,
        db: AsyncSession,
        source: SchemeSubmission,
        user,
        valid_from: date | None,
        valid_to: date | None,
        next_version: int,
    ):
        src_ov = source.overview
        overview = SchemeOverview(
            agency=src_ov.agency if src_ov else (source.master.agency if source.master else user.agency),
            scheme_name=src_ov.scheme_name if src_ov else (source.master.scheme_name if source.master else ""),
            scheme_code=src_ov.scheme_code if src_ov else (source.master.scheme_code if source.master else None),
            legislated_or_consent=src_ov.legislated_or_consent if src_ov else None,
            consent_scope=src_ov.consent_scope if src_ov else None,
            background_info=(dict(src_ov.background_info) if src_ov and src_ov.background_info else None),
        )
        db.add(overview)
        await db.flush()

        clone = SchemeSubmission(
            scheme_master_id=source.scheme_master_id,
            scheme_overview_id=overview.id,
            status=SubmissionStatus.draft.value,
            version=next_version,
            valid_from=valid_from,
            valid_to=valid_to,
            cloned_from_submission_id=source.id,
            created_by=user.id,
        )
        db.add(clone)
        await db.flush()

        def clone_tab(existing_obj, model_cls):
            if not existing_obj:
                return
            copied = dict(existing_obj.data) if existing_obj.data else {}
            db.add(model_cls(submission_id=clone.id, data=copied))

        clone_tab(source.mt_parameters, SchemeMTParameters)
        clone_tab(source.transactions, TransactionDetails)
        clone_tab(source.homes_functions, HOMESFunctions)
        clone_tab(source.mt_bands, MTBands)
        clone_tab(source.api_interfaces, APIBatchInterfaces)

        db.add(Comment(submission_id=clone.id, user_id=user.id, text=f"Cloned from v{source.version}", stage="cloned"))
        await db.commit()
        return clone

    async def activate_version(self, db: AsyncSession, sub: SchemeSubmission, user, effective_status_fn):
        res = await db.execute(select(SchemeSubmission).where(SchemeSubmission.scheme_master_id == sub.scheme_master_id))
        versions = res.scalars().all()
        for v in versions:
            if v.id == sub.id:
                continue
            if effective_status_fn(v) == SubmissionStatus.active.value:
                v.status = SubmissionStatus.expired.value

        sub.status = SubmissionStatus.active.value
        sub.updated_at = sg_now()
        db.add(Comment(submission_id=sub.id, user_id=user.id, text="Version activated", stage="active"))
        await db.commit()
        return {"ok": True, "status": sub.status}

    async def retire_version(self, db: AsyncSession, sub: SchemeSubmission, user, retire_date: date, comment: str | None):
        sub.valid_to = retire_date
        sub.status = SubmissionStatus.retired.value
        sub.updated_at = sg_now()
        db.add(Comment(submission_id=sub.id, user_id=user.id, text=(comment or "Version retired by MTO"), stage="retired"))
        await db.commit()
        return {
            "ok": True,
            "status": sub.status,
            "valid_to": sub.valid_to.isoformat() if sub.valid_to else None,
        }

    async def submit_for_review(self, db: AsyncSession, sub: SchemeSubmission, user):
        sub.status = SubmissionStatus.pending_review.value
        sub.updated_at = sg_now()
        db.add(Comment(submission_id=sub.id, user_id=user.id, text="Submitted for agency review", stage="submitted"))
        await db.commit()
        return {"ok": True, "status": sub.status}

    async def approve_to_final(self, db: AsyncSession, sub: SchemeSubmission, user):
        sub.status = SubmissionStatus.pending_final.value
        sub.updated_at = sg_now()
        db.add(Comment(submission_id=sub.id, user_id=user.id, text="Approved by agency approver and sent to MTO", stage="approved"))
        await db.commit()
        return {"ok": True, "status": sub.status}

    async def final_approve(self, db: AsyncSession, sub: SchemeSubmission, user):
        sub.status = SubmissionStatus.approved.value
        sub.updated_at = sg_now()
        db.add(Comment(submission_id=sub.id, user_id=user.id, text="Final approval granted", stage="approved"))
        await db.commit()
        return {"ok": True, "status": sub.status}

    async def reject(self, db: AsyncSession, sub: SchemeSubmission, user, comment: str | None):
        sub.status = SubmissionStatus.rejected.value
        sub.updated_at = sg_now()
        comment_text = comment or "Rejected"
        db.add(Comment(submission_id=sub.id, user_id=user.id, text=comment_text, stage="rejected"))
        await db.commit()
        return {"ok": True, "status": sub.status}
