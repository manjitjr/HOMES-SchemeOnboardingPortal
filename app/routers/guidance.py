from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config import get_db
from app.auth import get_current_user
from app.models import User
from app.services.guidance.service import FieldGuidanceService

router = APIRouter(prefix="/api/guidance", tags=["guidance"])
service = FieldGuidanceService()


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
    return await service.list_guidance(db, tab)


@router.get("/{tab}/{field}")
async def get_guidance(
    tab: str,
    field: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get guidance for a specific tab/field."""
    return await service.get_guidance(db, tab, field)


@router.put("/{tab}/{field}")
async def update_guidance(
    tab: str,
    field: str,
    body: GuidanceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update guidance for a specific tab/field. MTO admin only."""
    return await service.update_guidance(
        db,
        user,
        tab,
        field,
        {
            "inline_hint": body.inline_hint,
            "popover_title": body.popover_title,
            "popover_description": body.popover_description,
            "popover_examples": body.popover_examples,
            "popover_do": body.popover_do,
            "popover_dont": body.popover_dont,
        },
    )
