'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 11:20:38
FilePath: /student_pg_db/src/student_pg_db/core/connection.py
'''
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator, Optional
from ..config import DatabaseConfig

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def connect(self, connection_string: str):
        """通用连接方法，支持断线重连"""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(connection_string)
                self._connection.autocommit = False # 默认显式事务
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                raise
        return self._connection

    def connect_admin(self):
        return self.connect(DatabaseConfig.get_admin_connection_string())

    def connect_app(self):
        return self.connect(DatabaseConfig.get_app_connection_string())

    @contextmanager
    def get_cursor(self) -> Generator:
        """上下文管理器：自动获取和关闭游标，处理异常"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            conn.commit() # 成功则提交
        except Exception:
            conn.rollback() # 失败则回滚
            raise
        finally:
            cursor.close()

    def get_connection(self):
        if not self._connection or self._connection.closed:
            raise ConnectionError("数据库未连接，请先调用 connect_admin 或 connect_app")
        return self._connection

    def close(self):
        """重要：显式关闭连接，修复测试报错"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None