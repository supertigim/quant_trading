from nicegui import ui
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/quant_trading"
)

# App configuration
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8080"))

# Create FastAPI app
app = FastAPI(title="Quantitative Trading System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create the main page
@ui.page("/")
def main():
    ui.label("Quantitative Trading System").classes("text-h4 q-mb-md")

    with ui.card().classes("w-full"):
        ui.label("Welcome to the Quantitative Trading System").classes("text-h5")
        ui.label("This is a basic setup with NiceGUI and PostgreSQL.")


# Mount NiceGUI
ui.run_with(app)
