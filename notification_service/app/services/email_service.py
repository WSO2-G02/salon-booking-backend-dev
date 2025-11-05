import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)

def send_email(recipient: str, subject: str, html_body: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_email
        msg["To"] = recipient
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.smtp_email, settings.smtp_app_password)
            server.send_message(msg)
            print(msg)

        logger.info(f"Email sent successfully to {recipient}")
        print(f"Email sent successfully to {recipient}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        print(f"Failed to send email to {recipient}: {e}")
        return False
