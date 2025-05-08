from nicegui import ui
from src.db.session import get_db
from src.db.repositories.stock import StockRepository


def create_stocks_page():
    # 국가 선택을 위한 상수
    COUNTRIES = {"KR": "한국", "US": "미국", "CA": "캐나다"}

    # 데이터베이스 세션 생성
    db = next(get_db())
    stock_repo = StockRepository(db)

    # 중앙 정렬을 위한 컨테이너
    with ui.column().classes("w-full items-center gap-4"):
        # 제목 추가
        ui.label("주식 목록").classes("text-2xl font-bold")

        # 테이블 컨테이너
        table_container = ui.column().classes("w-full max-w-2xl gap-2")

        # 테이블 헤더
        with table_container:
            with ui.row().classes("w-full items-center gap-4 font-bold border-b pb-2"):
                ui.label("선택").classes("w-16")
                ui.label("종목명").classes("w-48")
                ui.label("티커").classes("w-32")
                ui.label("국가").classes("w-24")

        # 데이터 컨테이너
        data_container = ui.column().classes("w-full max-w-2xl gap-2")

        # 주식 목록 새로고침 함수
        def refresh_stocks():
            # 기존 데이터 제거
            data_container.clear()

            # 주식 목록 가져오기
            stocks = stock_repo.get_all()

            # 각 주식에 대한 체크박스와 정보 추가
            for stock in stocks:
                with data_container:
                    with ui.row().classes("w-full items-center gap-4 py-2"):
                        ui.checkbox().classes("w-16")
                        ui.label(stock.name).classes("w-48")
                        ui.label(stock.ticker).classes("w-32")
                        ui.label(COUNTRIES.get(stock.country, stock.country)).classes(
                            "w-24"
                        )

        # 초기 데이터 로드
        refresh_stocks()
