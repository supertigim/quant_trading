from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nicegui import ui, app
from src.core.config import settings
from src.api.v1.api import api_router
from src.pages.register import create_register_page
from src.pages.login import create_login_page
from src.pages.main import create_main_page


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
    def home():
        create_main_page()

    @ui.page("/register")
    def register():
        create_register_page()

    @ui.page("/login")
    def login():
        create_login_page()

    # Mount NiceGUI
    ui.run_with(app)

    return app


app = create_app()
