'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-10 08:38:53
FilePath: /student_pg_db/src/student_pg_db/core/session.py
'''


from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..config import DatabaseConfig

# 1. 创建引擎（包含连接池配置）
engine = create_engine(
    DatabaseConfig().sync_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# 2. 创建 Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from contextlib import contextmanager

@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
def get_session() -> Generator[Session, None, None]:
    with session_scope() as session:
        yield session