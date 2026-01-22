# AI Messaging Application

## Git Setup

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/cyysky/ai_messaging.git
git push -u origin main
```

## Application Setup

uv venv --python 3.13 .venv
source .venv/bin/activate

1. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies and run:

## Backend

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run the server
python -m backend.main
```

## Running Tests

```bash
# Install test dependencies
pip install pytest

# Run message tests
python -m pytest backend/tests/test_messages.py -v

# Run auth tests
python -m pytest backend/tests/test_auth.py -v

# Run report tests
python -m pytest backend/tests/test_reports.py -v
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_MESSAGE_HOST` | Backend host | `0.0.0.0` |
| `AI_MESSAGE_PORT` | Backend port | `8000` |
| `AI_MESSAGE_DOMAIN` | API domain | `api.example.com` |
| `AI_MESSAGE_FRONTEND_PORT` | Frontend dev server port | `3000` |
| `AI_MESSAGE_FRONTEND_SSL` | Enable HTTPS for frontend dev server | `false` |
| `AI_MESSAGE_DATABASE_URL` | Database connection string | `sqlite:///./backend/backend.db` |
| `AI_MESSAGE_SSL_CERT` | SSL certificate path | `ssl/cert.pem` |
| `AI_MESSAGE_SSL_KEY` | SSL private key path | `ssl/key.pem` |
| `AI_MESSAGE_LOGS_FOLDER` | Logs directory | `logs` |

### Twilio Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | - |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | - |
| `TWILIO_PHONE_NUMBER` | Twilio phone number (for sending) | - |

## Logging

The application uses centralized logging configured in [`backend/init_logs.py`](backend/init_logs.py:1). Log files are stored in the `logs/` directory by default.

### Available Loggers

| Logger | Log File | Description |
|--------|----------|-------------|
| `auth` | `logs/auth.log` | Authentication events |
| `twilio_logger` | `logs/twilio_webhook.log` | Twilio webhook & reply events |
| `messages_logger` | `logs/messages.log` | Message operations |
| `orchestrator_logger` | `logs/orchestrator.log` | AI orchestration & agent debugging |

### Adding New Loggers

To add a new logger, edit `backend/init_logs.py`:

```python
from init_logs import setup_logger

# Add at the bottom:
my_logger = setup_logger("my_module", "my_module.log")

# Then import in your module:
# from init_logs import my_logger
# my_logger.info("Your message")
```

### Log File Properties

Each log file:
- Maximum 1MB per file
- Up to 50 backup files (50MB total)
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

Example output:
```
2026-01-22 15:30:45,123 - orchestrator - INFO - User 1: make a report about... (history_len=1)
2026-01-22 15:30:45,456 - orchestrator - INFO - Routing to agent: report_agent
2026-01-22 15:30:46,789 - orchestrator - INFO - report_agent calling function: create_report
```

## SSL Setup

To enable HTTPS for the frontend dev server:
1. Set `AI_MESSAGE_FRONTEND_SSL=true` in `.env`
2. Ensure SSL certificates exist at the paths specified in `AI_MESSAGE_SSL_CERT` and `AI_MESSAGE_SSL_KEY`

## API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout |
| POST | `/auth/logout-all` | Logout from all devices |
| GET | `/auth/me` | Get current user |
| PUT | `/auth/me` | Update current user |
| PUT | `/auth/me/password` | Change password |
| GET | `/auth/users` | List users (superuser) |
| GET | `/auth/users/{id}` | Get user (superuser) |
| POST | `/auth/users` | Create user (superuser) |
| DELETE | `/auth/users/{id}` | Delete user (superuser) |
| PUT | `/auth/users/{id}/disable` | Disable user (superuser) |
| PUT | `/auth/users/{id}/enable` | Enable user (superuser) |
| GET | `/auth/sessions` | List user sessions |
| DELETE | `/auth/sessions/{id}` | Delete session |
| GET | `/auth/roles` | List roles (superuser) |
| POST | `/auth/roles` | Create role (superuser) |
| DELETE | `/auth/roles/{id}` | Delete role (superuser) |
| PUT | `/auth/users/{id}/roles` | Assign roles (superuser) |
| GET | `/auth/conversations` | List conversations |
| GET | `/auth/conversations/{id}/messages` | Get conversation messages |
| POST | `/auth/conversations/{id}/messages` | Send message |
| PUT | `/auth/conversations/{id}/read` | Mark conversation read |

