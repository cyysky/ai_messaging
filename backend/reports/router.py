import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.config import get_db
from db.models import User, Report
from auth.schemas import (
    ReportCreate, ReportUpdate, ReportResponse, ReportListResponse, ReportCommentRequest
)
from auth.utils import get_current_user, require_superuser

router = APIRouter(prefix="/reports", tags=["Reports"])

# Reports module logger
reports_logger = logging.getLogger("reports")


# ==================== USER REPORT ENDPOINTS ====================

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new report (any authenticated user)"""
    report = Report(
        reporter_id=current_user.id,
        title=report_data.title,
        content=report_data.content,
        status="open"
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    reports_logger.info(f"Report created by user {current_user.username}: {report.id}")
    
    return report


@router.get("", response_model=list[ReportListResponse])
async def get_my_reports(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports created by the current user"""
    query = db.query(Report).filter(Report.reporter_id == current_user.id)
    
    if status_filter:
        query = query.filter(Report.status == status_filter)
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    result = []
    for report in reports:
        resolver = db.query(User).filter(User.id == report.resolved_by).first() if report.resolved_by else None
        
        result.append(ReportListResponse(
            id=report.id,
            reporter_id=report.reporter_id,
            reporter_username=current_user.username,
            title=report.title,
            content=report.content,
            status=report.status,
            comment=report.comment,
            resolved_at=report.resolved_at,
            resolved_by=report.resolved_by,
            resolver_username=resolver.username if resolver else None,
            created_at=report.created_at,
            updated_at=report.updated_at
        ))
    
    return result


@router.get("/{report_id}", response_model=ReportListResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report (only if created by current user or is superuser)"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if user is the reporter or superuser
    if report.reporter_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this report"
        )
    
    reporter = db.query(User).filter(User.id == report.reporter_id).first()
    resolver = db.query(User).filter(User.id == report.resolved_by).first() if report.resolved_by else None
    
    return ReportListResponse(
        id=report.id,
        reporter_id=report.reporter_id,
        reporter_username=reporter.username if reporter else None,
        title=report.title,
        content=report.content,
        status=report.status,
        comment=report.comment,
        resolved_at=report.resolved_at,
        resolved_by=report.resolved_by,
        resolver_username=resolver.username if resolver else None,
        created_at=report.created_at,
        updated_at=report.updated_at
    )


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a report (only if created by current user and status is open)"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.reporter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this report"
        )
    
    if report.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a report that is not in open status"
        )
    
    if report_data.title is not None:
        report.title = report_data.title
    if report_data.content is not None:
        report.content = report_data.content
    
    db.commit()
    db.refresh(report)
    
    reports_logger.info(f"Report {report.id} updated by user {current_user.username}")
    
    return report


# ==================== SUPERUSER REPORT ENDPOINTS ====================

@router.get("/admin/all", response_model=list[ReportListResponse])
async def get_all_reports(
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Get all reports (superuser only)"""
    query = db.query(Report)
    
    if status_filter:
        query = query.filter(Report.status == status_filter)
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    result = []
    for report in reports:
        reporter = db.query(User).filter(User.id == report.reporter_id).first()
        resolver = db.query(User).filter(User.id == report.resolved_by).first() if report.resolved_by else None
        
        result.append(ReportListResponse(
            id=report.id,
            reporter_id=report.reporter_id,
            reporter_username=reporter.username if reporter else None,
            title=report.title,
            content=report.content,
            status=report.status,
            comment=report.comment,
            resolved_at=report.resolved_at,
            resolved_by=report.resolved_by,
            resolver_username=resolver.username if resolver else None,
            created_at=report.created_at,
            updated_at=report.updated_at
        ))
    
    return result


@router.post("/{report_id}/comment", response_model=ReportResponse)
async def add_report_comment(
    report_id: int,
    comment_data: ReportCommentRequest,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Add a comment to a report and optionally change status (superuser only)"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report.comment = comment_data.comment
    
    if comment_data.status:
        valid_statuses = ["open", "in_progress", "resolved"]
        if comment_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        report.status = comment_data.status
        
        if comment_data.status == "resolved":
            report.resolved_at = datetime.utcnow()
            report.resolved_by = current_user.id
    
    db.commit()
    db.refresh(report)
    
    reports_logger.info(f"Report {report_id} commented by superuser {current_user.username}, status: {report.status}")
    
    return report


@router.put("/{report_id}/resolve", response_model=ReportResponse)
async def resolve_report(
    report_id: int,
    comment_data: ReportCommentRequest,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """Resolve a report with a comment (superuser only)"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report.status = "resolved"
    report.resolved_at = datetime.utcnow()
    report.resolved_by = current_user.id
    
    if comment_data.comment:
        report.comment = comment_data.comment
    
    db.commit()
    db.refresh(report)
    
    reports_logger.info(f"Report {report_id} resolved by superuser {current_user.username}")
    
    return report