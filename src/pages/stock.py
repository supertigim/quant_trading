import logging
from nicegui import ui
from src.db.session import AsyncSessionLocal
from src.db.repositories.stock import StockRepository
from src.db.repositories.price import PriceRepository
from src.models.stock import Stock
from src.models.price import Price
from src.services.stock_service import StockService
import asyncio
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

            # 차트 섹션
            with ui.card().classes("w-full"):
                ui.label("가격 차트").classes("text-xl font-bold mb-4")

                # 기간 설정
                with ui.row().classes("w-full items-center gap-4 mb-4"):
                    # 시작일 (3개월 전)
                    start_date = datetime.now() - timedelta(days=90)
                    start_date_value = start_date.strftime("%Y-%m-%d")
                    start_date_input = (
                        ui.input("시작일", value=start_date_value)
                        .props("readonly")
                        .classes("w-full")
                    )
                    start_date_dialog = ui.dialog()
                    with start_date_dialog:
                        date_picker = ui.date(value=start_date_value)
                        ui.button(
                            "확인",
                            on_click=lambda: (
                                start_date_input.set_value(date_picker.value),
                                start_date_dialog.close(),
                                update_chart(),
                            ),
                        ).props("color=primary")
                    start_date_input.on("click", lambda: start_date_dialog.open())

                    # 종료일 (오늘)
                    end_date = datetime.now()
                    end_date_value = end_date.strftime("%Y-%m-%d")
                    end_date_input = (
                        ui.input("종료일", value=end_date_value)
                        .props("readonly")
                        .classes("w-full")
                    )
                    end_date_dialog = ui.dialog()
                    with end_date_dialog:
                        date_picker2 = ui.date(value=end_date_value)
                        ui.button(
                            "확인",
                            on_click=lambda: (
                                end_date_input.set_value(date_picker2.value),
                                end_date_dialog.close(),
                                update_chart(),
                            ),
                        ).props("color=primary")
                    end_date_input.on("click", lambda: end_date_dialog.open())

                    # 기간 선택 버튼 + 차트 보기 버튼을 같은 row에 배치
                    with ui.row().classes("w-2/3 items-center gap-2"):
                        with ui.button_group():
                            ui.button(
                                "1주일", on_click=lambda: set_date_range(7)
                            ).classes("bg-blue-500 hover:bg-blue-600 text-white")
                            ui.button(
                                "1개월", on_click=lambda: set_date_range(30)
                            ).classes("bg-blue-500 hover:bg-blue-600 text-white")
                            ui.button(
                                "3개월", on_click=lambda: set_date_range(90)
                            ).classes("bg-blue-500 hover:bg-blue-600 text-white")
                            ui.button(
                                "1년", on_click=lambda: set_date_range(365)
                            ).classes("bg-blue-500 hover:bg-blue-600 text-white")
                        ui.button(
                            "차트 보기",
                            on_click=lambda: update_chart(),
                        ).classes("ml-2 bg-blue-500 hover:bg-blue-600 text-white")

                # 차트 영역
                chart_container = ui.card().classes("w-full h-[400px]")

            def set_date_range(days: int):
                """기간을 설정하고 차트를 업데이트합니다."""
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                start_date_input.set_value(start_date.strftime("%Y-%m-%d"))
                end_date_input.set_value(end_date.strftime("%Y-%m-%d"))
                update_chart()

            def update_chart():
                """차트를 업데이트합니다."""
                try:
                    start = datetime.strptime(start_date_input.value, "%Y-%m-%d")
                    end = datetime.strptime(end_date_input.value, "%Y-%m-%d")

                    if start > end:
                        ui.notify(
                            "시작일이 종료일보다 늦을 수 없습니다.", type="negative"
                        )
                        return

                    async def fetch_and_display_data():
                        async with AsyncSessionLocal() as db:
                            stock_repo = StockRepository(db)
                            price_repo = PriceRepository(db)

                            # 주식 정보 조회
                            stock = await stock_repo.get_by_ticker(ticker)
                            if not stock:
                                ui.notify(
                                    "주식 정보를 찾을 수 없습니다.", type="negative"
                                )
                                return

                            # DB에서 데이터 확인
                            db_data = await price_repo.get_by_stock_and_date_range(
                                stock.id, start, end
                            )

                            if not db_data:
                                # DB에 데이터가 없으면 FinanceDataReader로 가져오기
                                df = fdr.DataReader(ticker, start, end)

                                if df.empty:
                                    ui.notify(
                                        "해당 기간의 데이터를 찾을 수 없습니다.",
                                        type="negative",
                                    )
                                    return

                                # DB에 데이터 저장
                                prices = []
                                for index, row in df.iterrows():
                                    price = Price(
                                        stock_id=stock.id,
                                        date=index,
                                        open=float(row["Open"]),
                                        high=float(row["High"]),
                                        low=float(row["Low"]),
                                        close=float(row["Close"]),
                                        volume=int(row["Volume"]),
                                    )
                                    prices.append(price)

                                await price_repo.bulk_create(prices)
                                db_data = await price_repo.get_by_stock_and_date_range(
                                    stock.id, start, end
                                )

                            # 차트 데이터 준비
                            dates = [price.date for price in db_data]
                            closes = [price.close for price in db_data]
                            volumes = [price.volume for price in db_data]

                            # Plotly 차트 생성
                            fig = make_subplots(
                                rows=2,
                                cols=1,
                                shared_xaxes=True,
                                vertical_spacing=0.03,
                                row_heights=[0.7, 0.3],
                            )

                            # 주가 차트
                            fig.add_trace(
                                go.Candlestick(
                                    x=dates,
                                    open=[price.open for price in db_data],
                                    high=[price.high for price in db_data],
                                    low=[price.low for price in db_data],
                                    close=closes,
                                    name="주가",
                                ),
                                row=1,
                                col=1,
                            )

                            # 거래량 차트
                            fig.add_trace(
                                go.Bar(x=dates, y=volumes, name="거래량"), row=2, col=1
                            )

                            # 차트 레이아웃 설정
                            fig.update_layout(
                                title=f"{ticker} 주가 차트",
                                yaxis_title="주가",
                                yaxis2_title="거래량",
                                xaxis_rangeslider_visible=False,
                                height=600,
                            )

                            # 차트 표시
                            with chart_container:
                                chart_container.clear()
                                ui.plotly(fig).classes("w-full h-full")

                    # 비동기 함수 실행
                    asyncio.create_task(fetch_and_display_data())

                except Exception as e:
                    logger.error(f"Error updating chart: {str(e)}")
                    ui.notify("차트 업데이트 중 오류가 발생했습니다.", type="negative")

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
