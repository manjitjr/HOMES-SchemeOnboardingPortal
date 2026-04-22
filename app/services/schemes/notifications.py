from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import NotificationLog, SchemeOverview, SchemeSubmission, SubmissionStatus, User
from app.services.notifications import send_email_notification


class NotificationOrchestrationService:
    """Handles workflow notification dispatch and notification-log retrieval."""

    async def list_logs(self, db: AsyncSession, limit: int):
        safe_limit = max(1, min(limit, 1000))
        result = await db.execute(
            select(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(safe_limit)
        )
        logs = result.scalars().all()

        out = []
        for log in logs:
            sub = await db.get(SchemeSubmission, log.submission_id) if log.submission_id else None
            ov = await db.get(SchemeOverview, sub.scheme_overview_id) if sub and sub.scheme_overview_id else None
            actor = await db.get(User, log.triggered_by) if log.triggered_by else None
            out.append(
                {
                    "id": log.id,
                    "submission_id": log.submission_id,
                    "scheme_name": ov.scheme_name if ov else None,
                    "agency": ov.agency if ov else None,
                    "stage": log.stage,
                    "subject": log.subject,
                    "recipients": log.recipients or [],
                    "delivery_status": log.delivery_status,
                    "detail": log.detail,
                    "triggered_by": actor.display_name if actor else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
            )
        return out

    async def _approval_recipients(self, db: AsyncSession, role: str, agency: str | None = None) -> list[str]:
        result = await db.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()
        recipients: list[str] = []
        for u in users:
            if not u.has_role(role):
                continue
            if role == "agency_approver" and agency and u.agency != agency:
                continue
            if u.email:
                recipients.append(u.email)
        return recipients

    def _build_review_email(self, sub: SchemeSubmission, stage: str) -> tuple[str, str, str]:
        scheme_name = (sub.overview.scheme_name if sub.overview else "Unnamed Scheme")
        agency = (sub.overview.agency if sub.overview else "-")
        scheme_code = (sub.overview.scheme_code if sub.overview else "-")
        detail_url = f"{settings.app_base_url}/"

        if stage == SubmissionStatus.pending_review.value:
            subject = f"[HOMES] Scheme Pending Review: {scheme_name}"
            action = "A scheme has been submitted and is now pending agency review."
        else:
            subject = f"[HOMES] Scheme Pending Final Approval: {scheme_name}"
            action = "A scheme has been approved by agency approver and is now pending final MTO approval."

        text = (
            f"{action}\n\n"
            f"Scheme: {scheme_name}\n"
            f"Scheme Code: {scheme_code}\n"
            f"Agency: {agency}\n"
            f"Submission ID: {sub.id}\n\n"
            f"Open in portal: {detail_url}\n"
        )

        html = (
            f"<p>{action}</p>"
            f"<ul>"
            f"<li><strong>Scheme:</strong> {scheme_name}</li>"
            f"<li><strong>Scheme Code:</strong> {scheme_code}</li>"
            f"<li><strong>Agency:</strong> {agency}</li>"
            f"<li><strong>Submission ID:</strong> {sub.id}</li>"
            f"</ul>"
            f"<p><a href=\"{detail_url}\">Open in HOMES Portal</a></p>"
        )
        return subject, text, html

    async def notify_for_workflow_stage(
        self,
        db: AsyncSession,
        sub: SchemeSubmission,
        stage: str,
        triggered_by: str | None = None,
    ):
        if stage == SubmissionStatus.pending_review.value:
            recipients = await self._approval_recipients(
                db,
                "agency_approver",
                agency=(sub.overview.agency if sub.overview else None),
            )
        elif stage == SubmissionStatus.pending_final.value:
            recipients = await self._approval_recipients(db, "mto_admin")
        else:
            return

        subject, text, html = self._build_review_email(sub, stage)
        result = send_email_notification(recipients, subject, text, html)
        db.add(
            NotificationLog(
                submission_id=sub.id,
                stage=stage,
                subject=subject,
                recipients=result.get("recipients") or recipients,
                delivery_status=result.get("status") or "skipped",
                detail=result.get("detail"),
                triggered_by=triggered_by,
            )
        )
        await db.commit()
