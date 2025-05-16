from datetime import datetime
import platform
import psutil

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.session import get_db


router = APIRouter()


@router.get("")
@router.get("/")
def health_check(db: Session = Depends(get_db)):
    # 시스템 정보
    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "memory_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
    }

    # 데이터베이스 연결 확인
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # 애플리케이션 정보
    app_info = {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "development",  # TODO: 환경 변수로 설정
        "timestamp": datetime.utcnow().isoformat(),
    }

    return {
        "status": "healthy",
        "system": system_info,
        "database": db_status,
        "application": app_info,
    }


@router.get("/ping")
def ping():
    """간단한 ping/pong 체크"""
    return {"ping": "pong"}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """서비스 준비 상태 확인"""
    try:
        # 데이터베이스 연결 확인
        db.execute(text("SELECT 1"))
        db_ready = True
    except Exception:
        db_ready = False

    return {
        "status": "ready" if db_ready else "not ready",
        "database": "connected" if db_ready else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
    }
