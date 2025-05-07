from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nicegui import ui
from src.core.config import settings
from src.api.v1.api import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Set CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Create the main page
    @ui.page("/")
    def main():
        ui.label(settings.PROJECT_NAME).classes("text-h4 q-mb-md")
        with ui.card().classes("w-full"):
            ui.label(f"Welcome to {settings.PROJECT_NAME}").classes("text-h5")
            ui.label("This is a basic setup with NiceGUI and PostgreSQL.")

    # Mount NiceGUI
    ui.run_with(app)

    return app


app = create_app()
