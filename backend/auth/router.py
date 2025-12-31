import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from db.config import get_db
from db.models import User, Session as UserSession, RefreshToken, Role, UserRole, Message
from auth.schemas import (
    UserCreate, UserUpdate, UserResponse, LoginRequest, Token,
    ChangePasswordRequest, SessionResponse, RoleCreate, RoleResponse,
    UserRoleAssign, RefreshTokenRequest, MessageCreate, MessageResponse,
    ConversationResponse, AuthResponse
)
from auth.utils import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    decode_token, get_current_user, require_superuser, generate_session_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Auth module logger
auth_logger = logging.getLogger("auth")


# ==================== AUTHENTICATION ====================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        auth_logger.warning(f"Registration failed: username '{user_data.username}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        auth_logger.warning(f"Registration failed: email '{user_data.email}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        auth_logger.info(f"User registered successfully: {user_data.username} (email: {user_data.email})")
    except IntegrityError:
        db.rollback()
        auth_logger.error(f"Registration failed: integrity error for username '{user_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    return user


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login and get access/refresh tokens"""
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        auth_logger.warning(f"Login failed: incorrect credentials for username '{login_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        auth_logger.warning(f"Login failed: user '{login_data.username}' is disabled")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled"
        )
    
    # Create tokens
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)
    
    # Store refresh token in database
    refresh_token_db = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token_db)
    
    # Create session
    client_host = request.client.host if request.client else None
    user_session = UserSession(
        user_id=user.id,
        session_token=generate_session_token(),
        device_info=request.headers.get("user-agent", "Unknown")[:255],
        ip_address=client_host,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(user_session)
    db.commit()
    
    auth_logger.info(f"User logged in successfully: {login_data.username} (IP: {client_host})")
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = decode_token(refresh_data.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    username: str = payload.get("username")
    
    # Check if refresh token exists and is valid
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_data.refresh_token,
        RefreshToken.is_used == False
    ).first()
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or already used",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if stored_token.expires_at < datetime.utcnow():
        db.delete(stored_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mark old token as used
    stored_token.is_used = True
    db.commit()
    
    # Create new tokens
    access_token = create_access_token(user_id, username)
    refresh_token = create_refresh_token(user_id, username)
    
    # Store new refresh token
    new_refresh_token_db = RefreshToken(
        user_id=user_id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(new_refresh_token_db)
    db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(
    refresh_data: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout and invalidate refresh token"""
    if refresh_data and refresh_data.refresh_token:
        # Invalidate the refresh token
        token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_data.refresh_token,
            RefreshToken.user_id == current_user.id
        ).first()
        if token:
            token.is_used = True
            db.commit()
    
    auth_logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices"""
    # Invalidate all refresh tokens
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).delete()
    
    # Deactivate all sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).update(
        {"is_active": False}
    )
    
    db.commit()
    
    auth_logger.info(f"User logged out from all devices: {current_user.username}")
    
    return {"message": "Successfully logged out from all devices"}


# ==================== USER MANAGEMENT ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.bio is not None:
        current_user.bio = user_data.bio
    if user_data.phone_number is not None:
        current_user.phone_number = user_data.phone_number
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.put("/me/password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


# ==================== USER CRUD (Admin) ====================

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """List all users (superuser only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Get a specific user (superuser only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Create a new user (superuser only)"""
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Delete a user (superuser only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.put("/users/{user_id}/disable")
async def disable_user(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Disable a user (superuser only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": "User disabled successfully"}


@router.put("/users/{user_id}/enable")
async def enable_user(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Enable a user (superuser only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": "User enabled successfully"}


@router.put("/users/{user_id}/superuser")
async def toggle_superuser(
    user_id: int,
    is_superuser: bool,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Toggle superuser status (superuser only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own superuser status"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_superuser = is_superuser
    db.commit()
    
    return {"message": f"User superuser status set to {is_superuser}"}


# ==================== SESSIONS ====================

@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all sessions for current user"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).all()
    return sessions


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific session"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}


# ==================== ROLES ====================

@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """List all roles (superuser only)"""
    roles = db.query(Role).all()
    return roles


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Create a new role (superuser only)"""
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    role = Role(
        name=role_data.name,
        description=role_data.description
    )
    
    db.add(role)
    db.commit()
    db.refresh(role)
    
    return role


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Delete a role (superuser only)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    db.delete(role)
    db.commit()
    
    return {"message": "Role deleted successfully"}


@router.put("/users/{user_id}/roles")
async def assign_roles(
    user_id: int,
    role_data: UserRoleAssign,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Assign roles to a user (superuser only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove existing roles
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    
    # Add new roles
    for role_id in role_data.role_ids:
        role = db.query(Role).filter(Role.id == role_id).first()
        if role:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)
    
    db.commit()
    
    return {"message": "Roles assigned successfully"}


@router.get("/users/{user_id}/roles", response_model=list[RoleResponse])
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Get roles for a specific user (superuser only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    roles = [ur.role for ur in user_roles if ur.role]
    
    return roles


# ==================== CONVERSATIONS ====================

@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    # Get all unique conversation IDs where user is sender or recipient
    conversations = db.query(
        Message.conversation_id,
        func.max(Message.created_at).label('last_message_at')
    ).filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).group_by(Message.conversation_id).all()
    
    result = []
    for conv in conversations:
        # Get the last message in this conversation
        last_msg = db.query(Message).filter(
            Message.conversation_id == conv.conversation_id
        ).order_by(Message.created_at.desc()).first()
        
        if not last_msg:
            continue
        
        # Determine the other user
        if last_msg.sender_id == current_user.id:
            other_user_id = last_msg.recipient_id
        else:
            other_user_id = last_msg.sender_id
        
        other_user = db.query(User).filter(User.id == other_user_id).first()
        other_user_name = other_user.username if other_user else "Unknown"
        
        # Count unread messages
        unread_count = db.query(Message).filter(
            Message.conversation_id == conv.conversation_id,
            Message.recipient_id == current_user.id,
            Message.is_read == False
        ).count()
        
        result.append(ConversationResponse(
            conversation_id=conv.conversation_id,
            other_user_id=other_user_id,
            other_user_name=other_user_name,
            last_message=last_msg.content[:100] if last_msg.content else "",
            last_message_at=last_msg.created_at,
            unread_count=unread_count
        ))
    
    # Sort by last message time, most recent first
    result.sort(key=lambda x: x.last_message_at, reverse=True)
    return result


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific conversation"""
    # Verify user is part of this conversation
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        ((Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    return messages[::-1]  # Reverse to get chronological order


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a conversation"""
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        content=message_data.content,
        conversation_id=conversation_id
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


@router.put("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all messages in a conversation as read"""
    db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.recipient_id == current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "Conversation marked as read"}