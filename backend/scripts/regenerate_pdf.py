"""Script to regenerate PDF for an existing resume."""

import asyncio
from mongoengine import connect
from app.schemas import Resume, User
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService
from app.config import settings

connect(host=settings.mongodb_url)


async def regenerate_pdf(resume_id: str):
    """Regenerate PDF for a resume."""

    # Get resume
    resume = Resume.objects(id=resume_id).first()
    if not resume:
        print(f"Resume {resume_id} not found")
        return

    print(f"Found resume: {resume.id}")
    print(f"User ID: {resume.user_id}")
    print(f"Current PDF URL: {resume.pdf_url}")

    # Get user
    user = User.objects(id=resume.user_id).first()
    if not user:
        print(f"User {resume.user_id} not found")
        return

    # Initialize services
    pdf_service = PDFService()
    storage_service = StorageService()

    print("\nGenerating PDF...")

    # Generate PDF
    loop = asyncio.get_event_loop()

    def _generate_and_upload():
        # Generate PDF bytes
        pdf_bytes = pdf_service.generate_pdf(resume, is_free_user=True)
        print(f"PDF generated: {len(pdf_bytes)} bytes")

        # Upload to S3
        pdf_url = storage_service.upload_pdf(
            file_content=pdf_bytes,
            user_id=str(user.id),
            resume_id=str(resume.id)
        )
        print(f"Uploaded to: {pdf_url}")

        # Update resume
        resume.pdf_url = pdf_url
        resume.save()

        return pdf_url

    pdf_url = await loop.run_in_executor(None, _generate_and_upload)

    print(f"\n✅ PDF regenerated successfully!")
    print(f"PDF URL: {pdf_url}")
    print(f"\nView resume at: http://localhost:3000/resume/{resume.id}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scripts/regenerate_pdf.py <resume_id>")

        # Show available resumes
        resumes = Resume.objects()
        if resumes.count() > 0:
            print(f"\nAvailable resumes ({resumes.count()}):")
            for resume in resumes:
                print(f"  - {resume.id} (User: {resume.user_id}, PDF: {'Yes' if resume.pdf_url else 'No'})")
        else:
            print("\nNo resumes found in database")
        sys.exit(1)

    resume_id = sys.argv[1]
    asyncio.run(regenerate_pdf(resume_id))
