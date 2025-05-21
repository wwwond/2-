# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

# db 
SQLALCHEMY_DATABASE_URL = "oracle+oracledb://GD:gdgd@210.119.12.114:1521/xe"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── 기존에 직접 정의할 모델용 Base ──────────
Base = declarative_base()

# ── 자동 매핑용 Base (Reflect) ─────────────
AutoBase = automap_base()
# engine에 연결된 DB의 모든 테이블을 읽어서 클래스로 생성
AutoBase.prepare(engine, reflect=True)

# 이제 아래처럼 사용 가능:
#   from database import AutoBase, SessionLocal
#   HobbyTag = AutoBase.classes.hobby_tag
#   session = SessionLocal()
#   tags = session.query(HobbyTag).all()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
