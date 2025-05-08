from nicegui import ui
import logging
import FinanceDataReader as fdr

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_page():
    logger.info("Creating test page...")

    with ui.column().classes("w-full items-center gap-4"):
        # 제목
        ui.label("테스트 페이지").classes("text-2xl font-bold")

        # 한국 주식 목록 표시
        with ui.card().classes("w-full max-w-4xl"):
            ui.label("한국 주식 목록").classes("text-lg font-bold mb-4")

            try:
                # FinanceDataReader로 주식 정보 조회
                stock_info = fdr.StockListing("ETF/KR")

                # 데이터 구조 확인을 위한 로깅
                logger.info(f"Available columns: {stock_info.columns.tolist()}")

                # KODEX와 TIGER ETF만 필터링
                stock_info = stock_info[
                    stock_info["Name"].str.startswith(("KODEX", "TIGER"), na=False)
                ]

                # 테이블 생성
                columns = [
                    {"name": "symbol", "label": "티커", "field": "symbol"},
                    {"name": "name", "label": "종목명", "field": "name"},
                    {"name": "category", "label": "카테고리", "field": "category"},
                    {"name": "price", "label": "가격", "field": "price"},
                    {"name": "change_rate", "label": "등락률", "field": "change_rate"},
                ]

                rows = [
                    {
                        "symbol": row["Symbol"],
                        "name": row["Name"],
                        "category": row["Category"] if "Category" in row else "N/A",
                        "price": row["Price"] if "Price" in row else "N/A",
                        "change_rate": (
                            row["ChangeRate"] if "ChangeRate" in row else "N/A"
                        ),
                    }
                    for _, row in stock_info.iterrows()
                ]

                table = ui.table(columns=columns, rows=rows).classes("w-full")

            except Exception as e:
                logger.error(f"Error fetching stock info: {e}")
                ui.label("주식 정보를 가져오는 중 오류가 발생했습니다.").classes(
                    "text-md text-red-500"
                )

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
