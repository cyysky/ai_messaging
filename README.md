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

## Logging

The application uses centralized logging configured in [`backend/init_logs.py`](backend/init_logs.py:1). Log files are stored in the `logs/` directory by default.

| Logger | Log File | Description |
|--------|----------|-------------|
| `auth` | `logs/auth.log` | Authentication events |
| `twilio_webhook` | `logs/twilio_webhook.log` | Twilio webhook events |
| `messages` | `logs/messages.log` | Message operations |

Each log file:
- Maximum 1MB per file
- Up to 50 backup files (50MB total)
- Timestamped entries with logger name and level

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
| PUT | `/messages/{id}` | Update message |
| PUT | `/messages/{id}/read` | Mark as read |
| DELETE | `/messages/{id}` | Delete message |
| GET | `/messages/unread/count` | Get unread count |
| PUT | `/messages/read-all` | Mark all as read |

### Webhook

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/twilio_webhook` | Twilio incoming message webhook |

All endpoints except `/twilio_webhook` and `/auth/register` require authentication via JWT Bearer token.