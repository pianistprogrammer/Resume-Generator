"""Admin controller for admin endpoints."""

from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.middlewares.admin_middleware import get_current_admin
from app.schemas.user import User
from app.services.admin_service import AdminService
from app.models.response import ApiResponse
from pydantic import BaseModel


router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ===== Request Models =====
class CreateFeedRequest(BaseModel):
    name: str
    url: str
    feed_type: str  # "rss", "greenhouse", "lever"
    company_token: Optional[str] = None


class UpdateFeedRequest(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    feed_type: Optional[str] = None
    company_token: Optional[str] = None


class UpdateCreditsRequest(BaseModel):
    credits: int


# ===== Dashboard =====
@router.get("/dashboard", response_model=ApiResponse)
async def get_admin_dashboard(admin: User = Depends(get_current_admin)):
    """Get admin dashboard statistics."""
    stats = await AdminService.get_dashboard_stats()
    return ApiResponse(
        success=True,
        msg="Dashboard stats retrieved",
        data=stats
    )


# ===== User Management =====
@router.get("/users", response_model=ApiResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    is_admin: Optional[bool] = None,
    admin: User = Depends(get_current_admin)
):
    """Get all users with pagination and filtering."""
    users = await AdminService.get_all_users(skip, limit, search, is_admin)
    return ApiResponse(
        success=True,
        msg="Users retrieved",
        data={"users": users}
    )


@router.get("/users/{user_id}", response_model=ApiResponse)
async def get_user(
    user_id: str,
    admin: User = Depends(get_current_admin)
):
    """Get detailed user information."""
    user = await AdminService.get_user_details(user_id)
    return ApiResponse(
        success=True,
        msg="User details retrieved",
        data=user
    )


@router.patch("/users/{user_id}/credits", response_model=ApiResponse)
async def update_user_credits(
    user_id: str,
    request: UpdateCreditsRequest,
    admin: User = Depends(get_current_admin)
):
    """Update user's credit balance."""
    user = await AdminService.update_user_credits(user_id, request.credits)
    return ApiResponse(
        success=True,
        msg="Credits updated",
        data=user
    )


@router.patch("/users/{user_id}/toggle-admin", response_model=ApiResponse)
async def toggle_user_admin(
    user_id: str,
    admin: User = Depends(get_current_admin)
):
    """Toggle user's admin status."""
    user = await AdminService.toggle_user_admin(user_id)
    return ApiResponse(
        success=True,
        msg="Admin status toggled",
        data=user
    )


@router.patch("/users/{user_id}/toggle-active", response_model=ApiResponse)
async def toggle_user_active(
    user_id: str,
    admin: User = Depends(get_current_admin)
):
    """Toggle user's active status."""
    user = await AdminService.toggle_user_active(user_id)
    return ApiResponse(
        success=True,
        msg="Active status toggled",
        data=user
    )


# ===== Feed Source Management =====
@router.get("/feeds", response_model=ApiResponse)
async def get_feeds(
    include_inactive: bool = False,
    admin: User = Depends(get_current_admin)
):
    """Get all feed sources."""
    feeds = await AdminService.get_all_feeds(include_inactive)
    return ApiResponse(
        success=True,
        msg="Feeds retrieved",
        data={"feeds": feeds}
    )


@router.post("/feeds", response_model=ApiResponse)
async def create_feed(
    request: CreateFeedRequest,
    admin: User = Depends(get_current_admin)
):
    """Create a new feed source."""
    feed = await AdminService.create_feed(
        name=request.name,
        url=request.url,
        feed_type=request.feed_type,
        company_token=request.company_token,
        admin_id=str(admin.id)
    )
    return ApiResponse(
        success=True,
        msg="Feed created successfully",
        data=feed
    )


@router.patch("/feeds/{feed_id}", response_model=ApiResponse)
async def update_feed(
    feed_id: str,
    request: UpdateFeedRequest,
    admin: User = Depends(get_current_admin)
):
    """Update a feed source."""
    feed = await AdminService.update_feed(
        feed_id=feed_id,
        name=request.name,
        url=request.url,
        feed_type=request.feed_type,
        company_token=request.company_token
    )
    return ApiResponse(
        success=True,
        msg="Feed updated successfully",
        data=feed
    )


@router.patch("/feeds/{feed_id}/toggle", response_model=ApiResponse)
async def toggle_feed(
    feed_id: str,
    admin: User = Depends(get_current_admin)
):
    """Toggle feed's active status."""
    feed = await AdminService.toggle_feed_active(feed_id)
    return ApiResponse(
        success=True,
        msg="Feed status toggled",
        data=feed
    )


@router.delete("/feeds/{feed_id}", response_model=ApiResponse)
async def delete_feed(
    feed_id: str,
    admin: User = Depends(get_current_admin)
):
    """Delete a feed source."""
    await AdminService.delete_feed(feed_id)
    return ApiResponse(
        success=True,
        msg="Feed deleted successfully",
        data=None
    )


# ===== Job Management =====
@router.get("/jobs", response_model=ApiResponse)
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    source: Optional[str] = None,
    admin: User = Depends(get_current_admin)
):
    """Get all jobs with pagination and filtering."""
    jobs = await AdminService.get_all_jobs(skip, limit, search, source)
    return ApiResponse(
        success=True,
        msg="Jobs retrieved",
        data={"jobs": jobs}
    )


@router.delete("/jobs/{job_id}", response_model=ApiResponse)
async def delete_job(
    job_id: str,
    admin: User = Depends(get_current_admin)
):
    """Delete a job posting."""
    await AdminService.delete_job(job_id)
    return ApiResponse(
        success=True,
        msg="Job deleted successfully",
        data=None
    )


# ===== Resume Management =====
@router.get("/resumes", response_model=ApiResponse)
async def get_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = None,
    admin: User = Depends(get_current_admin)
):
    """Get all resumes with pagination and filtering."""
    resumes = await AdminService.get_all_resumes(skip, limit, user_id)
    return ApiResponse(
        success=True,
        msg="Resumes retrieved",
        data={"resumes": resumes}
    )
