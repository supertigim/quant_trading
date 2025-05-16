import logging

from nicegui import ui
from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.core.config import settings
from src.core.security import create_access_token, verify_password
from src.api.deps import authenticate_user
from src.models.user import User


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_login_page():
    with ui.card().classes(
        "w-full max-w-md mx-auto mt-8 bg-gray-800 shadow-lg rounded-lg"
    ):
        ui.label("로그인").classes("text-2xl font-bold mb-6 text-center text-white")

        with ui.column().classes("w-full px-6 pb-6"):
            email = (
                ui.input(placeholder="이메일")
                .classes(
                    "w-full mb-4 bg-gray-700 text-white border border-gray-600 rounded-lg"
                )
                .props("input-class=text-white placeholder-color=gray-400")
            )

            password = (
                ui.input(placeholder="비밀번호", password=True)
                .classes(
                    "w-full mb-4 bg-gray-700 text-white border border-gray-600 rounded-lg"
                )
                .props("input-class=text-white placeholder-color=gray-400")
            )

            error_label = ui.label("").classes("text-red-400 mb-4 text-sm")

            async def handle_login():
                try:
                    logger.info(f"로그인 시도: {email.value}")

                    if not email.value or not password.value:
                        error_label.set_text("이메일과 비밀번호를 입력해주세요.")
                        logger.warning("로그인 실패: 필수 입력값 누락")
                        return

                    async with AsyncSessionLocal() as db:
                        result = await db.execute(
                            select(User).where(User.email == email.value)
                        )
                        user = result.scalar_one_or_none()

                        if not user:
                            error_label.set_text(
                                "이메일 또는 비밀번호가 올바르지 않습니다."
                            )
                            logger.warning(
                                f"로그인 실패: 사용자를 찾을 수 없음 (이메일: {email.value})"
                            )
                            return

                        if not verify_password(password.value, user.hashed_password):
                            error_label.set_text(
                                "이메일 또는 비밀번호가 올바르지 않습니다."
                            )
                            logger.warning(
                                f"로그인 실패: 비밀번호 불일치 (이메일: {email.value})"
                            )
                            return

                        access_token = create_access_token(data={"sub": str(user.id)})
                        logger.info(f"로그인 성공: {user.username} ({user.email})")

                        if not hasattr(ui, "storage"):
                            ui.storage = {}
                        if "user" not in ui.storage:
                            ui.storage["user"] = {}

                        ui.storage["user"] = {
                            "token": access_token,
                            "user": {
                                "id": str(user.id),
                                "username": user.username,
                                "email": user.email,
                                "is_active": user.is_active,
                                "is_superuser": user.is_superuser,
                            },
                        }

                        ui.notify("로그인 성공!", type="positive")
                        ui.navigate.to("/")

                except Exception as e:
                    error_msg = f"로그인 중 오류가 발생했습니다: {str(e)}"
                    error_label.set_text(error_msg)
                    logger.error(f"로그인 오류: {str(e)}", exc_info=True)

            ui.button("로그인", on_click=handle_login).classes(
                "w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors"
            )

            with ui.row().classes("w-full justify-center mt-4"):
                ui.link("계정이 없으신가요? 회원가입", "/register").classes(
                    "text-blue-400 hover:text-blue-300 text-sm transition-colors"
                )
