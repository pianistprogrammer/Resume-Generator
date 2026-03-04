"""Resume controller with FastAPI endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.middlewares.auth_middleware import get_current_user
from app.services.resume_service import ResumeService
from app.schemas.user import User
from app.models.response import ApiResponse


# Response Models
class ResumeGenerateResponse(BaseModel):
    message: str
    match_id: str
    resume_id: Optional[str]
    status: str


class ResumeContentResponse(BaseModel):
    id: str
    match_id: str
    job_id: str
    content: dict
    pdf_url: Optional[str]
    generation_time_seconds: Optional[float]
    created_at: str


# Router
router = APIRouter(prefix="/resumes", tags=["Resumes"])

# Initialize service
resume_service = ResumeService()


@router.post("/generate/{match_id}", response_model=ApiResponse[ResumeGenerateResponse], status_code=status.HTTP_202_ACCEPTED)
async def generate_resume(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger resume generation for a match.
    Deducts 1 credit and queues generation task.
    """
    result = await resume_service.generate_on_demand(match_id, str(current_user.id))
    return ApiResponse(
        success=True,
        msg="Resume generation started",
        data=result
    )


@router.get("/{resume_id}", response_model=ApiResponse[ResumeContentResponse])
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get resume content by ID."""
    resume = await ResumeService.get_resume_by_id(resume_id, str(current_user.id))

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Refresh presigned URL if PDF exists
    pdf_url = await ResumeService.refresh_pdf_url(resume)

    data = {
        "id": str(resume.id),
        "match_id": resume.match_id,
        "job_id": resume.job_id,
        "content": resume.content.to_mongo().to_dict() if hasattr(resume.content, 'to_mongo') else {},
        "pdf_url": pdf_url,  # Use refreshed URL
        "generation_time_seconds": resume.generation_time_seconds,
        "created_at": resume.created_at.isoformat()
    }

    return ApiResponse(
        success=True,
        msg="Resume retrieved",
        data=data
    )


@router.get("/match/{match_id}", response_model=ApiResponse[ResumeContentResponse])
async def get_resume_by_match(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get resume for a specific match."""
    resume = await ResumeService.get_resume_by_match(match_id, str(current_user.id))

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found for this match"
        )

    # Refresh presigned URL if PDF exists
    pdf_url = await ResumeService.refresh_pdf_url(resume)

    data = {
        "id": str(resume.id),
        "match_id": resume.match_id,
        "job_id": resume.job_id,
        "content": resume.content.to_mongo().to_dict() if hasattr(resume.content, 'to_mongo') else {},
        "pdf_url": pdf_url,  # Use refreshed URL
        "generation_time_seconds": resume.generation_time_seconds,
        "created_at": resume.created_at.isoformat()
    }

    return ApiResponse(
        success=True,
        msg="Resume retrieved",
        data=data
    )


@router.post("/{resume_id}/regenerate-pdf", response_model=ApiResponse[dict])
async def regenerate_pdf(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Regenerate PDF for an existing resume."""
    pdf_url = await ResumeService.regenerate_pdf(resume_id, str(current_user.id))

    if not pdf_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate PDF"
        )

    return ApiResponse(
        success=True,
        msg="PDF regenerated successfully",
        data={"pdf_url": pdf_url}
    )


@router.get("/{resume_id}/pdf")
async def get_resume_pdf(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get PDF URL for resume (redirect)."""
    resume = await ResumeService.get_resume_by_id(resume_id, str(current_user.id))

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    if not resume.pdf_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not yet generated"
        )

    # Return redirect to PDF URL
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=resume.pdf_url)
