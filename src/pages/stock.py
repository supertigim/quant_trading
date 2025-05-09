import logging
from nicegui import ui
from src.db.session import AsyncSessionLocal
from src.db.repositories.stock import StockRepository
from src.models.stock import Stock
from src.services.stock_service import StockService
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@ui.page("/stock/{ticker}")
def stock_detail_page(ticker: str):
    """주식 상세 정보 페이지"""
    with ui.column().classes("w-full items-center gap-4"):
        ui.label(f"주식 상세 정보: {ticker}").classes("text-2xl font-bold")

        # 뒤로가기 버튼
        ui.button("목록으로 돌아가기", on_click=lambda: ui.navigate.to("/")).classes(
            "bg-blue-500 hover:bg-blue-600 text-white"
        )

        # 상세 정보를 표시할 컨테이너
        with ui.card().classes("w-full max-w-2xl") as container:
            # 기본 정보 섹션
            with ui.card().classes("w-full"):
                ui.label("기본 정보").classes("text-xl font-bold mb-4")
                info_grid = ui.grid(columns=2).classes("gap-4")
                with info_grid:
                    ui.label("종목명").classes("font-bold")
                    name_label = ui.label("로딩 중...")
                    ui.label("티커").classes("font-bold")
                    ticker_label = ui.label("로딩 중...")
                    ui.label("마켓").classes("font-bold")
                    market_label = ui.label("로딩 중...")
                    ui.label("국가").classes("font-bold")
                    country_label = ui.label("로딩 중...")
                    ui.label("마지막 업데이트").classes("font-bold")
                    last_updated_label = ui.label("로딩 중...")

            # 차트 섹션 (추후 구현)
            with ui.card().classes("w-full"):
                ui.label("가격 차트").classes("text-xl font-bold mb-4")
                ui.label("차트는 추후 구현 예정입니다.").classes("text-gray-500")

            # 거래 내역 섹션 (추후 구현)
            with ui.card().classes("w-full"):
                ui.label("거래 내역").classes("text-xl font-bold mb-4")
                ui.label("거래 내역은 추후 구현 예정입니다.").classes("text-gray-500")

            async def load_stock_details():
                try:
                    async with AsyncSessionLocal() as db:
                        stock_repo = StockRepository(db)
                        stock = await stock_repo.get_by_ticker(ticker)

                        if stock:
                            # UI 업데이트를 컨테이너 컨텍스트 내에서 수행
                            with container:
                                # 기본 정보 업데이트
                                name_label.set_text(stock.name)
                                ticker_label.set_text(stock.ticker)
                                market_label.set_text(stock.market)
                                country_label.set_text(stock.country)
                                last_updated_label.set_text(
                                    stock.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                                    if stock.last_updated
                                    else "-"
                                )

                                # 로딩 성공 알림
                                ui.notify(
                                    "종목 정보를 성공적으로 불러왔습니다.",
                                    type="positive",
                                )
                        else:
                            with container:
                                ui.notify(
                                    f"종목을 찾을 수 없습니다: {ticker}",
                                    type="negative",
                                )
                                ui.navigate.to("/")

                except Exception as e:
                    logger.error(f"Error loading stock details: {str(e)}")
                    with container:
                        ui.notify(
                            "종목 정보를 불러오는 중 오류가 발생했습니다.",
                            type="negative",
                        )

            # 비동기로 데이터 로드
            asyncio.create_task(load_stock_details())
