"""
Notification Service - RabbitMQ Consumer.
This service listens for appointment events and sends notifications.
"""
import pika
import json
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ Configuration
RABBITMQ_HOST = "localhost"
EXCHANGE_NAME = "salon_booking_events"
QUEUE_NAME = "notifications_queue"

# Email Configuration (for demo purposes)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "salon@example.com"
SENDER_PASSWORD = "your-app-password"  # Use environment variable in production

class NotificationService:
    """
    Notification service for handling appointment-related notifications.
    
    This service consumes events from RabbitMQ and sends appropriate
    notifications via email, SMS, or push notifications.
    """
    
    def __init__(self):
        """Initialize the notification service"""
        self.connection = None
        self.channel = None
        
    def connect_to_rabbitmq(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type='topic',
                durable=True
            )
            
            # Declare queue
            self.channel.queue_declare(queue=QUEUE_NAME, durable=True)
            
            # Bind queue to exchange with routing patterns
            routing_keys = [
                "appointment.booked",
                "appointment.confirmed",
                "appointment.cancelled",
                "appointment.reminder"
            ]
            
            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=EXCHANGE_NAME,
                    queue=QUEUE_NAME,
                    routing_key=routing_key
                )
            
            logger.info("Connected to RabbitMQ successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def send_email_notification(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MimeMultipart()
            message["From"] = SENDER_EMAIL
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MimeText(body, "plain"))
            
            # Connect to server and send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Enable security
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            text = message.as_string()
            server.sendmail(SENDER_EMAIL, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_sms_notification(self, phone_number: str, message: str) -> bool:
        """
        Send SMS notification (mock implementation).
        
        In production, integrate with SMS providers like Twilio, AWS SNS, etc.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
        
        Returns:
            True if sent successfully
        """
        # Mock SMS sending - log the message
        logger.info(f"SMS to {phone_number}: {message}")
        return True
    
    def get_user_contact_info(self, user_id: int) -> Dict[str, str]:
        """
        Get user contact information from User Service.
        
        In production, this would make an API call to User Service.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with email and phone information
        """
        # Mock implementation - in production, call User Service API
        return {
            "email": f"user{user_id}@example.com",
            "phone": "+1234567890",
            "full_name": f"Customer {user_id}"
        }
    
    def handle_appointment_booked(self, event_data: Dict[Any, Any]):
        """
        Handle appointment booked event.
        
        Sends confirmation email/SMS to customer about their booking request.
        
        Args:
            event_data: Event payload from RabbitMQ
        """
        try:
            appointment_id = event_data["appointment_id"]
            user_id = event_data["user_id"]
            appointment_datetime = event_data["appointment_datetime"]
            
            # Get user contact information
            user_info = self.get_user_contact_info(user_id)
            
            # Format appointment datetime
            apt_time = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
            formatted_time = apt_time.strftime("%B %d, %Y at %I:%M %p")
            
            # Send email confirmation
            subject = "Appointment Booking Confirmation - Salon"
            body = f"""
Dear {user_info['full_name']},

Your appointment booking request has been received!

Appointment Details:
- Date & Time: {formatted_time}
- Appointment ID: {appointment_id}
- Status: Pending Confirmation

We will confirm your appointment shortly and send you another notification.

Thank you for choosing our salon!

Best regards,
Salon Team
            """.strip()
            
            self.send_email_notification(user_info["email"], subject, body)
            
            # Send SMS confirmation
            sms_message = f"Salon: Your appointment for {formatted_time} is CONFIRMED (ID: {appointment_id}). See you then!"
            self.send_sms_notification(user_info["phone"], sms_message)
            
            logger.info(f"Processed appointment confirmed event for appointment {appointment_id}")
            
        except Exception as e:
            logger.error(f"Error handling appointment confirmed event: {e}")
    
    def handle_appointment_cancelled(self, event_data: Dict[Any, Any]):
        """
        Handle appointment cancelled event.
        
        Sends cancellation notification to customer.
        
        Args:
            event_data: Event payload from RabbitMQ
        """
        try:
            appointment_id = event_data["appointment_id"]
            user_id = event_data["user_id"]
            appointment_datetime = event_data["appointment_datetime"]
            cancellation_reason = event_data.get("cancellation_reason", "No reason provided")
            
            user_info = self.get_user_contact_info(user_id)
            
            apt_time = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
            formatted_time = apt_time.strftime("%B %d, %Y at %I:%M %p")
            
            # Send cancellation email
            subject = "Appointment Cancelled - Salon"
            body = f"""
Dear {user_info['full_name']},

We regret to inform you that your appointment has been cancelled.

Cancelled Appointment Details:
- Date & Time: {formatted_time}
- Appointment ID: {appointment_id}
- Reason: {cancellation_reason}

We apologize for any inconvenience caused. Please feel free to book another appointment at your convenience.

If you have any questions, please don't hesitate to contact us.

Best regards,
Salon Team
            """.strip()
            
            self.send_email_notification(user_info["email"], subject, body)
            
            # Send SMS notification
            sms_message = f"Salon: Your appointment for {formatted_time} has been cancelled (ID: {appointment_id}). Sorry for the inconvenience!"
            self.send_sms_notification(user_info["phone"], sms_message)
            
            logger.info(f"Processed appointment cancelled event for appointment {appointment_id}")
            
        except Exception as e:
            logger.error(f"Error handling appointment cancelled event: {e}")
    
    def process_message(self, channel, method, properties, body):
        """
        Process incoming messages from RabbitMQ.
        
        This is the main callback function that handles all types of events.
        
        Args:
            channel: RabbitMQ channel
            method: Message method
            properties: Message properties
            body: Message body (JSON)
        """
        try:
            # Parse message body
            event_data = json.loads(body.decode('utf-8'))
            event_type = method.routing_key
            
            logger.info(f"Received event: {event_type}")
            
            # Route to appropriate handler based on event type
            if event_type == "appointment.booked":
                self.handle_appointment_booked(event_data)
            elif event_type == "appointment.confirmed":
                self.handle_appointment_confirmed(event_data)
            elif event_type == "appointment.cancelled":
                self.handle_appointment_cancelled(event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
            
            # Acknowledge message processing
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
            # Reject message and don't requeue
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject message and requeue for retry
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """
        Start consuming messages from RabbitMQ.
        
        This method runs indefinitely, processing incoming events.
        """
        if not self.connect_to_rabbitmq():
            logger.error("Failed to connect to RabbitMQ. Exiting...")
            return
        
        try:
            # Set up consumer
            self.channel.basic_qos(prefetch_count=1)  # Process one message at a time
            self.channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=self.process_message
            )
            
            logger.info("Notification service started. Waiting for messages...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping notification service...")
            self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"Error in message consumption: {e}")

def main():
    """Main entry point for the notification service"""
    service = NotificationService()
    service.start_consuming()

if __name__ == "__main__":
    main()