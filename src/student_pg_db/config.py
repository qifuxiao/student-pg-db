"""
数据库配置（支持通过 .env / .env.test / .env.prod 文件切换）
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

def _setup_env():
    """
    根据 APP_ENV 加载对应的 .env 文件
    """
    env = os.getenv("APP_ENV", "dev").lower()

    if env == "prod":
        env_file = ".env.prod"
    elif env == "test":
        env_file = ".env.test"
    else:
        env_file = ".env"

    env_path = Path(".") / env_file

    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)

_setup_env()

@dataclass(frozen=True)
class _DBProfile:
    host: str
    port: int
    admin_user: str
    admin_password: str
    admin_db: str
    app_db_name: str
    app_user: str
    app_password: str


class DatabaseConfig:
    """
    数据库配置中心（统一对外接口：sync_url / async_url）
    """

    @classmethod
    def _load_profile(cls) -> _DBProfile:
        return _DBProfile(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", 5432)),
            admin_user=os.getenv("DB_ADMIN_USER", "postgres"),
            admin_password=os.getenv("DB_ADMIN_PASSWORD", "123456"),
            admin_db=os.getenv("DB_ADMIN_DB", "postgres"),
            app_db_name=os.getenv("DB_NAME", "student_management"),
            app_user=os.getenv("DB_USER", "student_app"),
            app_password=os.getenv("DB_PASSWORD", "student_secure_pass"),
        )

    # ========= 推荐统一接口 =========

    @property
    def sync_url(self) -> str:
        """
        SQLAlchemy 同步引擎连接串（Alembic / 同步 ORM 使用）
        """
        p = self._load_profile()
        return (
            f"postgresql+psycopg2://"
            f"{p.app_user}:{p.app_password}@"
            f"{p.host}:{p.port}/{p.app_db_name}"
        )

    @property
    def async_url(self) -> str:
        """
        SQLAlchemy Async 引擎连接串（未来 async ORM 使用）
        """
        p = self._load_profile()
        return (
            f"postgresql+asyncpg://"
            f"{p.app_user}:{p.app_password}@"
            f"{p.host}:{p.port}/{p.app_db_name}"
        )

    # ========= 向后兼容（避免你现有代码全部改动） =========

    @classmethod
    def get_sqlalchemy_url(cls) -> str:
        """
        向后兼容旧接口（内部转 sync_url）
        """
        return cls().sync_url

    @classmethod
    def get_admin_connection_string(cls) -> str:
        p = cls._load_profile()
        return (
            f"host={p.host} "
            f"port={p.port} "
            f"dbname={p.admin_db} "
            f"user={p.admin_user} "
            f"password={p.admin_password}"
        )

    @classmethod
    def get_app_connection_string(cls) -> str:
        p = cls._load_profile()
        return (
            f"host={p.host} "
            f"port={p.port} "
            f"dbname={p.app_db_name} "
            f"user={p.app_user} "
            f"password={p.app_password}"
        )
