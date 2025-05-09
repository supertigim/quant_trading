import logging
from nicegui import ui, app
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
async def stock_detail_page(ticker: str):
    stock_info = {"name": "", "ticker": "", "market": "", "country": ""}

    with ui.column().classes("w-full items-center gap-6"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("gap-4 items-center"):
                start_date = datetime.now() - timedelta(days=90)
                start_date_value = start_date.strftime("%Y-%m-%d")
                start_date_input = (
                    ui.input("시작일", value=start_date_value)
                    .props("readonly")
                    .classes("w-28")
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

                end_date = datetime.now()
                end_date_value = end_date.strftime("%Y-%m-%d")
                end_date_input = (
                    ui.input("종료일", value=end_date_value)
                    .props("readonly")
                    .classes("w-28")
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

                with ui.row().classes("items-center gap-2"):
                    with ui.button_group():
                        ui.button("1주일", on_click=lambda: set_date_range(7)).classes(
                            "bg-blue-500 hover:bg-blue-600 text-white"
                        )
                        ui.button("1개월", on_click=lambda: set_date_range(30)).classes(
                            "bg-blue-500 hover:bg-blue-600 text-white"
                        )
                        ui.button("3개월", on_click=lambda: set_date_range(90)).classes(
                            "bg-blue-500 hover:bg-blue-600 text-white"
                        )
                        ui.button("1년", on_click=lambda: set_date_range(365)).classes(
                            "bg-blue-500 hover:bg-blue-600 text-white"
                        )
                    ui.button(
                        "차트 보기",
                        on_click=lambda: update_chart(),
                    ).classes("ml-2 bg-blue-500 hover:bg-blue-600 text-white")
            stock_info_label = ui.label("").classes(
                "text-lg font-medium text-right ml-8"
            )

        chart_container = ui.card().classes("w-full h-[600px] shadow-lg")
        with ui.row().classes("w-full gap-4 mt-8"):
            with ui.card().classes("w-full min-h-[180px]"):
                ui.label("백테스트").classes("text-xl font-bold mb-2")
                ui.label("백테스트 기능은 추후 구현 예정입니다.").classes(
                    "text-gray-500"
                )

    def set_stock_info_label():
        info = app.storage.user.get("stock_info", {})
        if info and info.get("name"):
            stock_info_label.set_text(
                f"종목명: {info['name']} / 티커: {info['ticker']} / 마켓: {info['market']} / 국가: {info['country']}"
            )
        else:
            stock_info_label.set_text("")

    ui.timer(0.5, set_stock_info_label)

    def set_date_range(days: int):
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # 날짜 형식 검증
            if start_date > end_date:
                ui.notify("날짜 범위가 잘못되었습니다.", type="negative")
                return

            # 날짜 형식 변환 및 설정
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            start_date_input.set_value(start_date_str)
            end_date_input.set_value(end_date_str)

            # 차트 업데이트
            update_chart()
        except Exception as e:
            logger.error(f"Error setting date range: {str(e)}")
            ui.notify("날짜 범위 설정 중 오류가 발생했습니다.", type="negative")

    def update_chart():
        try:
            start = datetime.strptime(start_date_input.value, "%Y-%m-%d")
            end = datetime.strptime(end_date_input.value, "%Y-%m-%d")

            if start > end:
                ui.notify("시작일이 종료일보다 늦을 수 없습니다.", type="negative")
                return

            # 날짜 범위 검증
            max_days = 365 * 2  # 최대 2년
            if (end - start).days > max_days:
                ui.notify(
                    f"최대 {max_days}일의 데이터만 조회할 수 있습니다.", type="warning"
                )
                start = end - timedelta(days=max_days)
                start_date_input.set_value(start.strftime("%Y-%m-%d"))

            async def fetch_and_display_data():
                try:
                    async with AsyncSessionLocal() as db:
                        stock_repo = StockRepository(db)
                        price_repo = PriceRepository(db)

                        # 주식 정보 조회
                        stock = await stock_repo.get_by_ticker(ticker)
                        if not stock:
                            ui.notify("주식 정보를 찾을 수 없습니다.", type="negative")
                            return

                        # DB에서 데이터 확인
                        db_data = await price_repo.get_by_stock_and_date_range(
                            stock.id, start, end
                        )

                        if not db_data:
                            # DB에 데이터가 없으면 FinanceDataReader로 가져오기
                            df = fdr.DataReader(ticker, start, end)

                            if df.empty:
                                with chart_container:
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

                            # 중복 키 처리를 위한 upsert 로직
                            for price in prices:
                                existing_price = await price_repo.get_by_stock_and_date(
                                    stock.id, price.date
                                )
                                if existing_price:
                                    # 기존 데이터 업데이트
                                    existing_price.open = price.open
                                    existing_price.high = price.high
                                    existing_price.low = price.low
                                    existing_price.close = price.close
                                    existing_price.volume = price.volume
                                    await price_repo.update(existing_price)
                                else:
                                    # 새로운 데이터 추가
                                    await price_repo.create(price)

                            # 전체 데이터 다시 조회
                            db_data = await price_repo.get_by_stock_and_date_range(
                                stock.id, start, end
                            )
                        else:
                            # DB에 있는 가장 오래된 데이터의 날짜 확인
                            oldest_date = min(price.date for price in db_data)

                            # 시작일과 가장 오래된 데이터 사이의 간격이 30일 이상인 경우
                            if (oldest_date - start).days > 30:
                                # 시작일 - 30일부터 가장 오래된 데이터까지의 데이터 가져오기
                                fetch_start = start
                                fetch_end = oldest_date

                                df = fdr.DataReader(ticker, fetch_start, fetch_end)

                                if not df.empty:
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

                                    # 중복 키 처리를 위한 upsert 로직
                                    for price in prices:
                                        existing_price = (
                                            await price_repo.get_by_stock_and_date(
                                                stock.id, price.date
                                            )
                                        )
                                        if existing_price:
                                            # 기존 데이터 업데이트
                                            existing_price.open = price.open
                                            existing_price.high = price.high
                                            existing_price.low = price.low
                                            existing_price.close = price.close
                                            existing_price.volume = price.volume
                                            await price_repo.update(existing_price)
                                        else:
                                            # 새로운 데이터 추가
                                            await price_repo.create(price)

                                    # 전체 데이터 다시 조회
                                    db_data = (
                                        await price_repo.get_by_stock_and_date_range(
                                            stock.id, start, end
                                        )
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
                except Exception as e:
                    logger.error(f"Error in fetch_and_display_data: {str(e)}")
                    with chart_container:
                        ui.notify(
                            "데이터를 가져오는 중 오류가 발생했습니다.", type="negative"
                        )

            # 비동기 함수 실행
            asyncio.create_task(fetch_and_display_data())

        except Exception as e:
            logger.error(f"Error updating chart: {str(e)}")
            with chart_container:
                ui.notify("차트 업데이트 중 오류가 발생했습니다.", type="negative")

    async def load_stock_details():
        try:
            async with AsyncSessionLocal() as db:
                stock_repo = StockRepository(db)
                stock = await stock_repo.get_by_ticker(ticker)
                if stock:
                    stock_info["name"] = stock.name
                    stock_info["ticker"] = stock.ticker
                    stock_info["market"] = stock.market
                    stock_info["country"] = stock.country
                    app.storage.user["stock_info"] = stock_info.copy()
                    ui.notify("종목 정보를 성공적으로 불러왔습니다.", type="positive")
                else:
                    with chart_container:
                        ui.notify(f"종목을 찾을 수 없습니다: {ticker}", type="negative")
                        ui.navigate.to("/")
        except Exception as e:
            logger.error(f"Error loading stock details: {str(e)}")
            with chart_container:
                ui.notify(
                    "종목 정보를 불러오는 중 오류가 발생했습니다.", type="negative"
                )

    # 비동기로 데이터 로드
    await load_stock_details()
