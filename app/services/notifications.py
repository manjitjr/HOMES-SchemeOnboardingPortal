import smtplib
from email.message import EmailMessage

from app.config import settings


def send_email_notification(recipients: list[str], subject: str, text_body: str, html_body: str | None = None) -> dict:
    clean_recipients = sorted({(r or "").strip() for r in recipients if (r or "").strip()})
    if not clean_recipients:
        return {"status": "skipped", "detail": "No recipients", "recipients": []}

    # Safe fallback for local/dev use when SMTP is not configured.
    if not settings.smtp_host:
        print(
            f"Notification skipped (SMTP not configured). Subject='{subject}', Recipients={clean_recipients}"
        )
        return {"status": "skipped", "detail": "SMTP not configured", "recipients": clean_recipients}

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_sender
    msg["To"] = ", ".join(clean_recipients)
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password or "")
            smtp.send_message(msg)
        return {"status": "sent", "detail": "Delivered", "recipients": clean_recipients}
    except Exception as exc:
        print(f"Notification email failed: {exc}")
        return {"status": "failed", "detail": str(exc), "recipients": clean_recipients}
