from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config import get_db
from app.auth import get_current_user
from app.models import User, FieldGuidance

router = APIRouter(prefix="/api/guidance", tags=["guidance"])


class GuidanceUpdate(BaseModel):
    inline_hint: str | None = None
    popover_title: str | None = None
    popover_description: str | None = None
    popover_examples: list | None = None
    popover_do: list | None = None
    popover_dont: list | None = None


@router.get("")
async def list_guidance(
    tab: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all field guidance, optionally filtered by tab."""
    query = select(FieldGuidance)
    if tab:
        query = query.where(FieldGuidance.tab_name == tab)
    
    result = await db.execute(query.order_by(FieldGuidance.tab_name, FieldGuidance.field_name))
    guides = result.scalars().all()
    
    return [
        {
            "id": g.id,
            "tab_name": g.tab_name,
            "field_name": g.field_name,
            "inline_hint": g.inline_hint or "",
            "popover_title": g.popover_title or "",
            "popover_description": g.popover_description or "",
            "popover_examples": g.popover_examples or [],
            "popover_do": g.popover_do or [],
            "popover_dont": g.popover_dont or [],
        }
        for g in guides
    ]


@router.get("/{tab}/{field}")
async def get_guidance(
    tab: str,
    field: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get guidance for a specific tab/field."""
    result = await db.execute(
        select(FieldGuidance).where(
            FieldGuidance.tab_name == tab,
            FieldGuidance.field_name == field,
        )
    )
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=404, detail="Guidance not found")
    
    return {
        "id": guide.id,
        "tab_name": guide.tab_name,
        "field_name": guide.field_name,
        "inline_hint": guide.inline_hint or "",
        "popover_title": guide.popover_title or "",
        "popover_description": guide.popover_description or "",
        "popover_examples": guide.popover_examples or [],
        "popover_do": guide.popover_do or [],
        "popover_dont": guide.popover_dont or [],
    }


@router.put("/{tab}/{field}")
async def update_guidance(
    tab: str,
    field: str,
    body: GuidanceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update guidance for a specific tab/field. MTO admin only."""
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Only MTO Admin can edit field guidance")
    
    result = await db.execute(
        select(FieldGuidance).where(
            FieldGuidance.tab_name == tab,
            FieldGuidance.field_name == field,
        )
    )
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=404, detail="Guidance not found")
    
    # Update fields
    if body.inline_hint is not None:
        guide.inline_hint = body.inline_hint
    if body.popover_title is not None:
        guide.popover_title = body.popover_title
    if body.popover_description is not None:
        guide.popover_description = body.popover_description
    if body.popover_examples is not None:
        guide.popover_examples = body.popover_examples
    if body.popover_do is not None:
        guide.popover_do = body.popover_do
    if body.popover_dont is not None:
        guide.popover_dont = body.popover_dont
    
    await db.commit()
    return {"ok": True, "updated": f"{tab}.{field}"}
