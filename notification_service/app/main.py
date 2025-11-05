from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.token_validator import validate_token
from app.services.email_service import send_email
from app.config import settings

app = FastAPI(
    title="Salon Notification Service",
    description="Handles notification delivery for the Salon Appointment Booking System.",
    version="1.0.0"
)

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    message: str

@app.get("/")
def root():
    return {"message": "Notification Service is running"}


@app.post("/api/v1/notifications/send-email")
def send_email_notification(
    email_req: EmailRequest,
    authorization: str = Header(...)
):
    """
    Sends an email notification. Requires a valid Bearer token.
    """
    # Validate token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.replace("Bearer ", "").strip()
    user_id = validate_token(token)

    print(email_req)

    # Send email
    success = send_email(email_req.to_email, email_req.subject, email_req.message)

    if not success:
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to send email"}
        )

    # Return success response
    return {
        "status": "success",
        "message": f"Email sent to {email_req.to_email}",
        "sent_by_user": user_id
    }


# Optional health-check endpoint for Kubernetes
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Entry point (for uvicorn)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

