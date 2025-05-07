from nicegui import ui
from src.api.deps import authenticate_user
from src.core.security import create_access_token
from src.db.session import SessionLocal
from datetime import timedelta
from src.core.config import settings

# import nicegui # nicegui 전체 모듈 임포트 제거 또는 주석 처리
import httpx


def create_login_page():
    with ui.card().classes("w-full max-w-md mx-auto mt-8"):
        ui.label("Login").classes("text-2xl font-bold mb-4")

        email = ui.input("Email").classes("w-full mb-4")
        password = ui.input("Password", password=True).classes("w-full mb-4")
        error_label = ui.label("").classes("text-red-500 mb-4")

        async def handle_login():
            try:
                db = SessionLocal()
                user = authenticate_user(db, email.value, password.value)

                if not user:
                    error_label.set_text("Invalid email or password")
                    return

                if not user.is_active:
                    error_label.set_text("Inactive user")
                    return

                # Initialize storage if not exists
                if not hasattr(ui, "storage"):
                    ui.storage = {}
                if "user" not in ui.storage:
                    ui.storage["user"] = {}

                # Create access token
                access_token_expires = timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                )
                access_token = create_access_token(
                    user.id, expires_delta=access_token_expires
                )

                # Store user info and token in storage
                ui.storage["user"]["token"] = access_token
                ui.storage["user"]["user"] = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                }

                ui.notify("Login successful!", type="positive")
                ui.navigate.to("/")  # Redirect to home page
            except Exception as e:
                error_label.set_text(f"Login failed: {str(e)}")
            finally:
                db.close()

        ui.button("Login", on_click=handle_login).classes(
            "w-full bg-blue-500 text-white"
        )
        ui.link("Don't have an account? Register", "/register").classes(
            "mt-4 text-blue-500"
        )
