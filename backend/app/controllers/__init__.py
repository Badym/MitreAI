from fastapi import APIRouter

from app.controllers import (
    auth_controller,
    conversation_controller,
    health_controller,
    message_controller,
    model_controller,
    user_controller,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(health_controller.router)
api_router.include_router(auth_controller.router)
api_router.include_router(user_controller.router)
api_router.include_router(model_controller.router)
api_router.include_router(conversation_controller.router)
api_router.include_router(message_controller.router)
