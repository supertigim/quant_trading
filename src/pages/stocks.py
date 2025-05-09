import sys  # Import sys for flush=True
import logging
from nicegui import ui
from src.db.session import AsyncSessionLocal
from src.db.repositories.stock import StockRepository
from uuid import UUID
import FinanceDataReader as fdr
import yfinance as yf
from src.models.stock import Stock
from src.services.stock_service import StockService
from src.schemas.stock import StockCreate, StockUpdate
from sqlalchemy import select, desc, asc
from typing import Optional, List
from datetime import datetime
import asyncio
from nicegui.events import ValueChangeEventArguments

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_stocks_page():
    # 국가 선택을 위한 상수
    COUNTRIES = {"KR": "한국", "US": "미국", "CA": "캐나다"}

    # 검색 필터 상태
    search_keyword = ""
    search_ticker = ""
    sort_column = "ticker"
    sort_direction = "asc"

    # 중앙 정렬을 위한 컨테이너
    with ui.column().classes("w-full items-center gap-4"):
        # 제목 추가
        ui.label("주식 목록").classes("text-2xl font-bold")

        # 업데이트 버튼 컨테이너
        with ui.row().classes("w-full max-w-2xl justify-center gap-4 mb-4"):

            async def update_kr_stocks():
                try:
                    ui.notify("한국 ETF 목록 업데이트를 시작합니다.", type="info")
                    # FinanceDataReader로 주식 정보 조회
                    stock_info = fdr.StockListing("ETF/KR")

                    # KODEX와 TIGER ETF만 필터링
                    etf_info = stock_info[
                        stock_info["Name"].str.startswith(("KODEX", "TIGER"), na=False)
                    ]

                    async with AsyncSessionLocal() as db:
                        stock_repo = StockRepository(db)
                        # 기존 주식 목록 가져오기
                        existing_stocks = {
                            stock.ticker: stock for stock in await stock_repo.get_all()
                        }

                        # 진행 상황 표시
                        progress = ui.linear_progress().classes("w-full")
                        progress.value = 0
                        total_etfs = len(etf_info)

                        for i, (_, row) in enumerate(etf_info.iterrows()):
                            try:
                                ticker = row["Symbol"]
                                name = row["Name"]
                                category = (
                                    row["Category"] if "Category" in row else "N/A"
                                )
                                price = row["Price"] if "Price" in row else "N/A"
                                change_rate = (
                                    row["ChangeRate"] if "ChangeRate" in row else "N/A"
                                )

                                if ticker in existing_stocks:
                                    # 기존 ETF 업데이트
                                    stock = existing_stocks[ticker]
                                    stock.name = name
                                    stock.market = "ETF"  # ETF로 고정
                                    await stock_repo.update(stock)
                                    logger.info(f"Updated ETF: {ticker} - {name}")
                                else:
                                    # 새로운 ETF 추가
                                    new_stock = Stock(
                                        ticker=ticker,
                                        name=name,
                                        country="KR",
                                        market="ETF",  # ETF로 고정
                                    )
                                    await stock_repo.create(new_stock)
                                    logger.info(f"Added new ETF: {ticker} - {name}")

                                # 진행률 업데이트
                                progress.value = (i + 1) / total_etfs

                            except Exception as e:
                                logger.error(f"Error processing ETF {ticker}: {str(e)}")
                                ui.notify(
                                    f"ETF {ticker} 처리 중 오류 발생: {str(e)}",
                                    type="negative",
                                )

                        # 진행 표시줄 제거
                        progress.delete()

                        ui.notify(
                            "한국 ETF 목록이 성공적으로 업데이트되었습니다.",
                            type="positive",
                        )
                        await refresh_stocks()

                except Exception as e:
                    logger.error(f"Error updating KR ETFs: {str(e)}")
                    ui.notify(
                        "한국 ETF 목록 업데이트 중 오류가 발생했습니다.",
                        type="negative",
                    )

            async def update_ca_stocks():
                try:
                    ui.notify("캐나다 ETF 목록 업데이트를 시작합니다.", type="info")

                    # 캐나다 주요 ETF 목록
                    ca_etf_tickers = [
                        # 레버리지 ETF
                        "HXU.TO",  # Horizons S&P/TSX 60 Bull Plus ETF (2x)
                        "HXD.TO",  # Horizons S&P/TSX 60 Bear Plus ETF (-2x)
                    ]

                    async with AsyncSessionLocal() as db:
                        stock_repo = StockRepository(db)
                        # 기존 주식 목록 가져오기
                        existing_stocks = {
                            stock.ticker: stock for stock in await stock_repo.get_all()
                        }

                        # 진행 상황 표시
                        progress = ui.linear_progress().classes("w-full")
                        progress.value = 0
                        total_etfs = len(ca_etf_tickers)

                        for i, ticker in enumerate(ca_etf_tickers):
                            try:
                                # 개별 ETF 정보 가져오기
                                stock_info = yf.Ticker(ticker)

                                # 타임아웃 처리를 위한 재시도 로직
                                max_retries = 3
                                retry_count = 0
                                info = None

                                while retry_count < max_retries and info is None:
                                    try:
                                        info = stock_info.info
                                        if not info:
                                            raise ValueError("No info available")
                                    except Exception as e:
                                        retry_count += 1
                                        if retry_count == max_retries:
                                            raise e
                                        logger.warning(
                                            f"Retry {retry_count} for {ticker}: {str(e)}"
                                        )
                                        continue

                                name = info.get("longName", ticker)
                                market = "TSX"

                                if ticker in existing_stocks:
                                    # 기존 ETF 업데이트
                                    stock = existing_stocks[ticker]
                                    stock.name = name
                                    stock.market = market
                                    await stock_repo.update(stock)
                                    logger.info(f"Updated ETF: {ticker} - {name}")
                                else:
                                    # 새로운 ETF 추가
                                    new_stock = Stock(
                                        ticker=ticker,
                                        name=name,
                                        country="CA",
                                        market=market,
                                    )
                                    await stock_repo.create(new_stock)
                                    logger.info(f"Added new ETF: {ticker} - {name}")

                                # 진행률 업데이트
                                progress.value = (i + 1) / total_etfs

                            except Exception as e:
                                logger.error(f"Error processing ETF {ticker}: {str(e)}")
                                ui.notify(
                                    f"ETF {ticker} 처리 중 오류 발생: {str(e)}",
                                    type="negative",
                                )

                        # 진행 표시줄 제거
                        progress.delete()

                        ui.notify(
                            "캐나다 ETF 목록이 성공적으로 업데이트되었습니다.",
                            type="positive",
                        )
                        await refresh_stocks()

                except Exception as e:
                    logger.error(f"Error updating CA ETFs: {str(e)}")
                    ui.notify(
                        "캐나다 ETF 목록 업데이트 중 오류가 발생했습니다.",
                        type="negative",
                    )

            ui.button("한국 ETF 목록 업데이트", on_click=update_kr_stocks).classes(
                "bg-blue-500 hover:bg-blue-600 text-white"
            )
            ui.button("캐나다 주식 목록 업데이트", on_click=update_ca_stocks).classes(
                "bg-blue-500 hover:bg-blue-600 text-white"
            )

        # 검색 필터 추가
        with ui.row().classes("w-full max-w-2xl gap-4 mb-4"):
            with ui.input(
                label="종목명 검색", placeholder="검색어를 입력하세요"
            ).classes("w-1/2") as keyword_input:

                def on_keyword_change(e):
                    nonlocal search_keyword
                    search_keyword = e.value.lower()
                    asyncio.create_task(refresh_stocks())

                keyword_input.on("update", on_keyword_change)

            with ui.input(label="티커 검색", placeholder="티커를 입력하세요").classes(
                "w-1/2"
            ) as ticker_input:

                def on_ticker_change(e):
                    nonlocal search_ticker
                    search_ticker = e.value.lower()
                    asyncio.create_task(refresh_stocks())

                ticker_input.on("update", on_ticker_change)

        # 테이블 컨테이너
        table_container = ui.column().classes("w-full max-w-2xl gap-2")

        # 테이블 컬럼 정의
        columns = [
            {
                "name": "name",
                "label": "종목명",
                "field": "name",
                "align": "left",
                "sortable": True,
                "width": 300,
            },
            {
                "name": "ticker",
                "label": "티커",
                "field": "ticker",
                "align": "left",
                "sortable": True,
                "width": 120,
            },
            {
                "name": "market",
                "label": "마켓",
                "field": "market",
                "align": "left",
                "sortable": True,
                "width": 100,
            },
            {
                "name": "country",
                "label": "국가",
                "field": "country",
                "align": "left",
                "sortable": True,
                "width": 100,
            },
        ]

        # 주식 목록 새로고침 함수
        async def refresh_stocks():
            try:
                logger.info("Refreshing stocks list")
                print("--- refresh_stocks CALLED ---", flush=True)

                async with AsyncSessionLocal() as db:
                    stock_repo = StockRepository(db)
                    # 모든 주식 가져오기
                    stocks = await stock_repo.get_all()

                    # 검색어로 필터링
                    if search_keyword:
                        stocks = [s for s in stocks if search_keyword in s.name.lower()]
                    if search_ticker:
                        stocks = [
                            s for s in stocks if search_ticker in s.ticker.lower()
                        ]

                    # 정렬 적용
                    stocks = sorted(
                        stocks,
                        key=lambda x: getattr(x, sort_column),
                        reverse=(sort_direction == "desc"),
                    )

                    # 테이블 데이터 업데이트
                    with table:
                        table.rows = [
                            {
                                "name": stock.name,
                                "ticker": stock.ticker,
                                "market": stock.market,
                                "country": COUNTRIES.get(stock.country, stock.country),
                                "last_updated": (
                                    stock.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                                    if stock.last_updated
                                    else "-"
                                ),
                            }
                            for stock in stocks
                        ]
                        table.update()  # 테이블 UI 업데이트
            except Exception as e:
                logger.error(f"Error refreshing stocks: {str(e)}")
                with table:
                    ui.notify(
                        "주식 목록을 새로고침하는 중 오류가 발생했습니다.",
                        type="negative",
                    )

        # 테이블 정렬 이벤트 핸들러
        def on_sort(e):
            nonlocal sort_column, sort_direction
            sort_column = e.args["column"]
            sort_direction = e.args["direction"]
            asyncio.create_task(refresh_stocks())

        # 종목 상세 정보 팝업 표시 함수
        def show_stock_details(e):
            try:
                logger.info(f"###### {e.args}")
                # row 데이터는 e.args[1]에 있음
                row = (
                    e.args[1] if isinstance(e.args, list) and len(e.args) > 1 else None
                )
                if not row or "ticker" not in row:
                    logger.info("rowClick: no row data")
                    return
                logger.info(f"rowClick: {row}")
                ui.notify(f"Clicked: {row['name']} ({row['ticker']})")
                with ui.dialog() as dialog, ui.card().classes("w-[600px] p-4"):
                    ui.label(f"종목 상세 정보").classes("text-xl font-bold mb-4")
                    with ui.column().classes("gap-2"):
                        ui.label(f"종목명: {row['name']}").classes("text-lg")
                        ui.label(f"티커: {row['ticker']}").classes("text-lg")
                        ui.label(f"마켓: {row['market']}").classes("text-lg")
                        ui.label(f"국가: {row['country']}").classes("text-lg")
                        ui.separator().classes("my-4")
                        ui.label("추가 정보").classes("text-lg font-bold mb-2")
                        ui.label("추가 정보는 추후 구현 예정입니다.").classes(
                            "text-gray-500"
                        )
                    with ui.row().classes("w-full justify-end mt-4"):
                        ui.button("닫기", on_click=dialog.close).classes(
                            "bg-blue-500 text-white"
                        )
                dialog.open()
            except Exception as e:
                logger.error(f"Error showing stock details: {str(e)}")
                ui.notify(
                    "상세 정보를 표시하는 중 오류가 발생했습니다.", type="negative"
                )

        # 테이블 컨테이너
        with ui.card().classes("w-full max-w-2xl"):
            # 테이블 생성
            table = ui.table(
                columns=columns, rows=[], row_key="ticker", pagination=False
            ).classes("w-full h-[600px]")

            # 테이블 스타일 설정
            table.classes(
                """
                [&_.q-table__top]:p-2
                [&_.q-table__bottom]:p-2
                [&_thead_tr_th]:bg-gray-100
                [&_thead_tr_th]:font-bold
                [&_thead_tr_th]:text-gray-900
                [&_tbody_tr:hover]:bg-gray-50
                [&_td]:text-center
                dark:[&_thead_tr_th]:bg-gray-800
                dark:[&_thead_tr_th]:text-gray-100
                dark:[&_tbody_tr]:text-gray-100
                dark:[&_tbody_tr:hover]:bg-gray-700
                """
            )

            # 이벤트 핸들러 연결
            table.on("rowClick", show_stock_details)
            table.on("sort", on_sort)

        # 초기 데이터 로드
        asyncio.create_task(refresh_stocks())


