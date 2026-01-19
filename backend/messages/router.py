from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.config import get_db
from db.models import User, Message
from auth.schemas import MessageResponse, MessageCreate, MessageUpdate
from auth.utils import get_current_user
from init_logs import messages_logger

router = APIRouter(prefix="/messages", tags=["Messages"])


# ==================== MESSAGES CRUD ====================

@router.get("", response_model=list[MessageResponse])
async def list_messages(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all messages for the current user (sent or received)"""
    query = db.query(Message).filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    )
    
    if unread_only:
        query = query.filter(
            Message.recipient_id == current_user.id,
            Message.is_read == False
        )
    
    messages = query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    return messages[::-1]  # Reverse to get chronological order


@router.get("/sent", response_model=list[MessageResponse])
async def list_sent_messages(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all messages sent by the current user"""
    messages = db.query(Message).filter(
        Message.sender_id == current_user.id
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    return messages[::-1]


@router.get("/received", response_model=list[MessageResponse])
async def list_received_messages(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all messages received by the current user"""
    query = db.query(Message).filter(
        Message.recipient_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Message.is_read == False)
    
    messages = query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    return messages[::-1]


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific message by ID"""
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user has access to this message
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this message"
        )
    
    return message


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a new message"""
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )

    # Generate conversation_id if not provided
    conversation_id = message_data.conversation_id
    if not conversation_id:
        # Create a consistent conversation ID based on both user IDs
        user_ids = sorted([current_user.id, message_data.recipient_id])
        conversation_id = f"conv_{user_ids[0]}_{user_ids[1]}"
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        content=message_data.content,
        conversation_id=conversation_id
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    messages_logger.info(f"Message {message.id} sent from user {current_user.id} to user {message_data.recipient_id}")
    
    return message


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a message (only sender can update, only content can be changed)"""
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Only sender can update the message
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the sender can update this message"
        )
    
    # Update fields
    if message_data.content is not None:
        message.content = message_data.content
    
    db.commit()
    db.refresh(message)
    
    return message


@router.put("/{message_id}/read")
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a message as read"""
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Only recipient can mark as read
    if message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recipient can mark this message as read"
        )
    
    message.is_read = True
    db.commit()
    
    return {"message": "Message marked as read"}


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Only sender or recipient can delete the message
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this message"
        )
    
    db.delete(message)
    db.commit()
    
    messages_logger.info(f"Message {message_id} deleted by user {current_user.id}")
    
    return {"message": "Message deleted successfully"}


@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread messages"""
    count = db.query(func.count(Message.id)).filter(
        Message.recipient_id == current_user.id,
        Message.is_read == False
    ).scalar()
    
    return {"unread_count": count or 0}


@router.put("/read-all", response_model=dict)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all received messages as read"""
    db.query(Message).filter(
        Message.recipient_id == current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "All messages marked as read"}