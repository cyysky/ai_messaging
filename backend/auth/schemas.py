from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str


# Auth schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: int
    username: str
    exp: datetime


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Session schemas
class SessionResponse(BaseModel):
    id: int
    user_id: int
    device_info: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Role schemas
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    role_ids: list[int]


# Password schemas
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


# Message schemas
class MessageCreate(BaseModel):
    recipient_id: int
    content: str
    conversation_id: Optional[str] = None


class MessageUpdate(BaseModel):
    content: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    is_read: bool
    conversation_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    conversation_id: str
    other_user_id: int
    other_user_name: str
    last_message: str
    last_message_at: datetime
    unread_count: int


class Message(BaseModel):
    detail: str