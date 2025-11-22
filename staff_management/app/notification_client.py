"""
Notification Service Client
Helper for sending emails via Notification Service
"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NotificationClient:
    """Client for communicating with Notification Service"""
    
    def __init__(self):
        self.base_url = settings.NOTIFICATION_SERVICE_URL
        self.timeout = 30.0
    
    async def _send_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        token: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Send request to Notification Service
        
        Args:
            endpoint: API endpoint (e.g., 'register-user')
            data: Request payload
            token: Optional auth token
        
        Returns:
            Response dict or None if failed
        """
        url = f"{self.base_url}/api/v1/notifications/email/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    logger.info(f"Notification sent successfully: {endpoint}")
                    return response.json()
                else:
                    logger.error(f"Notification failed: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Notification timeout: {endpoint}")
            return None
        except Exception as e:
            logger.error(f"Notification error: {e}")
            return None
    
    # ========================================================================
    # Email Methods
    # ========================================================================
    
    async def send_register_user_email(
        self,
        email: str,
        full_name: str,
        username: str
    ) -> Optional[Dict]:
        """Send registration welcome email"""
        return await self._send_request(
            endpoint="register-user",
            data={
                "email": email,
                "full_name": full_name,
                "username": username
            }
        )
    
    async def send_reset_password_email(
        self,
        email: str,
        full_name: str,
        reset_token: str,
        expiry_minutes: int = 30
    ) -> Optional[Dict]:
        """Send password reset email"""
        return await self._send_request(
            endpoint="reset-password",
            data={
                "email": email,
                "full_name": full_name,
                "reset_token": reset_token,
                "expiry_minutes": expiry_minutes
            }
        )
    
    async def send_create_staff_email(
        self,
        email: str,
        full_name: str,
        position: str,
        username: str,
        temporary_password: Optional[str] = None,
        token: Optional[str] = None
    ) -> Optional[Dict]:
        """Send staff welcome email (requires admin token)"""
        data = {
            "email": email,
            "full_name": full_name,
            "position": position,
            "username": username
        }
        if temporary_password:
            data["temporary_password"] = temporary_password
        
        return await self._send_request(
            endpoint="create-staff",
            data=data,
            token=token
        )
    
    async def send_create_appointment_email(
        self,
        email: str,
        customer_name: str,
        service_name: str,
        staff_name: str,
        appointment_datetime: datetime,
        duration_minutes: int,
        price: float,
        appointment_id: int,
        token: Optional[str] = None
    ) -> Optional[Dict]:
        """Send appointment confirmation email"""
        return await self._send_request(
            endpoint="create-appointment",
            data={
                "email": email,
                "customer_name": customer_name,
                "service_name": service_name,
                "staff_name": staff_name,
                "appointment_datetime": appointment_datetime.isoformat(),
                "duration_minutes": duration_minutes,
                "price": price,
                "appointment_id": appointment_id
            },
            token=token
        )
    
    async def send_update_appointment_email(
        self,
        email: str,
        customer_name: str,
        service_name: str,
        staff_name: str,
        old_datetime: datetime,
        new_datetime: datetime,
        appointment_id: int,
        change_reason: Optional[str] = None,
        token: Optional[str] = None
    ) -> Optional[Dict]:
        """Send appointment update email"""
        data = {
            "email": email,
            "customer_name": customer_name,
            "service_name": service_name,
            "staff_name": staff_name,
            "old_datetime": old_datetime.isoformat(),
            "new_datetime": new_datetime.isoformat(),
            "appointment_id": appointment_id
        }
        if change_reason:
            data["change_reason"] = change_reason
        
        return await self._send_request(
            endpoint="update-appointment",
            data=data,
            token=token
        )
    
    async def send_cancel_appointment_email(
        self,
        email: str,
        customer_name: str,
        service_name: str,
        staff_name: str,
        appointment_datetime: datetime,
        appointment_id: int,
        cancellation_reason: Optional[str] = None,
        token: Optional[str] = None
    ) -> Optional[Dict]:
        """Send appointment cancellation email"""
        data = {
            "email": email,
            "customer_name": customer_name,
            "service_name": service_name,
            "staff_name": staff_name,
            "appointment_datetime": appointment_datetime.isoformat(),
            "appointment_id": appointment_id
        }
        if cancellation_reason:
            data["cancellation_reason"] = cancellation_reason
        
        return await self._send_request(
            endpoint="cancel-appointment",
            data=data,
            token=token
        )


# Global client instance
notification_client = NotificationClient()


def get_notification_client() -> NotificationClient:
    """Get notification client instance"""
    return notification_client