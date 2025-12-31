import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from sqlalchemy.orm import Session

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.config import get_db, engine
from db.models import Base, User, Message
from auth.router import router as auth_router

load_dotenv()

# Configure logging for auth module
logs_folder = os.getenv("AI_MESSAGE_LOGS_FOLDER", "logs")
logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), logs_folder)
os.makedirs(logs_path, exist_ok=True)

auth_logger = logging.getLogger("auth")
auth_logger.setLevel(logging.INFO)

# Rotating file handler: max 50MB total (50 files x 1MB each)
auth_handler = RotatingFileHandler(
    os.path.join(logs_path, "auth.log"),
    maxBytes=1 * 1024 * 1024,  # 1MB per file
    backupCount=50  # 50 files = 50MB max
)
auth_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
auth_logger.addHandler(auth_handler)

# Configure logging for twilio_webhook module
twilio_logger = logging.getLogger("twilio_webhook")
twilio_logger.setLevel(logging.INFO)

# Rotating file handler: max 50MB total (50 files x 1MB each)
twilio_handler = RotatingFileHandler(
    os.path.join(logs_path, "twilio_webhook.log"),
    maxBytes=1 * 1024 * 1024,  # 1MB per file
    backupCount=50  # 50 files = 50MB max
)
twilio_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
twilio_logger.addHandler(twilio_handler)

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Message API",
    description="Authentication and user management API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Example endpoint with database dependency
@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    return {"status": "database connection working"}


@app.post("/twilio_webhook")
async def twilio_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Twilio webhook endpoint for incoming messages.
    Logs raw request and saves to database if phone number matches a user.
    """
    # Get raw request body for logging
    try:
        raw_body = await request.body()
        raw_text = raw_body.decode('utf-8') if raw_body else ""
    except Exception as e:
        raw_text = f"Error reading body: {str(e)}"
        raw_body = b""

    # Log the raw request
    twilio_logger.info(f"Raw Twilio request: {raw_text}")

    # Parse form data from the request
    form_data = {}
    try:
        # Try to parse as form data (application/x-www-form-urlencoded)
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            form_data = {k: v for k, v in (pair.split("=") for pair in raw_text.split("&") if "=" in pair)}
        elif "application/json" in content_type:
            form_data = json.loads(raw_text) if raw_text else {}
    except Exception as e:
        twilio_logger.error(f"Error parsing request body: {str(e)}")
        form_data = {"raw": raw_text}

    # Get phone number from Twilio request
    from_number = form_data.get("From", form_data.get("from", ""))
    to_number = form_data.get("To", form_data.get("to", ""))
    message_body = form_data.get("Body", form_data.get("body", ""))
    message_sid = form_data.get("MessageSid", form_data.get("message_sid", ""))

    twilio_logger.info(f"From: {from_number}, To: {to_number}, Body: {message_body[:100]}...")

    # Look up user by phone number
    user = None
    if from_number:
        # Normalize phone number (remove non-digits for comparison)
        normalized_from = "".join(filter(str.isdigit, from_number))
        user = db.query(User).filter(
            User.phone_number.isnot(None)
        ).all()
        
        for u in user:
            if u.phone_number:
                normalized_user_phone = "".join(filter(str.isdigit, u.phone_number))
                if normalized_user_phone in normalized_from or normalized_from in normalized_user_phone:
                    user = u
                    break
        else:
            user = None

    if user:
        twilio_logger.info(f"Found user {user.username} for phone number {from_number}")
        
        # Create message record
        message = Message(
            sender_id=user.id,
            recipient_id=user.id,  # Self-message for now
            content=message_body,
            conversation_id=message_sid or from_number
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        twilio_logger.info(f"Saved message {message.id} for user {user.username}")
        return {"status": "message saved", "user_id": user.id, "message_id": message.id}
    else:
        twilio_logger.warning(f"No user found for phone number {from_number}")
        return {"status": "user not found", "from": from_number}

if __name__ == "__main__":
    host = os.getenv("AI_MESSAGE_HOST", "0.0.0.0")
    port = int(os.getenv("AI_MESSAGE_PORT", 8000))
    domain = os.getenv("AI_MESSAGE_DOMAIN", "localhost")
    cert_file = os.getenv("AI_MESSAGE_SSL_CERT", "ssl/cert.pem")
    key_file = os.getenv("AI_MESSAGE_SSL_KEY", "ssl/key.pem")
    
    print(f"Starting server for domain: {domain}")
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        ssl_certfile=cert_file,
        ssl_keyfile=key_file
    )