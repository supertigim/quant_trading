from nicegui import ui
from src.db.session import AsyncSessionLocal
from src.core.security import get_password_hash
from src.core.config import settings
from src.db.repositories.user import UserRepository
from src.schemas.user import UserCreate
import uuid
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_register_page():
    with ui.card().classes(
        "w-full max-w-md mx-auto mt-8 bg-gray-800 shadow-lg rounded-lg"
    ):
        ui.label("회원가입").classes("text-2xl font-bold mb-6 text-center text-white")

        with ui.column().classes("w-full px-6 pb-6"):
            username = (
                ui.input(placeholder="사용자 이름")
                .classes(
                    "w-full mb-4 bg-gray-700 text-white border border-gray-600 rounded-lg"
                )
                .props("input-class=text-white placeholder-color=gray-400")
            )

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

            confirm_password = (
                ui.input(placeholder="비밀번호 확인", password=True)
                .classes(
                    "w-full mb-4 bg-gray-700 text-white border border-gray-600 rounded-lg"
                )
                .props("input-class=text-white placeholder-color=gray-400")
            )

            error_label = ui.label("").classes("text-red-400 mb-4 text-sm")

            async def handle_register():
                try:
                    logger.info(f"회원가입 시도: {email.value} ({username.value})")

                    if not all(
                        [
                            username.value,
                            email.value,
                            password.value,
                            confirm_password.value,
                        ]
                    ):
                        error_label.set_text("모든 필드를 입력해주세요.")
                        logger.warning("회원가입 실패: 필수 입력값 누락")
                        return

                    if password.value != confirm_password.value:
                        error_label.set_text("비밀번호가 일치하지 않습니다.")
                        logger.warning("회원가입 실패: 비밀번호 불일치")
                        return

                    async with AsyncSessionLocal() as db:
                        user_repo = UserRepository(db)

                        if await user_repo.get_by_email(email.value):
                            error_label.set_text("이미 등록된 이메일입니다.")
                            logger.warning(
                                f"회원가입 실패: 이메일 중복 ({email.value})"
                            )
                            return

                        if await user_repo.get_by_username(username.value):
                            error_label.set_text("이미 사용 중인 사용자 이름입니다.")
                            logger.warning(
                                f"회원가입 실패: 사용자 이름 중복 ({username.value})"
                            )
                            return

                        user_data = UserCreate(
                            id=str(uuid.uuid4()),
                            email=email.value,
                            username=username.value,
                            password=password.value,
                        )

                        user = await user_repo.create(user_data)
                        logger.info(f"회원가입 성공: {user.username} ({user.email})")

                        ui.notify("회원가입이 완료되었습니다!", type="positive")
                        ui.navigate.to("/login")

                except Exception as e:
                    error_msg = f"회원가입 중 오류가 발생했습니다: {str(e)}"
                    error_label.set_text(error_msg)
                    logger.error(f"회원가입 오류: {str(e)}", exc_info=True)

            ui.button("회원가입", on_click=handle_register).classes(
                "w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors"
            )

            with ui.row().classes("w-full justify-center mt-4"):
                ui.link("이미 계정이 있으신가요? 로그인", "/login").classes(
                    "text-blue-400 hover:text-blue-300 text-sm transition-colors"
                )
