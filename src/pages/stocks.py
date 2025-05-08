import sys  # Import sys for flush=True
import logging
from nicegui import ui
from src.db.session import get_db
from src.db.repositories.stock import StockRepository
from uuid import UUID
import FinanceDataReader as fdr
import yfinance as yf
from src.models.stock import Stock

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

        # 업데이트 버튼 컨테이너
        with ui.row().classes("w-full max-w-2xl justify-center gap-4 mb-4"):

            def update_kr_stocks():
                try:
                    ui.notify("한국 ETF 목록 업데이트를 시작합니다.", type="info")
                    # FinanceDataReader로 주식 정보 조회
                    stock_info = fdr.StockListing("ETF/KR")

                    # KODEX와 TIGER ETF만 필터링
                    etf_info = stock_info[
                        stock_info["Name"].str.startswith(("KODEX", "TIGER"), na=False)
                    ]

                    # 기존 주식 목록 가져오기
                    existing_stocks = {
                        stock.ticker: stock for stock in stock_repo.get_all()
                    }

                    # 진행 상황 표시
                    progress = ui.linear_progress().classes("w-full")
                    progress.value = 0
                    total_etfs = len(etf_info)

                    def process_etf(row, index):
                        try:
                            ticker = row["Symbol"]
                            name = row["Name"]
                            category = row["Category"] if "Category" in row else "N/A"
                            price = row["Price"] if "Price" in row else "N/A"
                            change_rate = (
                                row["ChangeRate"] if "ChangeRate" in row else "N/A"
                            )

                            if ticker in existing_stocks:
                                # 기존 ETF 업데이트
                                stock = existing_stocks[ticker]
                                stock.name = name
                                stock.market = "ETF"  # ETF로 고정
                                stock_repo.update(stock)
                                logger.info(f"Updated ETF: {ticker} - {name}")
                            else:
                                # 새로운 ETF 추가
                                new_stock = Stock(
                                    ticker=ticker,
                                    name=name,
                                    country="KR",
                                    market="ETF",  # ETF로 고정
                                )
                                stock_repo.create(new_stock)
                                logger.info(f"Added new ETF: {ticker} - {name}")

                            # 진행률 업데이트
                            progress.value = (index + 1) / total_etfs

                        except Exception as e:
                            logger.error(f"Error processing ETF {ticker}: {str(e)}")
                            ui.notify(
                                f"ETF {ticker} 처리 중 오류 발생: {str(e)}",
                                type="negative",
                            )

                    # 모든 ETF를 순차적으로 처리
                    for i, (_, row) in enumerate(etf_info.iterrows()):
                        process_etf(row, i)

                    # 진행 표시줄 제거
                    progress.delete()

                    ui.notify(
                        "한국 ETF 목록이 성공적으로 업데이트되었습니다.",
                        type="positive",
                    )
                    refresh_stocks()  # 목록 새로고침

                except Exception as e:
                    logger.error(f"Error updating KR ETFs: {str(e)}")
                    ui.notify(
                        "한국 ETF 목록 업데이트 중 오류가 발생했습니다.",
                        type="negative",
                    )

            def update_ca_stocks():
                try:
                    ui.notify("캐나다 ETF 목록 업데이트를 시작합니다.", type="info")

                    # 캐나다 주요 ETF 목록
                    ca_etf_tickers = [
                        # 레버리지 ETF
                        "HXU.TO",  # Horizons S&P/TSX 60 Bull Plus ETF (2x)
                        "HXD.TO",  # Horizons S&P/TSX 60 Bear Plus ETF (-2x)
                    ]

                    # 기존 주식 목록 가져오기
                    existing_stocks = {
                        stock.ticker: stock for stock in stock_repo.get_all()
                    }

                    # 진행 상황 표시
                    progress = ui.linear_progress().classes("w-full")
                    progress.value = 0
                    total_etfs = len(ca_etf_tickers)

                    def process_etf(ticker: str, index: int):
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
                                stock_repo.update(stock)
                                logger.info(f"Updated ETF: {ticker} - {name}")
                            else:
                                # 새로운 ETF 추가
                                new_stock = Stock(
                                    ticker=ticker,
                                    name=name,
                                    country="CA",
                                    market=market,
                                )
                                stock_repo.create(new_stock)
                                logger.info(f"Added new ETF: {ticker} - {name}")

                            # 진행률 업데이트
                            progress.value = (index + 1) / total_etfs

                        except Exception as e:
                            logger.error(f"Error processing ETF {ticker}: {str(e)}")
                            ui.notify(
                                f"ETF {ticker} 처리 중 오류 발생: {str(e)}",
                                type="negative",
                            )

                    # 모든 ETF를 순차적으로 처리
                    for i, ticker in enumerate(ca_etf_tickers):
                        process_etf(ticker, i)

                    # 진행 표시줄 제거
                    progress.delete()

                    ui.notify(
                        "캐나다 ETF 목록이 성공적으로 업데이트되었습니다.",
                        type="positive",
                    )
                    refresh_stocks()  # 목록 새로고침

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

        # 정렬 상태를 저장할 변수
        sort_column = "name"
        sort_direction = "asc"

        # 주식 목록 새로고침 함수
        def refresh_stocks():
            logger.info("Refreshing stocks list")
            print("--- refresh_stocks CALLED ---", flush=True)

            stocks = stock_repo.get_all()

            # 정렬 적용
            stocks = sorted(
                stocks,
                key=lambda x: getattr(x, sort_column),
                reverse=(sort_direction == "desc"),
            )

            # 테이블 데이터 생성
            rows = []
            for stock in stocks:
                rows.append(
                    {
                        "name": stock.name,
                        "ticker": stock.ticker,
                        "market": stock.market,
                        "country": COUNTRIES.get(stock.country, stock.country),
                    }
                )

            table.rows = rows
            table.update()  # 테이블 UI 업데이트

        # 테이블 정렬 이벤트 핸들러
        def on_sort(e):
            nonlocal sort_column, sort_direction
            sort_column = e.args["column"]
            sort_direction = "desc" if e.args["direction"] == "desc" else "asc"
            refresh_stocks()

        # 종목 상세 정보 팝업 표시 함수 (rowClick 이벤트 GenericEventArguments 대응)
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
            # 테이블 생성 (이벤트 파라미터 없이)
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

            # 이벤트 핸들러 연결 (NiceGUI 2.7.0 방식)
            table.on("rowClick", show_stock_details)
            table.on("sort", on_sort)
        refresh_stocks()
