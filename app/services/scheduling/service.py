from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import OnboardingSlot, SchemeOverview, SchemeSubmission, User


class SchedulingService:
    async def get_scheduling_overview(self, db: AsyncSession, user: User, year: int):
        query = (
            select(OnboardingSlot)
            .join(SchemeSubmission, OnboardingSlot.scheme_submission_id == SchemeSubmission.id)
            .join(SchemeOverview, SchemeSubmission.scheme_overview_id == SchemeOverview.id)
            .options(
                selectinload(OnboardingSlot.submission).selectinload(SchemeSubmission.overview),
                selectinload(OnboardingSlot.booked_by),
            )
            .where(
                OnboardingSlot.year == year,
                OnboardingSlot.approval_status == "approved",
            )
            .order_by(OnboardingSlot.slot_month)
        )

        if not user.is_admin():
            if not user.agency:
                raise HTTPException(status_code=403, detail="Agency is required")
            query = query.where(SchemeOverview.agency == user.agency)

        result = await db.execute(query)
        slots = result.scalars().all()

        month_names = {1: "January", 4: "April", 7: "July", 11: "November"}
        slots_by_month = {month: [] for month in [1, 4, 7, 11]}

        for slot in slots:
            if slot.slot_month in slots_by_month:
                slots_by_month[slot.slot_month].append(
                    {
                        "id": slot.id,
                        "submission_id": slot.submission.id if slot.submission else None,
                        "scheme_name": slot.submission.overview.scheme_name if slot.submission and slot.submission.overview else None,
                        "agency": slot.submission.overview.agency if slot.submission and slot.submission.overview else None,
                        "booked_by": slot.booked_by.display_name if slot.booked_by else None,
                        "technical_go_live": slot.technical_go_live.isoformat() if slot.technical_go_live else None,
                        "business_go_live": slot.business_go_live.isoformat() if slot.business_go_live else None,
                    }
                )

        return {
            "year": year,
            "quarters": [
                {
                    "month": month,
                    "month_name": month_names.get(month),
                    "bookings": slots_by_month.get(month, []),
                }
                for month in [1, 4, 7, 11]
            ],
        }

    async def get_my_bookings(self, db: AsyncSession, user: User):
        query = (
            select(SchemeSubmission)
            .join(SchemeOverview, SchemeSubmission.scheme_overview_id == SchemeOverview.id)
            .options(
                selectinload(SchemeSubmission.overview),
                selectinload(SchemeSubmission.onboarding_slots),
            )
            .where(True if user.is_admin() else (SchemeOverview.agency == user.agency))
            .order_by(SchemeSubmission.created_at.desc())
        )

        result = await db.execute(query)
        subs = result.scalars().all()

        bookings = []
        for sub in subs:
            for slot in (sub.onboarding_slots or []):
                bookings.append(
                    {
                        "slot_id": slot.id,
                        "submission_id": sub.id,
                        "scheme_name": sub.overview.scheme_name if sub.overview else None,
                        "year": slot.year,
                        "slot_month": slot.slot_month,
                        "slot_month_name": slot.slot_month_name,
                        "is_additional": slot.is_additional,
                        "technical_go_live": slot.technical_go_live.isoformat() if slot.technical_go_live else None,
                        "business_go_live": slot.business_go_live.isoformat() if slot.business_go_live else None,
                        "approval_status": slot.approval_status,
                        "approver_comment": slot.approver_comment,
                    }
                )

        return {
            "agency": user.agency,
            "total_bookings": len(bookings),
            "bookings": sorted(bookings, key=lambda x: (x["year"], x["slot_month"])),
        }
