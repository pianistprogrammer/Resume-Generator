"""Resume generation service using LLM providers."""

import asyncio
import json
import time
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status

from app.schemas import (
    User, Job, Match, Resume, ResumeContent, MatchStatus,
    WorkExperience, Education, Certification
)
from app.services.profile_service import ProfileService
from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService
from app.config import settings


class ResumeService:
    """Service for AI-powered resume generation."""

    def __init__(self):
        self.llm = LLMService()
        self.pdf_service = PDFService()
        self.storage_service = StorageService()

    def _build_claude_prompt(self, user: User, job: Job) -> str:
        """Build the prompt for Claude to generate a tailored resume."""

        prompt = f"""You are an expert resume writer and ATS optimization specialist. Your task is to tailor a resume for a specific job posting.

USER PROFILE:
Name: {user.profile.full_name}
Current Title: {user.profile.current_title or 'N/A'}
Location: {user.profile.location}
Years of Experience: {user.profile.years_of_experience or 'N/A'}

Skills: {', '.join(user.profile.skills)}

Professional Summary: {user.profile.summary or 'N/A'}

Work Experience:
{self._format_work_experience(user.profile.work_experience)}

Education:
{self._format_education(user.profile.education)}

Certifications:
{self._format_certifications(user.profile.certifications)}

---

JOB POSTING:
Title: {job.title}
Company: {job.company}
Location: {job.location or 'Remote'}

Description:
{job.normalized_description or job.description}

Required Skills: {', '.join(job.extracted_skills)}

---

INSTRUCTIONS:
1. Rewrite the professional summary to emphasize experience relevant to this job
2. Reorder skills to put the most relevant ones first (matching job requirements)
3. Rewrite work experience bullets to highlight achievements relevant to this job
4. Keep all dates, companies, and titles accurate - do not fabricate
5. Optimize for ATS by naturally incorporating keywords from the job description
6. Maintain professional tone and formatting

OUTPUT FORMAT (JSON):
{{
    "summary": "Tailored professional summary (2-3 sentences)",
    "skills_reordered": ["skill1", "skill2", ...],
    "work_experience": [
        {{
            "company": "Company Name",
            "title": "Job Title",
            "location": "Location",
            "start_date": "YYYY-MM",
            "end_date": "YYYY-MM or null",
            "is_current": false,
            "bullets": ["Tailored bullet point 1", "Tailored bullet point 2", ...]
        }}
    ],
    "education": [
        {{
            "institution": "School Name",
            "degree": "Degree",
            "field": "Field of Study",
            "graduation_year": 2020
        }}
    ],
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuer",
            "issue_date": "YYYY-MM"
        }}
    ],
    "keywords_injected": ["keyword1", "keyword2", ...],
    "keywords_missing": ["missing1", "missing2", ...],
    "ats_score": 85
}}

RESPOND ONLY WITH VALID JSON. NO EXPLANATIONS OR ADDITIONAL TEXT."""

        return prompt

    @staticmethod
    def _format_work_experience(experiences: list[WorkExperience]) -> str:
        """Format work experience for prompt."""
        if not experiences:
            return "None provided"

        formatted = []
        for exp in experiences:
            bullets = '\n  - ' + '\n  - '.join(exp.bullets) if exp.bullets else ''
            formatted.append(
                f"• {exp.title} at {exp.company} ({exp.start_date} - {exp.end_date or 'Present'})\n"
                f"  Location: {exp.location or 'N/A'}{bullets}"
            )

        return '\n\n'.join(formatted)

    @staticmethod
    def _format_education(education: list[Education]) -> str:
        """Format education for prompt."""
        if not education:
            return "None provided"

        formatted = []
        for edu in education:
            formatted.append(
                f"• {edu.degree} in {edu.field or 'N/A'} from {edu.institution} "
                f"({edu.graduation_year or 'N/A'})"
            )

        return '\n'.join(formatted)

    @staticmethod
    def _format_certifications(certifications: list[Certification]) -> str:
        """Format certifications for prompt."""
        if not certifications:
            return "None provided"

        formatted = []
        for cert in certifications:
            formatted.append(f"• {cert.name} from {cert.issuer} ({cert.issue_date or 'N/A'})")

        return '\n'.join(formatted)

    async def generate_resume(self, match_id: str) -> Resume:
        """Generate a tailored resume for a match (called by Celery worker)."""
        loop = asyncio.get_event_loop()

        # Fetch match
        def _get_match():
            return Match.objects(id=match_id).first()

        match = await loop.run_in_executor(None, _get_match)
        if not match:
            raise ValueError(f"Match {match_id} not found")

        # Fetch user and job
        def _get_user_and_job():
            user = User.objects(id=match.user_id).first()
            job = Job.objects(id=match.job_id).first()
            return user, job

        user, job = await loop.run_in_executor(None, _get_user_and_job)

        if not user or not job:
            raise ValueError("User or job not found")

        # Build prompt
        prompt = self._build_claude_prompt(user, job)

        # Call LLM API
        start_time = time.time()

        try:
            response_text, usage = await self.llm.generate_completion(prompt)
            generation_time = time.time() - start_time
            tokens_used = usage.get("total_tokens", 0)

            # Parse response
            try:
                resume_data = self.llm.parse_json_response(response_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse LLM response as JSON: {e}")
                print(f"Response: {response_text}")
                raise

            # Build ResumeContent
            content = ResumeContent(
                full_name=user.profile.full_name,
                email=user.email,
                phone=user.profile.phone or "",
                location=user.profile.location or "",
                linkedin_url=user.profile.linkedin_url or "",
                portfolio_url=user.profile.portfolio_url or "",
                summary=resume_data.get("summary", ""),
                skills=resume_data.get("skills_reordered", []),
                experience=resume_data.get("work_experience", []),
                education=resume_data.get("education", []),
                certifications=resume_data.get("certifications", []),
                keywords_injected=resume_data.get("keywords_injected", []),
                keywords_missing=resume_data.get("keywords_missing", []),
                ats_score=resume_data.get("ats_score", 85.0)
            )

            # Create Resume document
            resume = Resume(
                user_id=str(user.id),
                match_id=match_id,
                job_id=str(job.id),
                content=content,
                generation_time_seconds=generation_time,
                tokens_used=tokens_used,
                ats_score=resume_data.get("ats_score", 85.0)  # Store at top level too for easier querying
            )

            def _save_resume():
                resume.save()
                return resume

            await loop.run_in_executor(None, _save_resume)

            # Generate PDF
            def _generate_and_upload_pdf():
                try:
                    print(f"Generating PDF for resume {resume.id}...")
                    # Generate PDF bytes
                    pdf_bytes = self.pdf_service.generate_pdf(resume, is_free_user=True)
                    print(f"PDF generated: {len(pdf_bytes)} bytes")

                    # Upload to S3
                    print(f"Uploading to S3...")
                    pdf_url = self.storage_service.upload_pdf(
                        file_content=pdf_bytes,
                        user_id=str(user.id),
                        resume_id=str(resume.id)
                    )
                    print(f"PDF uploaded to: {pdf_url}")

                    # Update resume with PDF URL
                    resume.pdf_url = pdf_url
                    resume.save()
                    print(f"Resume updated with PDF URL")
                    return pdf_url
                except Exception as e:
                    print(f"ERROR generating/uploading PDF: {e}")
                    import traceback
                    traceback.print_exc()
                    return None

            pdf_url = await loop.run_in_executor(None, _generate_and_upload_pdf)
            if pdf_url:
                print(f"✅ PDF generation successful: {pdf_url}")
            else:
                print(f"⚠️ PDF generation failed, but resume content saved")

            # Update match
            def _update_match():
                match.resume_id = str(resume.id)
                match.status = MatchStatus.RESUME_READY
                match.updated_at = datetime.utcnow()
                match.save()

            await loop.run_in_executor(None, _update_match)

            return resume

        except Exception as e:
            print(f"Error generating resume: {e}")
            # Update match status to indicate failure
            def _revert_match():
                match.status = MatchStatus.NEW
                match.updated_at = datetime.utcnow()
                match.save()

            await loop.run_in_executor(None, _revert_match)
            raise

    async def generate_on_demand(self, match_id: str, user_id: str) -> dict:
        """
        Controller endpoint handler for on-demand resume generation.
        Returns immediately after queueing the task.
        """
        loop = asyncio.get_event_loop()

        # Fetch match and verify ownership
        def _get_match():
            return Match.objects(id=match_id).first()

        match = await loop.run_in_executor(None, _get_match)

        if not match or match.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        # Check if resume already exists
        if match.resume_id:
            def _get_resume():
                return Resume.objects(id=match.resume_id).first()

            resume = await loop.run_in_executor(None, _get_resume)
            if resume:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Resume already generated for this match"
                )

        # Check and deduct credits
        def _get_user():
            return User.objects(id=user_id).first()

        user = await loop.run_in_executor(None, _get_user)
        if user.credits < 1:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits"
            )

        # Deduct credit
        def _deduct_credit():
            ProfileService.deduct_credit(user, 1)

        await loop.run_in_executor(None, _deduct_credit)

        # Set match status to generating
        def _update_match_status():
            match.status = MatchStatus.GENERATING
            match.updated_at = datetime.utcnow()
            match.save()

        await loop.run_in_executor(None, _update_match_status)

        # TODO: Queue Celery task for background processing
        # For now, generate synchronously (will be replaced with Celery)
        try:
            resume = await self.generate_resume(match_id)

            return {
                "message": "Resume generation started",
                "match_id": match_id,
                "resume_id": str(resume.id),
                "status": "completed"  # Will be "queued" when Celery is integrated
            }
        except Exception as e:
            # Refund credit on failure
            def _refund_credit():
                user.credits += 1
                user.save()

            await loop.run_in_executor(None, _refund_credit)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate resume: {str(e)}"
            )

    @staticmethod
    async def get_resume_by_id(resume_id: str, user_id: str) -> Optional[Resume]:
        """Get a resume by ID, ensuring it belongs to the user."""
        loop = asyncio.get_event_loop()

        def _get_resume():
            try:
                resume = Resume.objects(id=resume_id, user_id=user_id).first()
                return resume
            except Exception:
                return None

        return await loop.run_in_executor(None, _get_resume)

    @staticmethod
    async def get_resume_by_match(match_id: str, user_id: str) -> Optional[Resume]:
        """Get resume for a match."""
        loop = asyncio.get_event_loop()

        def _get_resume():
            return Resume.objects(match_id=match_id, user_id=user_id).first()

        return await loop.run_in_executor(None, _get_resume)

    @staticmethod
    async def refresh_pdf_url(resume: Resume) -> Optional[str]:
        """
        Refresh presigned URL for resume PDF if it exists.

        Args:
            resume: Resume document

        Returns:
            str: Fresh presigned URL or None if no PDF
        """
        if not resume.pdf_url:
            return None

        loop = asyncio.get_event_loop()

        def _regenerate_url():
            try:
                storage_service = StorageService()
                s3_key = storage_service.extract_s3_key_from_url(resume.pdf_url)

                if s3_key:
                    # Generate new presigned URL (valid for 7 days)
                    new_url = storage_service.generate_presigned_url(s3_key, expires_in=604800)
                    return new_url
                return None
            except Exception as e:
                print(f"Error refreshing PDF URL: {e}")
                return None

        return await loop.run_in_executor(None, _regenerate_url)

    @staticmethod
    async def regenerate_pdf(resume_id: str, user_id: str) -> Optional[str]:
        """
        Regenerate PDF for an existing resume.

        Args:
            resume_id: Resume ID
            user_id: User ID (for authorization)

        Returns:
            str: Presigned PDF URL or None if generation failed
        """
        # Get resume
        resume = await ResumeService.get_resume_by_id(resume_id, user_id)
        if not resume:
            return None

        loop = asyncio.get_event_loop()
        pdf_service = PDFService()
        storage_service = StorageService()

        def _generate_and_upload_pdf():
            try:
                print(f"Regenerating PDF for resume {resume.id}...")

                # Generate PDF
                pdf_bytes = pdf_service.generate_pdf(resume, is_free_user=True)
                print(f"PDF generated: {len(pdf_bytes)} bytes")

                # Upload to S3
                pdf_url = storage_service.upload_pdf(
                    file_content=pdf_bytes,
                    user_id=user_id,
                    resume_id=str(resume.id)
                )

                print(f"PDF uploaded successfully: {pdf_url}")

                # Update resume with new PDF URL
                resume.pdf_url = pdf_url
                resume.save()

                return pdf_url
            except Exception as e:
                print(f"ERROR regenerating PDF: {e}")
                import traceback
                traceback.print_exc()
                return None

        return await loop.run_in_executor(None, _generate_and_upload_pdf)

