import sys  # Import sys for flush=True
import logging
from nicegui import ui
from src.db.session import get_db
from src.db.repositories.stock import StockRepository
from uuid import UUID

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_stocks_page():
    # 국가 선택을 위한 상수
    COUNTRIES = {"KR": "한국", "US": "미국", "CA": "캐나다"}

    # 데이터베이스 세션 생성
    db = next(get_db())
    stock_repo = StockRepository(db)

    # 페이지네이션 상태
    current_page = 1
    items_per_page = 10

    # 중앙 정렬을 위한 컨테이너
    with ui.column().classes("w-full items-center gap-4"):
        # 제목 추가
        ui.label("주식 목록").classes("text-2xl font-bold")

        # 테이블 컨테이너
        table_container = ui.column().classes("w-full max-w-2xl gap-2")

        # 체크박스 상태 저장
        checkboxes = []

        # 테이블 헤더
        with table_container:
            with ui.row().classes("w-full items-center gap-4 font-bold border-b pb-2"):
                # 전체 선택 체크박스
                select_all = ui.checkbox().classes("w-16")

                # 전체 선택 체크박스 이벤트 핸들러
                def on_select_all_change(e):
                    logger.info(f"Select all checkbox changed: {e.args}")
                    print(
                        f"--- EVENT: on_select_all_change --- Value: {e.args}",
                        flush=True,
                    )
                    is_checked = e.args[0]
                    for cb_item in checkboxes:
                        cb_item.set_value(is_checked)
                    update_selected_count("on_select_all_change")
                    # 알림 표시
                    ui.notify(
                        f"전체 선택: {'선택' if is_checked else '해제'}", position="top"
                    )

                select_all.on("update:model-value", on_select_all_change)

                ui.label("종목명").classes("w-48")
                ui.label("티커").classes("w-32")
                ui.label("국가").classes("w-24")

        # 데이터 컨테이너
        data_container = ui.column().classes("w-full max-w-2xl gap-2")

        # 페이지네이션 컨트롤
        pagination_container = ui.row().classes(
            "w-full max-w-2xl justify-between items-center gap-2 mt-4"
        )

        # 선택된 항목 수 표시 레이블
        selected_count_label = ui.label("선택된 항목: 0개").classes(
            "text-sm text-gray-600"
        )

        # 삭제 버튼
        delete_button = (
            ui.button("선택 항목 삭제", on_click=lambda: None)
            .classes("bg-red-500 hover:bg-red-600 text-white")
            .props("disable")
        )

        # 선택된 항목 수 업데이트 함수
        def update_selected_count(event_source_info="N/A"):
            logger.info(f"update_selected_count called from: {event_source_info}")
            print(
                f"--- update_selected_count CALLED from: {event_source_info} ---",
                flush=True,
            )
            selected_count = 0
            for i, cb in enumerate(checkboxes):
                if cb.value:
                    selected_count += 1
            selected_count_label.set_text(f"선택된 항목: {selected_count}개")
            # 삭제 버튼 활성화/비활성화
            delete_button.props(f"disable={selected_count == 0}")
            print(f"Updated selected count: {selected_count}", flush=True)

        # 삭제 확인 다이얼로그
        def show_delete_confirmation():
            with ui.dialog() as dialog, ui.card():
                ui.label("정말 삭제하시겠습니까?").classes("text-lg font-bold mb-4")
                with ui.row().classes("w-full justify-center gap-4"):
                    ui.button("네", on_click=lambda: handle_delete(dialog)).classes(
                        "bg-red-500 text-white"
                    )
                    ui.button("아니오", on_click=dialog.close).classes(
                        "bg-gray-500 text-white"
                    )
            dialog.open()

        # 삭제 처리 함수
        def handle_delete(dialog):
            try:
                # 선택된 항목들의 인덱스 수집
                selected_indices = []
                for i, cb in enumerate(checkboxes):
                    if cb.value:
                        selected_indices.append(i)

                # 선택된 항목들의 정보 수집
                stocks = stock_repo.get_all()
                start_idx = (current_page - 1) * items_per_page
                selected_stocks = [stocks[start_idx + i] for i in selected_indices]

                # 데이터베이스에서 삭제
                for stock in selected_stocks:
                    stock_repo.delete(stock)
                    logger.info(
                        f"Successfully deleted stock: {stock.name} (ID: {stock.id})"
                    )

                ui.notify("선택한 항목이 삭제되었습니다.", type="positive")
                dialog.close()
                refresh_stocks()  # 목록 새로고침
            except Exception as e:
                logger.error(f"Error deleting stocks: {str(e)}")
                ui.notify("삭제 중 오류가 발생했습니다.", type="negative")

        # 삭제 버튼 클릭 이벤트 연결
        delete_button.on("click", show_delete_confirmation)

        # 페이지 변경 함수
        def change_page(page):
            nonlocal current_page
            current_page = page
            refresh_stocks()

        # 주식 목록 새로고침 함수
        def refresh_stocks():
            logger.info("Refreshing stocks list")
            print("--- refresh_stocks CALLED ---", flush=True)
            data_container.clear()
            pagination_container.clear()
            checkboxes.clear()
            if "select_all" in locals() or "select_all" in globals():
                select_all.value = False

            stocks = stock_repo.get_all()
            total_items = len(stocks)
            total_pages = (total_items + items_per_page - 1) // items_per_page
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)

            for stock_idx, stock in enumerate(stocks[start_idx:end_idx]):
                with data_container:
                    with ui.row().classes("w-full items-center gap-4 py-2"):
                        checkbox = ui.checkbox().classes("w-16")

                        # 개별 체크박스 이벤트 핸들러
                        def handle_individual_checkbox_change(
                            e, item_name=stock.name, item_idx_in_page=stock_idx
                        ):
                            # 로깅
                            logger.info(f"Checkbox changed - {item_name}: {e.args}")
                            print(
                                f"--- EVENT: Individual Checkbox ({item_name}, page_idx:{item_idx_in_page}) --- Value: {e.args}",
                                flush=True,
                            )

                            # 알림 표시
                            ui.notify(
                                f"{item_name} {'선택' if e.args[0] else '해제'}",
                                position="top",
                                type="positive" if e.args[0] else "negative",
                            )

                            update_selected_count(f"individual checkbox: {item_name}")

                        checkbox.on(
                            "update:model-value",
                            lambda e, s_name=stock.name, s_idx=stock_idx: handle_individual_checkbox_change(
                                e, s_name, s_idx
                            ),
                        )
                        checkboxes.append(checkbox)
                        ui.label(stock.name).classes("w-48")
                        ui.label(stock.ticker).classes("w-32")
                        ui.label(COUNTRIES.get(stock.country, stock.country)).classes(
                            "w-24"
                        )
            update_selected_count("refresh_stocks end")

            with pagination_container:
                # 왼쪽: 선택된 항목 수와 삭제 버튼
                with ui.row().classes("items-center gap-4"):
                    selected_count_label
                    delete_button

                # 오른쪽: 페이지네이션 컨트롤
                with ui.row().classes("items-center gap-2"):
                    if current_page > 1:
                        ui.button(
                            "이전", on_click=lambda: change_page(current_page - 1)
                        ).classes("px-4 py-2")
                    ui.label(f"페이지 {current_page} / {total_pages}").classes("px-4")
                    if current_page < total_pages:
                        ui.button(
                            "다음", on_click=lambda: change_page(current_page + 1)
                        ).classes("px-4 py-2")

        refresh_stocks()
