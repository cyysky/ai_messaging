from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.config import Base


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
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    
    # Session relationship
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    # Reports relationship - user as reporter
    reports = relationship("Report", back_populates="reporter", cascade="all, delete-orphan", foreign_keys="Report.reporter_id")


class Role(BaseModel):
    """Role model for user permissions"""
    __tablename__ = "roles"
    
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Many-to-many relationship with users
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class UserRole(BaseModel):
    """Association table for user-role many-to-many relationship"""
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class Session(BaseModel):
    """Session model for managing user sessions"""
    __tablename__ = "sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="sessions")


class RefreshToken(BaseModel):
    """Refresh token model for token refresh functionality"""
    __tablename__ = "refresh_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="refresh_tokens")


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


class Report(BaseModel):
    """Report model for user complaints and issues"""
    __tablename__ = "reports"
    
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="open", nullable=False)  # open, in_progress, resolved
    comment = Column(Text, nullable=True)  # Superuser comment
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports")
    resolver = relationship("User", foreign_keys=[resolved_by])