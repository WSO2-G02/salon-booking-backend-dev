"""
Notification Service Business Logic Layer
Handles all email sending operations via Gmail SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime
import logging

from app.config import get_settings
from app.templates import (
    get_register_user_template,
    get_reset_password_template,
    get_create_staff_template,
    get_create_appointment_template,
    get_update_appointment_template,
    get_cancel_appointment_template
)

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Service class for sending emails via Gmail SMTP"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_name = settings.SMTP_FROM_NAME
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send an email via Gmail SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.smtp_user}>"
            message["To"] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Connect to Gmail SMTP and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            raise ValueError("Email authentication failed. Check SMTP credentials.")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise ValueError(f"Failed to send email: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise ValueError(f"Failed to send email: {str(e)}")
    
    # ========================================================================
    # Email Sending Methods
    # ========================================================================
    
    def send_register_user_email(
        self,
        email: str,
        full_name: str,
        username: str
    ) -> Dict:
        """
        Send welcome email to newly registered user
        
        Args:
            email: User's email address
            full_name: User's full name
            username: User's username
        
        Returns:
            Result dictionary
        """
        subject = "🎉 Welcome to Salon Booking System!"
        html_content = get_register_user_template(full_name, username)
        
        self._send_email(email, subject, html_content)
        
        return {
            "status": "success",
            "message": "Registration welcome email sent successfully",
            "email_sent_to": email,
            "email_type": "register_user"
        }
    
    def send_reset_password_email(
        self,
        email: str,
        full_name: str,
        reset_token: str,
        expiry_minutes: int = 30
    ) -> Dict:
        """
        Send password reset email
        
        Args:
            email: User's email address
            full_name: User's full name
            reset_token: Password reset token/link
            expiry_minutes: Token expiry time
        
        Returns:
            Result dictionary
        """
        subject = "🔐 Password Reset Request - Salon Booking"
        html_content = get_reset_password_template(full_name, reset_token, expiry_minutes)
        
        self._send_email(email, subject, html_content)
        
        return {
            "status": "success",
            "message": "Password reset email sent successfully",
            "email_sent_to": email,
            "email_type": "reset_password"
        }
    
    def send_create_staff_email(
        self,
        email: str,
        full_name: str,
        position: str,
        username: str,
        temporary_password: Optional[str] = None
    ) -> Dict:
        """
        Send welcome email to new staff member
        
        Args:
            email: Staff's email address
            full_name: Staff's full name
            position: Staff's position
            username: Staff's username
            temporary_password: Temporary password if generated
        
        Returns:
            Result dictionary
        """
        subject = "🎉 Welcome to Our Team - Salon Booking Staff"
        html_content = get_create_staff_template(full_name, position, username, temporary_password)
        
        self._send_email(email, subject, html_content)
        
        return {
            "status": "success",
            "message": "Staff welcome email sent successfully",
            "email_sent_to": email,
            "email_type": "create_staff"
        }
    
    def send_create_appointment_email(
        self,
        email: str,
        customer_name: str,
        service_name: str,
        staff_name: str,
        appointment_datetime: datetime,
        duration_minutes: int,
        price: float,
        appointment_id: int
    ) -> Dict:
        """
        Send appointment confirmation email
        
        Args:
            email: Customer's email address
            customer_name: Customer's name
            service_name: Service name
            staff_name: Staff name
            appointment_datetime: Appointment datetime
            duration_minutes: Service duration
            price: Service price
            appointment_id: Appointment ID
        
        Returns:
            Result dictionary
        """
        subject = f"✅ Appointment Confirmed - #{appointment_id}"
        
        # Format datetime for display
        formatted_datetime = appointment_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        
        html_content = get_create_appointment_template(
            customer_name,
            service_name,
            staff_name,
            formatted_datetime,
            duration_minutes,
            price,
            appointment_id
        )
        
        self._send_email(email, subject, html_content)
        
        return {
            "status": "success",
            "message": "Appointment confirmation email sent successfully",
            "email_sent_to": email,
            "email_type": "create_appointment"
        }
    
    def send_update_appointment_email(
        self,
        email: str,
        customer_name: str,
        service_name: str,
        staff_name: str,
        old_datetime: datetime,
        new_datetime: datetime,
        appointment_id: int,
        change_reason: Optional[str] = None
    ) -> Dict:
        """
        Send appointment update notification email
        
        Args:
            email: Customer's email address
            customer_name: Customer's name
            service_name: Service name
            staff_name: Staff name
            old_datetime: Previous appointment datetime
            new_datetime: New appointment datetime
            appointment_id: Appointment ID
            change_reason: Reason for the change
        
        Returns:
            Result dictionary
        """
        subject = f"🔄 Appointment Updated - #{appointment_id}"
        
        # Format datetimes for display
        old_formatted = old_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        new_formatted = new_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        
        html_content = get_update_appointment_template(
            customer_name,
            service_name,
            staff_name,
            old_formatted,
            new_formatted,
            appointment_id,
            change_reason
        )
        
        self._send_email(email, subject, html_content)
        
        return {
            "status": "success",
            "message": "Appointment update email sent successfully",
            "email_sent_to": email,
            "email_type": "update_appointment"
        }
    
    def send_cancel_appointment_email(
        self,
        email: str,
        customer_name: str,
        service_name: str,
        staff_name: str,
        appointment_datetime: datetime,
        appointment_id: int,
        cancellation_reason: Optional[str] = None
    ) -> Dict:
        """
        Send appointment cancellation email
        
        Args:
            email: Customer's email address
            customer_name: Customer's name
            service_name: Service name
            staff_name: Staff name
            appointment_datetime: Original appointment datetime
            appointment_id: Appointment ID
            cancellation_reason: Reason for cancellation
        
        Returns:
            Result dictionary
        """
        subject = f"❌ Appointment Cancelled - #{appointment_id}"
        
        # Format datetime for display
        formatted_datetime = appointment_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        
        html_content = get_cancel_appointment_template(
            customer_name,
            service_name,
            staff_name,
            formatted_datetime,
            appointment_id,
            cancellation_reason
        )
        
        self._send_email(email, subject, html_content)
        
        return {
            "status": "success",
            "message": "Appointment cancellation email sent successfully",
            "email_sent_to": email,
            "email_type": "cancel_appointment"
        }


# Global email service instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Dependency injection for email service"""
    return email_service