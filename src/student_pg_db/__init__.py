'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 09:36:06
FilePath: /student_pg_db/src/student_pg_db/__init__.py
'''

__version__ = "1.0.0"
__author__ = "alexqi"
__license__ = "MIT"



# 公开API
try:
    from .config import DatabaseConfig
    from .database.repository import StudentRepository
    from .models.students import Student
    from .schemas.student import StudentStatusEnum
except ImportError as e:
    # 友好提示常见导入错误（便于调试）
    import sys
    print(f"⚠️  模块导入警告: {e}", file=sys.stderr)
    print("💡 请确保已运行: poetry install", file=sys.stderr)
    # 不抛出异常，允许部分功能可用（如版本查询）
__all__ = [
    "DatabaseConfig",
    "StudentRepository",
    "Student",
    "StudentStatusEnum",
    "__version__",
]