from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FieldGuidance, User


class FieldGuidanceService:
    async def list_guidance(self, db: AsyncSession, tab: str | None = None):
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

    async def get_guidance(self, db: AsyncSession, tab: str, field: str):
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

    async def update_guidance(self, db: AsyncSession, user: User, tab: str, field: str, payload: dict):
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

        for key in [
            "inline_hint",
            "popover_title",
            "popover_description",
            "popover_examples",
            "popover_do",
            "popover_dont",
        ]:
            if key in payload and payload[key] is not None:
                setattr(guide, key, payload[key])

        await db.commit()
        return {"ok": True, "updated": f"{tab}.{field}"}
