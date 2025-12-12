from .logger import log_event
from fastapi import FastAPI
from app.schemas import AppointmentSchema
from fastapi import HTTPException
app = FastAPI()

@app.post("/appointments/")
async def create_appointment(appointment: AppointmentSchema):
    try:
        # [Your existing database save logic]
        
        # SUCCESS LOG 
        log_event(
            level="INFO", 
            message=f"Booking Confirmed for User {appointment.user_id}",
            extra_data={"amount": appointment.price, "type": appointment.service_type}
        )
        return {"status": "created"}

    except Exception as e:
        # ERROR LOG (This triggers the Alert)
        log_event(
            level="ERROR", 
            message="Booking Failed: Database Connection Timeout", # Simulate a critical error
            extra_data={"error_details": str(e)}
        )
        raise HTTPException(status_code=500, detail="Internal Error")

# DEMO TRICK: Add a specific Error Trigger Endpoint
# Add this so you don't have to break your real DB to show the alert

@app.post("/test-error")
async def trigger_demo_error():
    log_event("ERROR", "Payment Gateway Latency Critical", 
              service="payment-service")
    return {"status": "Demo Error Sent"}