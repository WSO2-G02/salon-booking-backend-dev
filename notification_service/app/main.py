from fastapi import FastAPI, Depends
from app.services.email_service import send_email
from app.services.token_validator import validate_token

app = FastAPI(title="Notification Service", version="1.0")

@app.post("/api/v1/notifications/send-email")
async def send_notification(payload: dict, user=Depends(validate_token)):
    subject = payload.get("subject")
    recipient = payload.get("to_email")
    message = payload.get("message", "<p>No message provided</p>")

    send_email(subject, recipient, message)

    return {
        "status": "success",
        "data": {"email_sent_to": recipient},
        "message": "Operation completed successfully"
    }