class StockPage:
    def __init__(self):
        self.stock_service = StockService()
        self.stocks: List[Stock] = []
        self.sort_column = "ticker"
        self.sort_direction = "asc"
        self.selected_stock: Optional[Stock] = None
        self.search_keyword = ""
        self.search_ticker = ""

    def create(self):
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full justify-between items-center"):
                ui.label("주식 종목 관리").classes("text-2xl font-bold")
                with ui.row().classes("gap-2"):
                    ui.button("새 종목 추가", on_click=self.show_add_dialog).props(
                        "color=primary"
                    )
                    ui.button("전체 업데이트", on_click=self.update_all_stocks).props(
                        "color=secondary"
                    )

            # 검색 필터 추가
            with ui.row().classes("w-full gap-4 mb-4"):
                with ui.input(
                    label="종목명 검색", placeholder="검색어를 입력하세요"
                ).classes("w-1/3") as self.keyword_input:
                    self.keyword_input.on("update", self.on_search)
                with ui.input(
                    label="티커 검색", placeholder="티커를 입력하세요"
                ).classes("w-1/3") as self.ticker_input:
                    self.ticker_input.on("update", self.on_search)

            with ui.table().classes("w-full") as self.table:
                self.table.add_columns(
                    [
                        {
                            "name": "ticker",
                            "label": "티커",
                            "field": "ticker",
                            "sortable": True,
                            "align": "left",
                        },
                        {
                            "name": "name",
                            "label": "종목명",
                            "field": "name",
                            "sortable": True,
                            "align": "left",
                        },
                        {
                            "name": "country",
                            "label": "국가",
                            "field": "country",
                            "sortable": True,
                            "align": "left",
                        },
                        {
                            "name": "last_updated",
                            "label": "마지막 업데이트",
                            "field": "last_updated",
                            "sortable": True,
                            "align": "left",
                        },
                    ]
                )
                self.table.on("rowClick", self.on_row_click)
                self.table.on("sort", self.on_sort)

            self.load_stocks()

    def on_search(self, e: ValueChangeEventArguments):
        """검색어 변경 시 호출되는 함수"""
        if e.sender == self.keyword_input:
            self.search_keyword = e.value.lower()
        elif e.sender == self.ticker_input:
            self.search_ticker = e.value.lower()
        self.load_stocks()

    def filter_stocks(self, stocks: List[Stock]) -> List[Stock]:
        """검색어와 티커로 주식 목록을 필터링"""
        filtered = stocks
        if self.search_keyword:
            filtered = [s for s in filtered if self.search_keyword in s.name.lower()]
        if self.search_ticker:
            filtered = [s for s in filtered if self.search_ticker in s.ticker.lower()]
        return filtered

    async def load_stocks(self):
        """주식 목록을 로드하고 필터링하여 표시"""
        self.stocks = await self.stock_service.get_all_stocks()

        # 정렬 적용
        if self.sort_direction == "asc":
            self.stocks.sort(key=lambda x: getattr(x, self.sort_column))
        else:
            self.stocks.sort(key=lambda x: getattr(x, self.sort_column), reverse=True)

        # 필터링 적용
        filtered_stocks = self.filter_stocks(self.stocks)

        # 테이블 데이터 업데이트
        self.table.rows = [
            {
                "ticker": stock.ticker,
                "name": stock.name,
                "country": stock.country,
                "last_updated": (
                    stock.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    if stock.last_updated
                    else "-"
                ),
            }
            for stock in filtered_stocks
        ]
