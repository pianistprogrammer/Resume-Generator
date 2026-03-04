"""Job controller with FastAPI endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

from app.controllers.auth_controller import get_current_user
from app.middlewares.auth_middleware import get_current_user
from app.services.job_service import JobService
from app.schemas.user import User, MatchStatus
from app.models.response import ApiResponse


# Request Models
class IngestUrlRequest(BaseModel):
    url: HttpUrl


class UpdateMatchStatusRequest(BaseModel):
    status: MatchStatus


# Response Models
class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    description: str
    apply_url: str
    location: Optional[str]
    remote: bool
    salary_min: Optional[int]
    salary_max: Optional[int]
    experience_level: Optional[str]
    source: str
    ats_platform: Optional[str]
    extracted_skills: List[str]
    ingested_at: str


class MatchResponse(BaseModel):
    id: str
    overall_score: float
    score_breakdown: dict
    status: str
    job: JobResponse
    created_at: str
    notified_at: Optional[str]
    viewed_at: Optional[str]


class DashboardStatsResponse(BaseModel):
    total_matches: int
    new_matches: int
    applied_count: int
    average_score: float


# Router
router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 20,
    company: Optional[str] = None,
    remote: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all jobs with optional filters."""
    jobs = await JobService.get_jobs(
        skip=skip,
        limit=limit,
        company=company,
        remote=remote,
        search=search
    )

    return [
        {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "apply_url": job.apply_url,
            "location": job.location,
            "remote": job.remote,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "experience_level": job.experience_level,
            "source": job.source,
            "ats_platform": job.ats_platform,
            "extracted_skills": job.extracted_skills,
            "ingested_at": job.ingested_at.isoformat()
        }
        for job in jobs
    ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific job by ID."""
    job = await JobService.get_job_by_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return {
        "id": str(job.id),
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "apply_url": job.apply_url,
        "location": job.location,
        "remote": job.remote,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "experience_level": job.experience_level,
        "source": job.source,
        "ats_platform": job.ats_platform,
        "extracted_skills": job.extracted_skills,
        "ingested_at": job.ingested_at.isoformat()
    }


@router.get("/my/matches", response_model=ApiResponse[List[MatchResponse]])
async def get_my_matches(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    min_score: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    """Get current user's job matches."""
    matches = await JobService.get_user_matches(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        min_score=min_score
    )

    data = [
        {
            "id": str(item["match"].id),
            "overall_score": item["match"].overall_score,
            "score_breakdown": {
                "title_score": item["match"].score_breakdown.title_score,
                "skills_score": item["match"].score_breakdown.skills_score,
                "location_score": item["match"].score_breakdown.location_score,
                "experience_score": item["match"].score_breakdown.experience_score,
                "keyword_score": item["match"].score_breakdown.keyword_score,
                "salary_score": item["match"].score_breakdown.salary_score,
                "matched_skills": item["match"].score_breakdown.matched_skills,
                "matched_keywords": item["match"].score_breakdown.matched_keywords,
            },
            "status": item["match"].status,
            "job": {
                "id": str(item["job"].id),
                "title": item["job"].title,
                "company": item["job"].company,
                "description": item["job"].description,
                "apply_url": item["job"].apply_url,
                "location": item["job"].location,
                "remote": item["job"].remote,
                "salary_min": item["job"].salary_min,
                "salary_max": item["job"].salary_max,
                "experience_level": item["job"].experience_level,
                "source": item["job"].source,
                "ats_platform": item["job"].ats_platform,
                "extracted_skills": item["job"].extracted_skills,
                "ingested_at": item["job"].ingested_at.isoformat()
            },
            "created_at": item["match"].created_at.isoformat(),
            "notified_at": item["match"].notified_at.isoformat() if item["match"].notified_at else None,
            "viewed_at": item["match"].viewed_at.isoformat() if item["match"].viewed_at else None
        }
        for item in matches
    ]

    return ApiResponse(
        success=True,
        msg="Matches retrieved",
        data=data
    )


@router.get("/my/matches/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific match by ID."""
    match = await JobService.get_match_by_id(match_id, str(current_user.id))

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    job = await JobService.get_job_by_id(match.job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated job not found"
        )

    return {
        "id": str(match.id),
        "overall_score": match.overall_score,
        "score_breakdown": match.score_breakdown.model_dump(),
        "status": match.status,
        "job": {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "apply_url": job.apply_url,
            "location": job.location,
            "remote": job.remote,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "experience_level": job.experience_level,
            "source": job.source,
            "ats_platform": job.ats_platform,
            "extracted_skills": job.extracted_skills,
            "ingested_at": job.ingested_at.isoformat()
        },
        "created_at": match.created_at.isoformat(),
        "notified_at": match.notified_at.isoformat() if match.notified_at else None,
        "viewed_at": match.viewed_at.isoformat() if match.viewed_at else None
    }


@router.patch("/my/matches/{match_id}/status")
async def update_match_status(
    match_id: str,
    request: UpdateMatchStatusRequest,
    current_user: User = Depends(get_current_user)
):
    """Update match status."""
    match = await JobService.update_match_status(
        match_id=match_id,
        user_id=str(current_user.id),
        new_status=request.status
    )

    return {
        "id": str(match.id),
        "status": match.status,
        "updated_at": match.updated_at.isoformat()
    }


@router.get("/my/dashboard/stats", response_model=ApiResponse[DashboardStatsResponse])
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Get dashboard statistics."""
    stats = await JobService.get_dashboard_stats(str(current_user.id))
    return ApiResponse(
        success=True,
        msg="Dashboard stats retrieved",
        data=stats
    )


@router.post("/ingest-url", status_code=status.HTTP_202_ACCEPTED)
async def ingest_url(
    request: IngestUrlRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Queue a URL for job ingestion."""
    # TODO: Implement URL ingestion via Celery task
    # background_tasks.add_task(ingest_url_task, str(request.url), str(current_user.id))

    return {
        "message": "URL queued for processing",
        "url": str(request.url)
    }
