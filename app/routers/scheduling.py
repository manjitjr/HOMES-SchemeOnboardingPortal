"""Scheduling overview router for onboarding slot calendar view."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_db
from app.auth import get_current_user
from app.models import User
from app.services.scheduling.service import SchedulingService

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])
service = SchedulingService()


@router.get("/overview/{year}")
async def get_scheduling_overview(
    year: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get calendar view of all onboarding slots for a given year.
    
    Returns slots grouped by quarter (Jan, Apr, Jul, Nov), showing which schemes are booked.
    MTO admins see all agencies; others are agency-scoped.
    """
    return await service.get_scheduling_overview(db, user, year)


@router.get("/my-bookings")
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all onboarding slots booked by the current user's scheme submissions.
    
    Returns slots in all statuses (pending, approved, rejected).
    """
    return await service.get_my_bookings(db, user)
