# Backend Documentation

A FastAPI-based backend for the AI Messaging application with SQLAlchemy ORM and Alembic migrations.

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy ORM
- **Migrations**: Alembic
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
├── db/
│   ├── config.py         # Database configuration and session management
│   └── models.py         # SQLAlchemy models
├── main.py               # FastAPI application entry point
├── alembic.ini           # Alembic configuration
└── requirements.txt      # Python dependencies
```

## Database Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./backend.db` |

### Supported Databases

- **SQLite** (development): `sqlite:///./backend.db`
- **PostgreSQL** (production): `postgresql://user:password@host:port/dbname`

### Database Configuration

The database configuration is defined in [`backend/db/config.py`](backend/db/config.py:7):

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./backend.db"  # Default to SQLite for development
)
```

## Models

### BaseModel

All models inherit from `BaseModel` which provides common fields:

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `created_at` | DateTime | Timestamp when record was created |
| `updated_at` | DateTime | Timestamp when record was last updated |

### User Model

Located in [`backend/db/models.py`](backend/db/models.py:15):

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

### Message Model

Located in [`backend/db/models.py`](backend/db/models.py:30):

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique message identifier |
| `sender_id` | Integer | Index, Not Null | Sender user ID |
| `recipient_id` | Integer | Index, Not Null | Recipient user ID |
| `content` | Text | Not Null | Message content |
| `is_read` | Boolean | Default: False | Read status |
| `parent_id` | Integer | Nullable | Parent message ID (for replies) |
| `conversation_id` | String(100) | Index, Nullable | Conversation grouping |

## Alembic Migrations

Alembic is used for database schema migration management.

### Alembic Configuration

The Alembic environment is configured in [`backend/alembic/env.py`](backend/alembic/env.py:1):

- Imports models from `backend.db.models`
- Uses `Base.metadata` from `backend.db.config`
- Supports both offline and online migration modes

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

# Downgrade to specific revision
python -m alembic downgrade <revision_id>
```

### Migration Files

Migrations are stored in [`backend/alembic/versions/`](backend/alembic/versions/). Each migration file contains:

- `upgrade()`: Applies schema changes
- `downgrade()`: Reverts schema changes

### Initial Migration

The initial migration [`753d9557b07b_initial.py`](backend/alembic/versions/753d9557b07b_initial.py:1) creates:
- `users` table with all user fields and indexes
- `messages` table with all message fields and indexes

## API Endpoints

The FastAPI application is defined in [`backend/main.py`](backend/main.py:15):

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

## Database Session Dependency

Use the `get_db` dependency to access the database in your endpoints:

```python
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from backend.db.config import get_db
from backend.db.models import User

app = FastAPI()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

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