import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(settings.SMTP_USER and settings.SMTP_PASSWORD and settings.SMTP_SERVER and settings.SMTP_PORT)


def send_email(to_email: str, subject: str, body_text: str, from_name: Optional[str] = None) -> bool:
    """Send a plain-text email using SMTP settings. Returns True on success, False otherwise.
    Falls back to console log if SMTP isn't configured.
    """
    if not _smtp_configured():
        logger.warning("SMTP not configured. Would have sent email to %s with subject '%s'. Body: %s", to_email, subject, body_text)
        return False

    from_email = settings.SMTP_USER
    display_from = f"{from_name} <{from_email}>" if from_name else from_email

    msg = MIMEMultipart()
    msg["From"] = display_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.ehlo()
            if settings.SMTP_PORT in (465,):
                server.starttls(context=context)
            elif settings.SMTP_PORT == 587:
                server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_email, [to_email], msg.as_string())
        logger.info("Email sent to %s with subject '%s'", to_email, subject)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, e)
        return False


def send_otp_email(to_email: str, otp: str, purpose: str = "Login") -> bool:
    """Send a simple OTP email for the given purpose (Login/Signup/Password Reset)."""
    subject = f"Your {purpose} OTP"
    body = (
        f"Hello,\n\n"
        f"Your one-time password (OTP) for {purpose.lower()} is: {otp}\n\n"
        f"This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
        f"If you did not request this, you can ignore this email.\n\n"
        f"Thanks,\nFoodHub"
    )
    return send_email(to_email, subject, body, from_name="FoodHub")
