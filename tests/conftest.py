'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-13 07:02:36
FilePath: /student_pg_db/tests/conftest.py
'''
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from student_pg_db.models.base import Base
from student_pg_db.utils.data_generator import DataGenerator
from student_pg_db.config import DatabaseConfig

@pytest.fixture(scope="session")
def db_engine():
    """创建测试数据库引擎"""
    config = DatabaseConfig()
    # 确保使用的是测试数据库连接
    engine = create_engine(config.sync_url)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    """为每个测试提供独立的数据库事务"""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def generator():
    """提供数据生成器实例"""
    return DataGenerator()