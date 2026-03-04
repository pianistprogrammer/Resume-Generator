"""Celery worker configuration and task definitions."""

from celery import Celery
from celery.schedules import crontab
import asyncio

from app.config import settings


# Initialize Celery
celery_app = Celery(
    "jobalert",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "ingest-feeds-every-30-minutes": {
        "task": "app.workers.celery_worker.ingest_all_feeds_task",
        "schedule": crontab(minute=f"*/{settings.feed_refresh_minutes}"),
    },
    "send-daily-digests": {
        "task": "app.workers.celery_worker.send_daily_digests_task",
        "schedule": crontab(hour=settings.digest_hour, minute=0),
    },
    "run-matching-hourly": {
        "task": "app.workers.celery_worker.run_matching_all_task",
        "schedule": crontab(minute=0),  # Every hour
    },
}


# Helper to run async functions in Celery
def run_async(coro):
    """Run an async function in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Tasks
@celery_app.task(name="app.workers.celery_worker.ingest_all_feeds_task")
def ingest_all_feeds_task():
    """Periodic task: Ingest jobs from all RSS/XML feeds."""
    from app.services.ingestion.xml_feed_service import XMLFeedService
    from app.database import connect_to_mongo

    async def _run():
        await connect_to_mongo()
        results = await XMLFeedService.ingest_all_feeds()
        return results

    results = run_async(_run())
    return {"status": "completed", "results": results}


@celery_app.task(name="app.workers.celery_worker.ingest_url_task")
def ingest_url_task(url: str, user_id: str):
    """On-demand task: Ingest a single URL submitted by user."""
    from app.services.ingestion.url_parser_service import URLParserService
    from app.database import connect_to_mongo

    async def _run():
        await connect_to_mongo()
        result = await URLParserService.ingest_from_url(url)
        return result

    result = run_async(_run())
    return {"status": "completed", "result": result}


@celery_app.task(name="app.workers.celery_worker.generate_resume_task")
def generate_resume_task(match_id: str):
    """On-demand task: Generate resume for a match."""
    from app.services.resume_service import ResumeService
    from app.database import connect_to_mongo

    async def _run():
        await connect_to_mongo()
        service = ResumeService()
        resume = await service.generate_resume(match_id)
        return str(resume.id)

    resume_id = run_async(_run())

    # TODO: Generate PDF and send notification
    # from app.services.pdf_service import PDFService
    # from app.services.notification_service import NotificationService

    return {"status": "completed", "resume_id": resume_id}


@celery_app.task(name="app.workers.celery_worker.send_daily_digests_task")
def send_daily_digests_task():
    """Periodic task: Send daily digest emails to all users."""
    from app.database import connect_to_mongo

    async def _run():
        await connect_to_mongo()
        # TODO: Implement notification service
        # from app.services.notification_service import NotificationService
        # results = await NotificationService.send_all_daily_digests()
        # return results
        return {"status": "not_implemented"}

    results = run_async(_run())
    return results


@celery_app.task(name="app.workers.celery_worker.run_matching_all_task")
def run_matching_all_task():
    """Periodic task: Run matching for all active users against recent jobs."""
    from app.models import User
    from app.services.matching_service import MatchingService
    from app.database import connect_to_mongo

    async def _run():
        await connect_to_mongo()

        users = await User.find(
            User.onboarding_completed == True,
            User.is_active == True
        ).to_list()

        total_matches = 0
        for user in users:
            matches = await MatchingService.run_matching_for_user(user, days=1)
            total_matches += len(matches)

        return {"users_processed": len(users), "matches_created": total_matches}

    results = run_async(_run())
    return results


if __name__ == "__main__":
    # Run worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=4"
    ])
