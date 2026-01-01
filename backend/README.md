# Backend Documentation

A FastAPI-based backend for the AI Messaging application with SQLAlchemy ORM, Alembic migrations, and JWT authentication.

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) with bcrypt password hashing
- **Database Support**: SQLite (development), PostgreSQL (production)

## Project Structure

```
backend/
├── alembic/
│   ├── versions/          # Migration files
│   │   └── 753d9557b07b_initial.py
│   ├── env.py            # Alembic environment configuration
│   ├── script.py.mako    # Migration script template
│   └── README            # Generic Alembic README
├── auth/
│   ├── router.py         # Authentication API endpoints
│   ├── schemas.py        # Pydantic schemas
│   └── utils.py          # Authentication utilities
├── db/
│   ├── config.py         # Database configuration and session management
│   └── models.py         # SQLAlchemy models
├── messages/
│   ├── __init__.py
│   └── router.py         # Messages API endpoints
├── reports/
│   ├── __init__.py
│   └── router.py         # Reports API endpoints
├── tests/
│   ├── __init__.py
│   ├── test_auth.py      # Authentication tests
│   ├── test_messages.py  # Messages tests
│   └── test_reports.py   # Reports tests
├── main.py               # FastAPI application entry point
├── init_logs.py          # Logging configuration
├── alembic.ini           # Alembic configuration
└── requirements.txt      # Python dependencies
```

## Authentication System

### Features

- **JWT Authentication**: Access tokens (30 min) and refresh tokens (7 days)
- **Session Management**: Track user sessions with device/IP info
- **Password Security**: Bcrypt hashing with salt
- **Role-Based Access**: Role-based permissions system
- **User Management**: Full CRUD operations for users

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register a new user |
| `/auth/login` | POST | Login and get tokens |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/logout` | POST | Logout (invalidate token) |
| `/auth/logout-all` | POST | Logout from all devices |

### User Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/auth/me` | GET | Get current user info | Required |
| `/auth/me` | PUT | Update current user | Required |
| `/auth/me/password` | PUT | Change password | Required |

### Admin Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/auth/users` | GET | List all users | Superuser |
| `/auth/users/{id}` | GET | Get user by ID | Superuser |
| `/auth/users` | POST | Create user | Superuser |
| `/auth/users/{id}` | DELETE | Delete user | Superuser |
| `/auth/users/{id}/disable` | PUT | Disable user | Superuser |
| `/auth/users/{id}/enable` | PUT | Enable user | Superuser |
| `/auth/users/{id}/superuser` | PUT | Toggle superuser | Superuser |
| `/auth/users/{id}/roles` | PUT | Assign roles | Superuser |
| `/auth/users/{id}/roles` | GET | Get user roles | Superuser |

### Session Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/auth/sessions` | GET | List user sessions | Required |
| `/auth/sessions/{id}` | DELETE | Delete session | Required |

### Role Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/auth/roles` | GET | List all roles | Superuser |
| `/auth/roles` | POST | Create role | Superuser |
| `/auth/roles/{id}` | DELETE | Delete role | Superuser |

### Conversation Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/auth/conversations` | GET | List all conversations | Required |
| `/auth/conversations/{id}/messages` | GET | Get conversation messages | Required |
| `/auth/conversations/{id}/messages` | POST | Send message | Required |
| `/auth/conversations/{id}/read` | PUT | Mark conversation read | Required |

### Message Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/messages` | GET | List all messages | Required |
| `/messages/sent` | GET | List sent messages | Required |
| `/messages/received` | GET | List received messages | Required |
| `/messages/{id}` | GET | Get specific message | Required |
| `/messages` | POST | Send new message | Required |
| `/messages/{id}` | PUT | Update message | Required |
| `/messages/{id}/read` | PUT | Mark as read | Required |
| `/messages/{id}` | DELETE | Delete message | Required |
| `/messages/unread/count` | GET | Get unread count | Required |
| `/messages/read-all` | PUT | Mark all as read | Required |

### Report Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/reports` | POST | Create a new report | Required |
| `/reports` | GET | List user's reports | Required |
| `/reports/{id}` | GET | Get specific report | Owner/Superuser |
| `/reports/{id}` | PUT | Update own report | Owner (open only) |
| `/reports/admin/all` | GET | List all reports | Superuser |
| `/reports/{id}/comment` | POST | Add comment/status | Superuser |
| `/reports/{id}/resolve` | PUT | Resolve report | Superuser |

### Login Response (AuthResponse)

The `/auth/login` endpoint returns an `AuthResponse` that includes both tokens and user information:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "bio": null,
    "phone_number": null,
    "is_active": true,
    "is_superuser": true,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  }
}
```

The `user` object in the response includes the `is_superuser` field, which the frontend uses to determine if the user has access to the User Management dashboard.

### Using Authentication

```python
import requests

# Login
response = requests.post("http://localhost:8000/auth/login", json={
    "username": "user",
    "password": "password"
})
tokens = response.json()
access_token = tokens["access_token"]

# Use token in requests
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/auth/me", headers=headers)
```

## Database Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./backend.db` |

### Supported Databases

- **SQLite** (development): `sqlite:///./backend.db`
- **PostgreSQL** (production): `postgresql://user:password@host:port/dbname`

## Models

### BaseModel

All models inherit from `BaseModel` which provides common fields:

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `created_at` | DateTime | Timestamp when record was created |
| `updated_at` | DateTime | Timestamp when record was last updated |

### User Model

