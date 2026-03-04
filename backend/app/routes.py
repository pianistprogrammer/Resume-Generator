"""API route registration."""

from fastapi import APIRouter
from app.controllers import auth_controller, profile_controller, job_controller, resume_controller, admin_controller


api_router = APIRouter()

# Register all route modules
api_router.include_router(auth_controller.router)
api_router.include_router(profile_controller.router)
api_router.include_router(job_controller.router)
api_router.include_router(resume_controller.router)
api_router.include_router(admin_controller.router)

# Additional routers will be added as they are implemented:
# api_router.include_router(payment_controller.router)
