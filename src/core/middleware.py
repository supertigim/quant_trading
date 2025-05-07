from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.types import ASGIApp
from typing import Callable, Awaitable
import logging
from nicegui import ui

# Public NiceGUI page paths that do not require authentication
PUBLIC_PAGE_PATHS = ["/login", "/register"]

# Prefixes for paths that should be ignored by this authentication middleware.
# These include API routes (which should have their own token auth),
# FastAPI/Swagger docs, and NiceGUI's internal static files/endpoints.
IGNORED_PATH_PREFIXES = [
    "/api",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/_nicegui",  # Crucial for NiceGUI's functionality (includes socket.io)
    # If you have custom static files served outside NiceGUI's @ui.page, add their prefix e.g., "/static"
]

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path

        # Bypass middleware for ignored path prefixes
        for prefix in IGNORED_PATH_PREFIXES:
            if path.startswith(prefix):
                return await call_next(request)

        # Bypass middleware for public NiceGUI page paths
        if path in PUBLIC_PAGE_PATHS:
            return await call_next(request)

        # Initialize storage if not exists
        if not hasattr(ui, "storage"):
            ui.storage = {}
        if "user" not in ui.storage:
            ui.storage["user"] = {}

        # Check authentication using ui.storage
        authenticated = False
        try:
            if ui.storage.get("user") and ui.storage["user"].get("user"):
                authenticated = True
        except Exception as e:
            logger.error(f"Unexpected error accessing storage: {e}")
            return await call_next(request)

        if not authenticated:
            accept_header = request.headers.get("accept", "")
            if "text/html" in accept_header:
                return RedirectResponse(url="/login", status_code=303)

        return await call_next(request)
