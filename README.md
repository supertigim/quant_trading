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
poetry run python src/main.py
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
poetry run export-requirements dev

# 스테이징 환경용
poetry run export-requirements staging

# 프로덕션 환경용
poetry run export-requirements prod
```

각 환경별 특징:
- dev: 모든 의존성 포함 (개발, 테스트 도구 포함)
- staging: 개발 의존성 포함, 테스트 도구 제외
- prod: 필수 의존성만 포함

## 프로젝트 구조

```
.
├── src/                    # 소스 코드
│   └── main.py            # 메인 애플리케이션
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
```

## 개발 가이드

1. 코드 스타일
   - Black을 사용한 코드 포맷팅
   - isort를 사용한 import 정렬
   - flake8을 사용한 코드 검사

2. 테스트
   - pytest를 사용한 테스트 실행
   ```bash
   poetry run pytest
   ```

3. 코드 포맷팅
   ```bash
   poetry run black .
   poetry run isort .
   ```

4. 코드 검사
   ```bash
   poetry run flake8
   ```