Located in [`backend/db/models.py`](backend/db/models.py:16):

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique user identifier |
| `username` | String(100) | Unique, Index, Not Null | Username |
| `email` | String(255) | Unique, Index, Not Null | Email address |
| `hashed_password` | String(255) | Not Null | Bcrypt hashed password |
| `is_active` | Boolean | Default: True | Account active status |
| `is_superuser` | Boolean | Default: False | Admin privileges |
| `full_name` | String(255) | Nullable | User's full name |
| `bio` | Text | Nullable | User biography |

### Role Model

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique role identifier |
| `name` | String(100) | Unique, Index, Not Null | Role name |
| `description` | String(255) | Nullable | Role description |

### Session Model

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique session identifier |
| `user_id` | Integer | Foreign Key, Not Null | User ID |
| `session_token` | String(255) | Unique, Index, Not Null | Session token |
| `device_info` | String(255) | Nullable | Device information |
| `ip_address` | String(50) | Nullable | IP address |
| `is_active` | Boolean | Default: True | Session active status |
| `expires_at` | DateTime | Not Null | Session expiration |

### RefreshToken Model

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique token identifier |
| `user_id` | Integer | Foreign Key, Not Null | User ID |
| `token` | String(255) | Unique, Index, Not Null | Refresh token |
| `expires_at` | DateTime | Not Null | Token expiration |
| `is_used` | Boolean | Default: False | Token used status |

### UserRole Model (Many-to-Many)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique identifier |
| `user_id` | Integer | Foreign Key, Not Null | User ID |
| `role_id` | Integer | Foreign Key, Not Null | Role ID |

### Message Model

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique message identifier |
| `sender_id` | Integer | Index, Not Null | Sender user ID |
| `recipient_id` | Integer | Index, Not Null | Recipient user ID |
| `content` | Text | Not Null | Message content |
| `is_read` | Boolean | Default: False | Read status |
| `parent_id` | Integer | Nullable | Parent message ID (for replies) |
| `conversation_id` | String(100) | Index, Nullable | Conversation grouping |

### Report Model

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique report identifier |
| `reporter_id` | Integer | Foreign Key, Not Null | Reporter user ID |
| `title` | String(255) | Not Null | Report title |
| `content` | Text | Not Null | Report content |
| `status` | String(50) | Default: "open" | Status: open, in_progress, resolved |
| `comment` | Text | Nullable | Superuser comment |
| `resolved_at` | DateTime | Nullable | Resolution timestamp |
| `resolved_by` | Integer | Foreign Key, Nullable | Resolver user ID |

## Alembic Migrations

Alembic is used for database schema migration management.

### Migration Commands

```bash
# Navigate to backend directory
cd backend

# Generate a new empty migration
python -m alembic revision -m "description"

# Generate auto migration (detects model changes)
python -m alembic revision --autogenerate -m "description"

# Apply all pending migrations
python -m alembic upgrade head

# Apply specific migration
python -m alembic upgrade <revision_id>

# Show current migration revision
python -m alembic current

# Show complete migration history
python -m alembic history

# Downgrade to previous migration
python -m alembic downgrade -1
```

## API Endpoints

The FastAPI application is defined in [`backend/main.py`](backend/main.py:17):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint, returns "Hello World" |
| `/health` | GET | Health check endpoint |
| `/db-test` | GET | Database connection test |

### Running the Server

```bash
cd backend
python main.py
```

The server will start on `0.0.0.0:8000` by default (configurable via environment variables).

### Environment Variables for Server

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_MESSAGE_HOST` | Server host | `0.0.0.0` |
| `AI_MESSAGE_PORT` | Server port | `8000` |
| `AI_MESSAGE_DOMAIN` | Domain name | `localhost` |
| `AI_MESSAGE_SSL_CERT` | SSL certificate path | `ssl/cert.pem` |
| `AI_MESSAGE_SSL_KEY` | SSL key path | `ssl/key.pem` |

## Testing

### Running Tests

```bash
cd backend
python -m pytest tests/test_auth.py -v
```

### Test Coverage

The test suite includes:
- Password hashing and verification
- JWT token creation and decoding
- Session token generation
- Token expiry validation
- Authentication integration flows

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (copy `.env.example` to `.env` and modify)

3. Run migrations:
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

4. Start the server:
   ```bash
   cd backend
   python main.py
   ```

5. Run tests:
   ```bash
   cd backend
   python -m pytest tests/test_auth.py -v
   ```

## Production Deployment

For production, use PostgreSQL:

1. Set `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@host:port/dbname"
   ```

2. Run migrations:
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

3. Start the server without SSL (use a reverse proxy like Nginx for SSL termination)

## Logging

The application uses a centralized logging module [`backend/init_logs.py`](backend/init_logs.py:1) that provides configured loggers for all modules.

### Log Files

| Logger | Log File | Description |
|--------|----------|-------------|
| `auth` | `logs/auth.log` | Authentication events |
| `twilio_webhook` | `logs/twilio_webhook.log` | Twilio webhook events |
| `messages` | `logs/messages.log` | Message operations |
| `reports` | `logs/reports.log` | Report operations |

### Configuration

Logs are stored in the folder specified by `AI_MESSAGE_LOGS_FOLDER` environment variable (default: `logs`). Each log file:
- Maximum 1MB per file
- Up to 50 backup files (50MB total)
- Timestamped entries with logger name and level

### Using Loggers

```python
from init_logs import messages_logger

# Log messages
messages_logger.info("User sent a message")
messages_logger.error("Failed to send message")
messages_logger.warning("Message rate limit approaching")
```

## Security Notes

- Change `SECRET_KEY` in [`backend/auth/utils.py`](backend/auth/utils.py:12) for production
- Use strong passwords and enable password complexity validation
- Set appropriate token expiration times
- Use HTTPS in production
- Regularly rotate refresh tokens