"""
RabbitMQ message publishing for appointment events.
"""
import pika
import json
import logging
from typing import Dict, Any
from . import schemas
import datetime

# RabbitMQ configuration
RABBITMQ_HOST = "localhost"  # In production, use environment variable
EXCHANGE_NAME = "salon_booking_events"

def get_rabbitmq_connection():
    """
    Establish connection to RabbitMQ.
    
    Returns:
        pika connection object
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        return connection
    except Exception as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
        return None

def publish_event(event_type: str, event_data: Dict[Any, Any]) -> bool:
    """
    Publish an event to RabbitMQ exchange.
    
    Args:
        event_type: Type of event (routing key)
        event_data: Event payload data
    
    Returns:
        True if published successfully, False otherwise
    """
    connection = get_rabbitmq_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        # Declare exchange if it doesn't exist
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type='topic',
            durable=True
        )
        
        # Publish message
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=event_type,
            body=json.dumps(event_data, default=str),  # Convert datetime to string
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
        
        connection.close()
        logging.info(f"Published event: {event_type}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to publish event {event_type}: {e}")
        return False

def publish_appointment_booked(appointment: schemas.AppointmentResponse) -> bool:
    """
    Publish appointment booked event.
    
    Args:
        appointment: Appointment data
    
    Returns:
        True if published successfully
    """
    event = schemas.AppointmentBookedEvent(
        appointment_id=appointment.id,
        user_id=appointment.user_id,
        staff_id=appointment.staff_id,
        service_id=appointment.service_id,
        appointment_datetime=appointment.appointment_datetime,
        service_price=appointment.service_price,
        customer_notes=appointment.customer_notes
    )
    
    return publish_event("appointment.booked", event.dict())

def publish_appointment_confirmed(appointment: schemas.AppointmentResponse) -> bool:
    """Publish appointment confirmed event"""
    event = schemas.AppointmentConfirmedEvent(
        appointment_id=appointment.id,
        user_id=appointment.user_id,
        staff_id=appointment.staff_id,
        service_id=appointment.service_id,
        appointment_datetime=appointment.appointment_datetime,
        confirmed_at=appointment.confirmed_at or datetime.now()
    )
    
    return publish_event("appointment.confirmed", event.dict())

def publish_appointment_cancelled(appointment: schemas.AppointmentResponse, reason: str = None) -> bool:
    """Publish appointment cancelled event"""
    event = schemas.AppointmentCancelledEvent(
        appointment_id=appointment.id,
        user_id=appointment.user_id,
        staff_id=appointment.staff_id,
        service_id=appointment.service_id,
        appointment_datetime=appointment.appointment_datetime,
        cancelled_at=datetime.now(),
        cancellation_reason=reason
    )
    
    return publish_event("appointment.cancelled", event.dict())