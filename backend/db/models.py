from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from backend.db.config import Base


class BaseModel(Base):
    """Base model with common fields for all tables"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(BaseModel):
    """User model - compatible with SQLite and PostgreSQL"""
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Profile fields
    full_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)


class Message(BaseModel):
    """Message model - compatible with SQLite and PostgreSQL"""
    __tablename__ = "messages"
    
    sender_id = Column(Integer, index=True, nullable=False)
    recipient_id = Column(Integer, index=True, nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # Optional: for message threading
    parent_id = Column(Integer, nullable=True)
    conversation_id = Column(String(100), index=True, nullable=True)