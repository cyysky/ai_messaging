import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from sqlalchemy.orm import Session

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.config import get_db, engine
from db.models import Base, User, Message
from auth.router import router as auth_router
from messages.router import router as messages_router
from reports.router import router as reports_router
from init_logs import auth_logger, twilio_logger

load_dotenv()

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Setup AI orchestrator
from orchestrator import setup_orchestrator
setup_orchestrator()

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

# Include messages router
app.include_router(messages_router)

# Include reports router
app.include_router(reports_router)

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


def process_ai_response_task(user_id: int, message_content: str, conversation_id: str, channel: str = "twilio", original_from: str = "", is_whatsapp: bool = False):
    """
    Background task to process AI response for a message.

    This is called automatically after a message is saved to trigger AI processing.
    Sends the AI response back to the appropriate channel.
    """
    from orchestrator import get_orchestrator
    from sqlalchemy.orm import Session
    from db.config import get_db
    from db.models import Message

    try:
        twilio_logger.info(f"[BackgroundTask] Processing AI response for user {user_id} via {channel} (whatsapp={is_whatsapp})")

        # Get orchestrator
        orchestrator = get_orchestrator()

        # Get AI response
        ai_response = orchestrator.process_message(user_id, message_content)
        twilio_logger.info(f"[BackgroundTask] AI response generated: {ai_response[:100]}...")

        # Save AI response as a new message
        db: Session = next(get_db())
        try:
            ai_message = Message(
                sender_id=-1,  # AI bot user ID
                recipient_id=user_id,
                content=ai_response,
                conversation_id=conversation_id,
                is_read=False
            )
            db.add(ai_message)
            db.commit()
            twilio_logger.info(f"[BackgroundTask] AI message saved: {ai_message.id}")
        finally:
            db.close()

        # Send response back to the appropriate channel
        if channel == "twilio" and original_from:
            _send_twilio_reply(original_from, ai_response, is_whatsapp=is_whatsapp)

    except Exception as e:
        twilio_logger.error(f"[BackgroundTask] Error processing AI response: {e}")


def _format_whatsapp_number(from_number: str) -> str:
    """Format a WhatsApp number from URL-encoded format.

    Twilio sends numbers as: whatsapp%3A%2B60127939038
    Twilio API expects: whatsapp:+60127939038
    """
    from urllib.parse import unquote

    # URL decode the number
    decoded = unquote(from_number)

    # If it's a WhatsApp number, ensure proper format
    if decoded.lower().startswith("whatsapp:"):
        # Remove any existing prefix issues and ensure clean format
        # e.g., "whatsapp:+60127939038"
        return decoded

    return decoded


def _send_twilio_reply(to_number: str, message: str, is_whatsapp: bool = False):
    """Send reply via Twilio API (SMS or WhatsApp)."""
    try:
        from twilio.rest import Client
        from dotenv import load_dotenv
        import os

        load_dotenv()

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not all([account_sid, auth_token, twilio_number]):
            twilio_logger.warning("[Twilio] Missing Twilio credentials")
            return

        # Format the recipient number
        recipient = _format_whatsapp_number(to_number)

        # Get sender number and format for WhatsApp if needed
        sender = twilio_number
        if is_whatsapp:
            # For WhatsApp, format both as whatsapp:...
            recipient = f"whatsapp:{recipient}" if not recipient.lower().startswith("whatsapp:") else recipient
            sender = f"whatsapp:{sender}" if not sender.lower().startswith("whatsapp:") else sender
        else:
            # For SMS, ensure plain format (remove whatsapp: prefix if present)
            recipient = recipient.replace("whatsapp:", "") if recipient.lower().startswith("whatsapp:") else recipient
            sender = sender.replace("whatsapp:", "") if sender.lower().startswith("whatsapp:") else sender

        twilio_logger.info(f"[Twilio] Sending message: from={sender}, to={recipient}")

        client = Client(account_sid, auth_token)
        twilio_message = client.messages.create(
            body=message,
            from_=sender,
            to=recipient
        )
        twilio_logger.info(f"[Twilio] Reply sent: {twilio_message.sid}")

    except Exception as e:
        twilio_logger.error(f"[Twilio] Failed to send reply: {e}")


# =============================================================================
# AI MESSAGE PROCESSING PATTERN
# =============================================================================
# When a message is saved (via any channel), the AI should automatically respond.
# This is implemented using a background task to avoid blocking the webhook.
#
# Pattern for new channels (WhatsApp, Web, API, etc.):
#   1. Save the incoming message to the database
#   2. Trigger AI processing via BackgroundTasks
#   3. Return success to the channel immediately
#
# The AI processing flow:
#   - Message is saved → process_ai_response_task (BackgroundTasks)
#   - Orchestrator checks message content for agent routing
#   - If report-related → report_agent handles it
#   - Otherwise → general conversational AI
#   - AI response is saved as a new message
# =============================================================================

@app.post("/twilio_webhook")
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Twilio webhook endpoint for incoming messages.
    Logs raw request, saves to database, and triggers AI processing in background.
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

        # Determine if this is WhatsApp (check for "whatsapp:" in From field)
        is_whatsapp = "whatsapp:" in from_number.lower() or "whatsapp%3a" in from_number.lower()

        # Trigger AI processing in background (non-blocking)
        background_tasks.add_task(
            process_ai_response_task,
            user_id=user.id,
            message_content=message_body,
            conversation_id=message_sid or from_number,
            channel="twilio",
            original_from=from_number,
            is_whatsapp=is_whatsapp
        )
        twilio_logger.info(f"[BackgroundTask] Queued AI processing for message {message.id}")

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