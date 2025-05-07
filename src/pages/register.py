from nicegui import ui
from src.schemas.user import UserCreate
from src.db.repositories.user import UserRepository
from src.db.session import SessionLocal
from src.core.security import create_access_token
from datetime import timedelta
from src.core.config import settings
import uuid


def create_register_page():
    with ui.card().classes("w-full max-w-md mx-auto mt-8"):
        ui.label("Registration").classes("text-2xl font-bold mb-4")

        email = ui.input("Email").classes("w-full mb-4")
        username = ui.input("Username").classes("w-full mb-4")
        password = ui.input("Password", password=True).classes("w-full mb-4")
        confirm_password = ui.input("Confirm Password", password=True).classes(
            "w-full mb-4"
        )

        error_label = ui.label("").classes("text-red-500 mb-4")

        async def handle_register():
            if not email.value or not username.value or not password.value:
                error_label.set_text("All fields are required")
                return

            if password.value != confirm_password.value:
                error_label.set_text("Passwords do not match")
                return

            if len(password.value) < 8:
                error_label.set_text("Password must be at least 8 characters long")
                return

            try:
                db = SessionLocal()
                user_repo = UserRepository(db)

                # Check if email already exists
                if user_repo.get_by_email(email.value):
                    error_label.set_text("Email already registered")
                    return

                # Check if username already exists
                if user_repo.get_by_username(username.value):
                    error_label.set_text("Username already taken")
                    return

                # Create new user
                user_data = UserCreate(
                    id=str(uuid.uuid4()),
                    email=email.value,
                    username=username.value,
                    password=password.value,
                )

                user = user_repo.create(user_data)

                # Initialize storage if not exists
                if not hasattr(ui, "storage"):
                    ui.storage = {}
                if "user" not in ui.storage:
                    ui.storage["user"] = {}

                # Create access token and store user info
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

                ui.notify("Registration successful! Welcome!", type="positive")
                ui.navigate.to("/")  # Redirect to main page

            except Exception as e:
                error_label.set_text(f"Registration failed: {str(e)}")
            finally:
                db.close()

        ui.button("Register", on_click=handle_register).classes(
            "w-full bg-blue-500 text-white"
        )
        ui.link("Already have an account? Login", "/login").classes(
            "mt-4 text-blue-500"
        )
