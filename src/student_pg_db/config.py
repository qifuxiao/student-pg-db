'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 09:40:47
FilePath: /student_pg_db/src/student_pg_db/config.py
'''
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """数据库配置类"""
    
    # 基础连接参数（用于创建数据库）
    HOST = os.getenv("DB_HOST", "127.0.0.1")
    PORT = int(os.getenv("DB_PORT", 5432))
    ADMIN_USER = os.getenv("DB_ADMIN_USER", "postgres")
    ADMIN_PASSWORD = os.getenv("DB_ADMIN_PASSWORD", "123456")
    ADMIN_DB = os.getenv("DB_ADMIN_DB", "postgres")
    
    # 应用数据库参数
    APP_DB_NAME = os.getenv("DB_NAME", "student_management")
    APP_USER = os.getenv("DB_USER", "student_app")
    APP_PASSWORD = os.getenv("DB_PASSWORD", "student_secure_pass")
    
    @classmethod
    def get_admin_connection_string(cls) -> str:
        """获取管理员连接字符串"""
        return f"host={cls.HOST} port={cls.PORT} dbname={cls.ADMIN_DB} user={cls.ADMIN_USER} password={cls.ADMIN_PASSWORD}"
    
    @classmethod
    def get_app_connection_string(cls) -> str:
        """获取应用连接字符串"""
        return f"host={cls.HOST} port={cls.PORT} dbname={cls.APP_DB_NAME} user={cls.APP_USER} password={cls.APP_PASSWORD}"