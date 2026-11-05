from .routes_auth import router as auth_router
from .routes_conversations import router as conversations_router
from .routes_services import router as services_router
from .routes_analytics import router as analytics_router
from .routes_community import router as community_router
from .routes_admin import router as admin_router

__all__ = [
    "auth_router",
    "conversations_router",
    "services_router",
    "analytics_router",
    "community_router",
    "admin_router"
]
