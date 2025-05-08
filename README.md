# Quantitative Trading System

NiceGUI와 PostgreSQL을 사용한 정량적 트레이딩 시스템입니다.

## 사전 요구사항

- Docker
- Docker Compose
- Poetry (로컬 개발용)

## 설치 및 실행

1. 저장소 클론:
```bash
git clone <repository-url>
cd quant-trading
```

2. 환경 설정:
```bash
# .env.example을 .env로 복사
cp .env.example .env
# 필요한 경우 .env 파일의 설정값 수정
```

3. Docker Compose로 실행:
```bash
docker-compose up --build
```

애플리케이션은 http://localhost:8080 에서 접속할 수 있습니다.

## 데이터베이스 사용

### 1. 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 마이그레이션을 관리합니다:

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "migration message"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1  # 한 단계 롤백
alembic downgrade base  # 처음으로 롤백
```

### 2. 모델 정의

`src/models` 디렉토리에 SQLAlchemy 모델을 정의합니다:

```python
from src.models.base import BaseModel
from sqlalchemy import Column, String, Float

class Stock(BaseModel):
    __tablename__ = "stocks"

    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
```

### 3. 스키마 정의

`src/schemas` 디렉토리에 Pydantic 스키마를 정의합니다:

```python
from pydantic import BaseModel
from datetime import datetime

class StockBase(BaseModel):
    symbol: str
    name: str
    price: float

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 4. 리포지토리 패턴

`src/db/repositories` 디렉토리에 데이터베이스 작업을 처리하는 리포지토리를 정의합니다:

```python
from sqlalchemy.orm import Session
from src.models.stock import Stock
from src.schemas.stock import StockCreate

class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, stock: StockCreate) -> Stock:
        db_stock = Stock(**stock.model_dump())
        self.db.add(db_stock)
        self.db.commit()
        self.db.refresh(db_stock)
        return db_stock

    def get_by_symbol(self, symbol: str) -> Stock:
        return self.db.query(Stock).filter(Stock.symbol == symbol).first()
```

### 5. 서비스 레이어

`src/services` 디렉토리에 비즈니스 로직을 처리하는 서비스를 정의합니다:

```python
from src.db.repositories.stock import StockRepository
from src.schemas.stock import StockCreate, Stock

class StockService:
    def __init__(self, stock_repository: StockRepository):
        self.stock_repository = stock_repository

    def create_stock(self, stock: StockCreate) -> Stock:
        return self.stock_repository.create(stock)

    def get_stock(self, symbol: str) -> Stock:
        return self.stock_repository.get_by_symbol(symbol)
```

### 6. API 엔드포인트

`src/api/v1/endpoints` 디렉토리에 API 엔드포인트를 정의합니다:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.services.stock import StockService
from src.schemas.stock import Stock, StockCreate

router = APIRouter()

@router.post("/stocks/", response_model=Stock)
def create_stock(
    stock: StockCreate,
    db: Session = Depends(get_db)
):
    stock_repository = StockRepository(db)
    stock_service = StockService(stock_repository)
    return stock_service.create_stock(stock)

@router.get("/stocks/{symbol}", response_model=Stock)
def get_stock(
    symbol: str,
    db: Session = Depends(get_db)
):
    stock_repository = StockRepository(db)
    stock_service = StockService(stock_repository)
    return stock_service.get_stock(symbol)
```

## 로컬 개발 환경 설정

1. Poetry 설치 (아직 설치하지 않은 경우):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. 의존성 설치:
```bash
poetry install
```

3. 애플리케이션 실행:
```bash
python src/main.py
```

## requirements.txt 생성 방법

Poetry를 사용하여 환경별 requirements.txt를 생성할 수 있습니다:

1. 자동 생성 (poetry install 또는 poetry add 실행 시):
```bash
# 모든 환경의 requirements 파일이 자동으로 생성됨
# - requirements/dev.txt
# - requirements/staging.txt
# - requirements/prod.txt
```

2. 수동으로 특정 환경의 requirements 파일만 생성:
```bash
# 개발 환경용
export-requirements dev

# 스테이징 환경용
export-requirements staging

# 프로덕션 환경용
export-requirements prod

# all
export-requirements all
```

각 환경별 특징:
- dev: 모든 의존성 포함 (개발, 테스트 도구 포함)
- staging: 개발 의존성 포함, 테스트 도구 제외
- prod: 필수 의존성만 포함

## 프로젝트 구조

```
.
├── src/                    # 소스 코드
│   ├── api/               # API 엔드포인트
│   │   └── v1/
│   ├── core/              # 핵심 설정
│   ├── db/                # 데이터베이스 관련
│   │   ├── migrations/    # Alembic 마이그레이션
│   │   └── repositories/  # 리포지토리 패턴
│   ├── models/            # SQLAlchemy 모델
│   ├── schemas/           # Pydantic 스키마
│   ├── services/          # 비즈니스 로직
│   └── utils/             # 유틸리티 함수
├── docker/                # Docker 관련 파일
│   └── Dockerfile.dev     # 개발용 Dockerfile
├── requirements/          # requirements 파일
│   ├── dev.txt           # 개발용 requirements
│   ├── staging.txt       # 스테이징용 requirements
│   └── prod.txt          # 프로덕션용 requirements
├── docker-compose.yml     # Docker Compose 설정
├── pyproject.toml        # Poetry 설정
└── README.md             # 프로젝트 문서
```

## 주요 기능

- NiceGUI 기반 웹 인터페이스
- PostgreSQL 데이터베이스 통합
- Docker 컨테이너화
- Poetry 의존성 관리
- Alembic 데이터베이스 마이그레이션
- 리포지토리 패턴
- 서비스 레이어 아키텍처

## 환경 변수

`.env` 파일에서 다음 환경 변수들을 설정할 수 있습니다:

```env
# PostgreSQL 설정
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=quant_trading
POSTGRES_HOST=db
POSTGRES_PORT=5432

# 애플리케이션 설정
APP_HOST=0.0.0.0
APP_PORT=8080

# 보안 설정
SECRET_KEY=your-secret-key-here
```

## 개발 가이드

1. 코드 스타일
   - Black을 사용한 코드 포맷팅
   - isort를 사용한 import 정렬
   - flake8을 사용한 코드 검사

2. 테스트
   - pytest를 사용한 테스트 실행
   ```bash
   pytest
   ```

3. 코드 포맷팅
   ```bash
   black .
   isort .
   ```

4. 코드 검사
   ```bash
   flake8
   ```