### Messages (`/messages`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/messages` | List all messages |
| GET | `/messages/sent` | List sent messages |
| GET | `/messages/received` | List received messages |
| GET | `/messages/{id}` | Get specific message |
| POST | `/messages` | Send new message |
| POST | `/messages` (recipient_id=-1) | Send to AI bot (auto-response) |
| PUT | `/messages/{id}` | Update message |
| PUT | `/messages/{id}/read` | Mark as read |
| DELETE | `/messages/{id}` | Delete message |
| GET | `/messages/unread/count` | Get unread count |
| PUT | `/messages/read-all` | Mark all as read |
| POST | `/messages/ai` | Send message to AI (sync response) |
| GET | `/messages/history` | Get chat history |
| DELETE | `/messages/history/clear` | Clear chat history |

#### AI Message Integration

**Pattern 1: Non-blocking (Recommended for webhooks)**
```bash
POST /messages
{
  "recipient_id": -1,  # AI_BOT_USER_ID
  "content": "Show my reports"
}
```
- Message is saved to database
- AI processing happens in background via BackgroundTasks
- Returns user message immediately
- AI response is saved asynchronously

**Pattern 2: Synchronous (For immediate response)**
```bash
POST /messages/ai
{
  "content": "Show my reports"
}
```
- Waits for AI processing
- Returns AI response directly
- Both user and AI messages saved to database

**Pattern 3: Webhook (Twilio)**
```bash
POST /twilio_webhook
```
- Twilio sends incoming SMS
- Message is saved
- AI processing triggered in background
- AI response returned to Twilio for delivery

### Reports (`/reports`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/reports` | Create a new report | Authenticated |
| GET | `/reports` | List user's reports | Authenticated |
| GET | `/reports/{id}` | Get specific report | Owner/Superuser |
| PUT | `/reports/{id}` | Update own report | Owner (open only) |
| GET | `/reports/admin/all` | List all reports | Superuser |
| POST | `/reports/{id}/comment` | Add comment/status | Superuser |
| PUT | `/reports/{id}/resolve` | Resolve report | Superuser |

### Webhook

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/twilio_webhook` | Twilio incoming message webhook |

All endpoints except `/twilio_webhook` and `/auth/register` require authentication via JWT Bearer token.

## AI Message Processing

### Architecture

```
[Channel: Twilio/Web/API] → Save Message → BackgroundTasks → Orchestrator → [Agent]
                                                                          → AI Response
                                                                          → Save Response
```

### Chat History

- Maximum 50 entries (user + assistant messages only)
- Managed by `ChatHistory` class in `backend/orchestrator/__init__.py`
- Stored in memory (per server instance)
- Accessible via `/messages/history` endpoint

### AI Agents

| Agent | Description | Functions |
|-------|-------------|-----------|
| `report_agent` | Report management | get_my_reports, get_report, update_report |
| General | Conversational AI | General questions and responses |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LITELLM_BASEURL` | LiteLLM API base URL | - |
| `LITELLM_API_KEY` | LiteLLM API key | - |
| `LITELLM_MODEL` | Model name | `gpt-3.5-turbo-1106` |
| `CHAT_HISTORY_MAX` | Max chat history entries | `50` |
| `AI_BOT_USER_ID` | User ID for AI bot | `-1` |

### Adding New Agents

1. Create agent in `backend/orchestrator/` (see `report_agent.py` for pattern)
2. Register in `backend/orchestrator/__init__.py` via `setup_orchestrator()`
3. Agent pattern requires: `SYSTEM_PROMPT`, `TOOLS`, `chat_func(user_id, ...)`

### Twilio Integration

The application supports WhatsApp messaging via Twilio. Messages sent to your Twilio number are processed through the AI orchestrator and replies are sent back automatically.

#### Setup

1. Create a Twilio account and get a phone number with WhatsApp
2. Add credentials to `.env`:
   ```
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=whatsapp:+1234567890
   ```
3. Configure the webhook in Twilio Console:
   - **A Message Comes In**: `https://yourdomain.com/twilio_webhook`
   - **Method**: POST

#### Message Flow (Twilio/WhatsApp)

```
User sends WhatsApp message
         ↓
Twilio POSTs to /twilio_webhook
         ↓
Save message to database
         ↓
Look up user by phone number
         ↓
Trigger BackgroundTasks for AI processing
         ↓
Return 200 OK to Twilio immediately
         ↓
Orchestrator processes message
         ↓
AI response saved to database
         ↓
Send reply via Twilio API (whatsapp:+user_number)
         ↓
User receives WhatsApp reply
```

#### Multi-Channel Support

The `process_ai_response_task` function supports multiple channels:

| Channel | Description |
|---------|-------------|
| `twilio` | SMS or WhatsApp via Twilio API |
| `telegram` | Telegram Bot API (TODO) |
| `web` | Web UI responses (already in DB) |

For new channels:
1. Create webhook endpoint similar to `/twilio_webhook`
2. Pass `channel`, `original_from`, and `is_whatsapp` to background task
3. Implement channel-specific reply logic