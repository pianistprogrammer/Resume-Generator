#!/usr/bin/env python3
"""Test script for resume generation with LMStudio."""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.models import Resume, ResumeContent
from app.database import connect_to_mongo
from datetime import datetime


async def test_resume_generation():
    """Test complete resume generation flow."""
    print("=" * 60)
    print("JobAlert AI - Resume Generation Test")
    print("=" * 60)
    print()

    # Initialize database
    print("[1/5] Connecting to database...")
    await connect_to_mongo()
    print("✓ Connected\n")

    # Initialize LLM service
    print("[2/5] Initializing LLM service...")
    llm = LLMService()
    provider_info = llm.get_provider_info()
    print(f"✓ Using: {provider_info['provider']} - {provider_info['model']}\n")

    # Sample user profile and job description
    print("[3/5] Preparing test data...")
    user_profile = {
        "full_name": "Alex Johnson",
        "email": "alex.johnson@email.com",
        "phone": "(555) 123-4567",
        "location": "San Francisco, CA",
        "linkedin_url": "linkedin.com/in/alexjohnson",
        "current_title": "Senior Full Stack Developer",
        "years_of_experience": 7,
        "summary": "Experienced full-stack developer with 7 years building scalable web applications using modern frameworks.",
        "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker", "AWS", "TypeScript", "FastAPI", "REST APIs"],
        "experience": [
            {
                "title": "Senior Full Stack Developer",
                "company": "TechCorp Inc",
                "start_date": "Jan 2021",
                "end_date": "Present",
                "location": "San Francisco, CA",
                "responsibilities": [
                    "Led development of microservices architecture serving 1M+ users",
                    "Built RESTful APIs with FastAPI and integrated with React frontend",
                    "Reduced API response time by 40% through optimization",
                    "Mentored 3 junior developers on best practices"
                ]
            },
            {
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "start_date": "Mar 2018",
                "end_date": "Dec 2020",
                "location": "Remote",
                "responsibilities": [
                    "Developed customer-facing web application with React and Node.js",
                    "Implemented CI/CD pipeline using GitHub Actions and Docker",
                    "Collaborated with design team on responsive UI/UX improvements"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "University of California, Berkeley",
                "graduation_date": "2017"
            }
        ]
    }

    job_description = """
    Senior Software Engineer - Full Stack

    We're looking for an experienced full-stack engineer to join our team building the next generation of our platform.

    Requirements:
    - 5+ years of professional software development experience
    - Strong proficiency in Python and JavaScript/TypeScript
    - Experience with modern frameworks (React, FastAPI, or similar)
    - Database design and optimization skills
    - Cloud platform experience (AWS, GCP, or Azure)
    - Strong communication and collaboration skills

    Responsibilities:
    - Design and implement scalable backend services
    - Build responsive frontend applications
    - Work with product team to define technical requirements
    - Mentor junior engineers and conduct code reviews
    - Participate in architectural decisions
    """

    print("✓ Test data prepared\n")

    # Generate resume using LLM
    print("[4/5] Generating tailored resume with AI...")
    print("(This may take 30-60 seconds...)\n")

    system_prompt = """You are an expert resume writer. Generate a professional, ATS-optimized resume in JSON format.
Tailor the resume to match the job description while highlighting relevant experience and skills from the user's profile.

Return ONLY valid JSON in this exact format:
{
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "linkedin_url": "string",
  "summary": "2-3 sentence professional summary tailored to the job",
  "skills": ["skill1", "skill2", ...],
  "experience": [
    {
      "title": "string",
      "company": "string",
      "start_date": "string",
      "end_date": "string",
      "location": "string",
      "responsibilities": ["bullet1", "bullet2", ...]
    }
  ],
  "education": [
    {
      "degree": "string",
      "field": "string",
      "institution": "string",
      "graduation_date": "string"
    }
  ]
}"""

    prompt = f"""User Profile:
{json.dumps(user_profile, indent=2)}

Job Description:
{job_description}

Generate a tailored resume that emphasizes relevant skills and experience for this specific role."""

    try:
        response_text, usage = await llm.generate_completion(prompt, system_prompt)

        print(f"✓ AI response received")
        print(f"  Response type: {type(response_text)}")
        print(f"  Tokens used: {usage.get('total_tokens', 'N/A')}\n")

        # Debug: Print first 200 characters
        response_preview = str(response_text)[:200] if response_text else "Empty"
        print(f"  Response preview: {response_preview}...\n")

        # Parse JSON response
        resume_data = llm.parse_json_response(response_text)

        # Create Resume document
        content = ResumeContent(**resume_data)
        resume = Resume(
            user_id="test_user_id",
            job_id="test_job_id",
            match_id="test_match_id",
            content=content,
            ats_score=85
        )

        print("✓ Resume data parsed successfully\n")

        # Generate PDF
        print("[5/5] Generating PDF...")
        pdf_bytes = PDFService.generate_pdf(resume, is_free_user=False)  # Test as paid user

        # Save PDF
        output_path = Path("test_resume.pdf")
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

        print(f"✓ PDF generated: {output_path.absolute()}")
        print(f"  File size: {len(pdf_bytes) / 1024:.1f} KB")
        print(f"  No footer (paid user version)\n")

        # Print summary
        print("=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        print()
        print("Resume Summary:")
        print(f"  Name: {content.full_name}")
        print(f"  Skills: {len(content.skills)} skills")
        print(f"  Experience: {len(content.experience)} positions")
        print(f"  Education: {len(content.education)} degrees")
        print()
        print(f"📄 Open the PDF: {output_path.absolute()}")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_resume_generation())
    sys.exit(0 if success else 1)
