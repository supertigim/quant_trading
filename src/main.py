from fastapi import FastAPI
from nicegui import ui
import logging
from src.core.config import settings
from src.core.middleware import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from src.pages.login import create_login_page
from src.pages.register import create_register_page
from src.pages.stocks import create_stocks_page
from src.pages.test import create_test_page
from src.pages.stock import stock_detail_page
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import auth

logger_main = logging.getLogger("main_debug_minimal")

# 1. FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 미들웨어 추가 (순서 중요: 나중에 추가된 미들웨어가 먼저 실행됨)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# API 라우터 등록
app.include_router(auth.router, prefix=settings.API_V1_STR)

# 다크 모드 설정
ui.dark_mode(True)


# 2. NiceGUI 페이지 정의
@ui.page("/")
def minimal_home_page():
    logger_main.info("Accessing MINIMAL home_page (/) triggering storage test")

    with ui.card().classes("w-full max-w-2xl mx-auto mt-8 bg-gray-800"):
        ui.label("Welcome to Quant Trading").classes(
            "text-2xl font-bold mb-4 text-white"
        )

        # User info section
        with ui.card().classes("w-full mb-4 bg-gray-700"):
            ui.label("User Information").classes(
                "text-xl font-semibold mb-2 text-white"
            )

            user_info = ui.label("Loading...").classes(
                "text-gray-300 whitespace-pre-line"
            )

            def load_user_info():
                # Initialize storage if not exists
                if not hasattr(ui, "storage"):
                    ui.storage = {}
                if "user" not in ui.storage:
                    ui.storage["user"] = {}

                user = ui.storage.get("user", {}).get("user")
                if user:
                    username = user.get("username", "N/A")
                    email = user.get("email", "N/A")
                    user_id = user.get("id", "N/A")

                    user_info_text = f"Username: {username}\n"
                    if email != "N/A":
                        user_info_text += f"Email: {email}\n"
                    if user_id != "N/A":
                        user_info_text += f"User ID: {user_id}"

                    user_info.set_text(user_info_text.strip())
                else:
                    user_info.set_text("User not logged in")

            # Load user info immediately
            load_user_info()

        # Logout function
        async def handle_logout():
            # Initialize storage if not exists
            if not hasattr(ui, "storage"):
                ui.storage = {}
            if "user" not in ui.storage:
                ui.storage["user"] = {}

            # Clear ui.storage
            ui.storage["user"] = {}

            ui.notify("Logged out successfully", type="positive")
            ui.navigate.to("/login")

        # Navigation buttons
        with ui.row().classes("w-full justify-center gap-4"):
            ui.button("주식 관리", on_click=lambda: ui.navigate.to("/stocks")).classes(
                "bg-blue-500 hover:bg-blue-600 text-white"
            )
            ui.button("테스트", on_click=lambda: ui.navigate.to("/test")).classes(
                "bg-green-500 hover:bg-green-600 text-white"
            )
            ui.button("Logout", on_click=handle_logout).classes(
                "bg-red-500 hover:bg-red-600 text-white"
            )


# 로그인 페이지 등록
@ui.page("/login")
def login_page():
    create_login_page()


# 회원가입 페이지 등록
@ui.page("/register")
def register_page():
    create_register_page()


# 주식 관리 페이지 등록
@ui.page("/stocks")
def stocks_page():
    create_stocks_page()


# 주식 상세 페이지는 이미 @ui.page 데코레이터로 등록되어 있으므로 여기서는 import만 하면 됩니다


# 테스트 페이지 등록
@ui.page("/test")
def test_page():
    create_test_page()


# 3. NiceGUI를 FastAPI 앱과 함께 실행
# storage_secret은 ui.storage가 초기화되는 데 매우 중요합니다.
ui.run_with(
    app,
    title="Minimal Storage Test",
    storage_secret=settings.SECRET_KEY,
    dark=True,  # 다크 모드 기본값 설정
)

logger_main.info(
    "MINIMAL FastAPI app setup complete, NiceGUI integrated with ui.run_with."
)
