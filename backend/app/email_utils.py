"""Email sending.

When EMAIL_ENABLED is False (default) emails print to the server console, so you can
develop the credential/alert flows without SMTP.

For real delivery with GMAIL you MUST use an App Password, not your normal Google password:
  1. Enable 2-Step Verification on the Google account.
  2. Go to https://myaccount.google.com/apppasswords and create an app password for "Mail".
  3. In backend/.env set:
       EMAIL_ENABLED=True
       SMTP_HOST=smtp.gmail.com
       SMTP_PORT=587
       SMTP_USER=youraddress@gmail.com
       SMTP_PASSWORD=the16charapppassword   (no spaces)
       EMAIL_FROM=youraddress@gmail.com      (must match SMTP_USER for Gmail)
Port 465 uses SSL instead of STARTTLS - the code handles both automatically.
"""
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import settings

logger = logging.getLogger("hire.email")


def send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.EMAIL_ENABLED:
        print("\n" + "=" * 70)
        print(f"[EMAIL - console mode]  To: {to_email}")
        print(f"Subject: {subject}")
        print("-" * 70)
        print(body)
        print("=" * 70 + "\n")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        if settings.SMTP_PORT == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context, timeout=20) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        logger.info("Email sent to %s (subject=%s)", to_email, subject)
    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP auth failed: %s", e)
        raise RuntimeError(
            "SMTP authentication failed. For Gmail, use a 16-character App Password "
            "(not your normal password) and make sure 2-Step Verification is on."
        ) from e
    except Exception as e:
        logger.error("Email send failed: %s", e)
        raise RuntimeError(f"Email could not be sent: {e}") from e


def send_credentials_email(to_email: str, name: str, user_id: str, password: str) -> None:
    subject = f"Your {settings.APP_NAME} login credentials"
    body = (
        f"Dear {name},\n\n"
        f"An account has been created for you on {settings.APP_NAME}.\n\n"
        f"  User ID  : {user_id}\n"
        f"  Password : {password}\n\n"
        f"These credentials work on both the web and mobile apps.\n"
        f"Please log in and change your password.\n\n"
        f"Login here: {settings.FRONTEND_URL}\n\n"
        f"Regards,\n{settings.APP_NAME} Team"
    )
    send_email(to_email, subject, body)


def send_application_email(recruiter_email: str, candidate_name: str, position: str,
                           job_code: str, location: str, education: str,
                           experience: str, key_skills: str) -> None:
    subject = f'{candidate_name} - Application for the position of "{position}", Job Code: {job_code}'
    body = (
        f"A new application has been received.\n\n"
        f"  Candidate name : {candidate_name}\n"
        f"  Position       : {position}\n"
        f"  Location       : {location}\n"
        f"  Education      : {education}\n"
        f"  Experience     : {experience}\n"
        f"  Key Skills     : {key_skills}\n\n"
        f"Log in to {settings.APP_NAME} to view the full resume.\n"
    )
    send_email(recruiter_email, subject, body)
