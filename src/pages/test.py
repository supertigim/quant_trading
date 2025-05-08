from nicegui import ui
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_page():
    logger.info("Creating test page...")

    with ui.column().classes("w-full items-center gap-4"):
        # 제목
        ui.label("테스트 페이지").classes("text-2xl font-bold")

        # 체크박스
        checkbox = ui.checkbox("테스트 체크박스")
        logger.info("Checkbox created")

        # 체크박스 이벤트 핸들러
        def on_checkbox_change(e):
            logger.info(f"Checkbox event triggered: {e}")
            print(f"체크박스 상태 변경: {e.args}", flush=True)

            try:
                if e.args[0]:
                    logger.info("Checkbox checked")
                    ui.notify(
                        "체크박스가 선택되었습니다!", position="top", type="positive"
                    )
                else:
                    logger.info("Checkbox unchecked")
                    ui.notify(
                        "체크박스가 해제되었습니다!", position="top", type="negative"
                    )
            except Exception as ex:
                logger.error(f"Error in checkbox handler: {ex}", exc_info=True)

        # 이벤트 핸들러 연결
        logger.info("Connecting checkbox event handler...")
        checkbox.on("update:model-value", on_checkbox_change)
        logger.info("Checkbox event handler connected")

        # 테스트용 버튼 추가
        def on_button_click():
            logger.info("Test button clicked")
            print("테스트 버튼 클릭됨", flush=True)
            ui.notify("테스트 버튼이 클릭되었습니다!", position="top")

        ui.button("테스트 버튼", on_click=on_button_click).classes("mt-4")
