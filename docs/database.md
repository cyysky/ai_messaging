# Database Specification

This document describes the database schema and configuration for the AI Message backend.

## Database Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Connection URL for the database | `sqlite:///./backend.db` |

### Supported Databases

- **SQLite** (development): `sqlite:///./backend.db`
- **PostgreSQL** (production): `postgresql://user:password@host:port/dbname`

## Schema

### Base Model

All models inherit from `BaseModel` which provides:

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `created_at` | DateTime | Timestamp when record was created |
| `updated_at` | DateTime | Timestamp when record was last updated |

### Users Table

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
| `created_at` | DateTime | Not Null | Creation timestamp |
| `updated_at` | DateTime | Not Null | Last update timestamp |

### Roles Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique role identifier |
| `name` | String(100) | Unique, Index, Not Null | Role name |
| `description` | String(255) | Nullable | Role description |
| `created_at` | DateTime | Not Null | Creation timestamp |
| `updated_at` | DateTime | Not Null | Last update timestamp |

### User Roles Table (Many-to-Many)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique identifier |
| `user_id` | Integer | Foreign Key, Not Null | User ID |
| `role_id` | Integer | Foreign Key, Not Null | Role ID |
| `created_at` | DateTime | Not Null | Creation timestamp |
| `updated_at` | DateTime | Not Null | Last update timestamp |

### Sessions Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique session identifier |
| `user_id` | Integer | Foreign Key, Not Null | User ID |
| `session_token` | String(255) | Unique, Index, Not Null | Session token |
| `device_info` | String(255) | Nullable | Device information |
| `ip_address` | String(50) | Nullable | IP address |
| `is_active` | Boolean | Default: True | Session active status |
| `expires_at` | DateTime | Not Null | Session expiration |
| `created_at` | DateTime | Not Null | Creation timestamp |
| `updated_at` | DateTime | Not Null | Last update timestamp |

### Refresh Tokens Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique token identifier |
| `user_id` | Integer | Foreign Key, Not Null | User ID |
| `token` | String(255) | Unique, Index, Not Null | Refresh token |
| `expires_at` | DateTime | Not Null | Token expiration |
| `is_used` | Boolean | Default: False | Token used status |
| `created_at` | DateTime | Not Null | Creation timestamp |

### Messages Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique message identifier |
| `sender_id` | Integer | Index, Not Null | Sender user ID |
| `recipient_id` | Integer | Index, Not Null | Recipient user ID |
| `content` | Text | Not Null | Message content |
| `is_read` | Boolean | Default: False | Read status |
| `parent_id` | Integer | Nullable | Parent message ID (for replies) |
| `conversation_id` | String(100) | Index, Nullable | Conversation grouping |
| `created_at` | DateTime | Not Null | Creation timestamp |
| `updated_at` | DateTime | Not Null | Last update timestamp |

## Indexes

### Users Table
- `ix_users_id` - Primary key index
- `ix_users_username` - Unique index on username
- `ix_users_email` - Unique index on email

### Roles Table
- `ix_roles_id` - Primary key index
- `ix_roles_name` - Unique index on name

### User Roles Table
- `ix_user_roles_id` - Primary key index
- `ix_user_roles_user_id` - Index on user_id
- `ix_user_roles_role_id` - Index on role_id

### Sessions Table
- `ix_sessions_id` - Primary key index
- `ix_sessions_session_token` - Unique index on session_token

### Refresh Tokens Table
- `ix_refresh_tokens_id` - Primary key index
- `ix_refresh_tokens_token` - Unique index on token

### Messages Table
- `ix_messages_id` - Primary key index
- `ix_messages_sender_id` - Index on sender_id
- `ix_messages_recipient_id` - Index on recipient_id
- `ix_messages_conversation_id` - Index on conversation_id

## Relationships

### User Relationships
- User has many Sessions (cascade delete)
- User has many RefreshTokens (cascade delete)
- User has many UserRoles (cascade delete)
- User has many Roles through UserRoles

### Role Relationships
- Role has many UserRoles (cascade delete)
- Role has many Users through UserRoles

## Alembic Migrations

### Commands

```bash
# Generate a new migration
cd backend
python -m alembic revision -m "description"

# Generate auto migration
python -m alembic revision --autogenerate -m "description"

# Apply migrations
python -m alembic upgrade head

# Show current revision
python -m alembic current

# Show migration history
python -m alembic history
```

### Migration Files

Migrations are stored in `backend/alembic/versions/`

## Usage Examples

### Database Session Dependency

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from db.config import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Creating Records

```python
from db.models import User
from db.config import SessionLocal

db = SessionLocal()
new_user = User(username="john", email="john@example.com", hashed_password="hash")
db.add(new_user)
db.commit()
db.close()
```

### Authentication Example

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.config import get_db
from db.models import User
from auth.utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user