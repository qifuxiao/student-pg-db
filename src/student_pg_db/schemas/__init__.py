'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-12 04:00:27
FilePath: /student_pg_db/src/student_pg_db/schemas/__init__.py
'''
"""
Schema 层公共导出
用途：统一管理 Pydantic 模型导出，避免循环依赖
"""
# 学生相关 Schema
from .student import (
    StudentBase,
    StudentCreate,
    StudentUpdate,
    StudentInDBBase,
    Student,
    StudentListResponse,
    StudentQuery,
    GenderEnum,
    StudentStatusEnum
)

__all__ = [
    # 枚举
    "GenderEnum",
    "StudentStatusEnum",
    # 基础 Schema
    "StudentBase",
    # 输入 Schema
    "StudentCreate",
    "StudentUpdate",
    "StudentQuery",
    # 输出 Schema
    "StudentInDBBase",
    "Student",
    "StudentListResponse",
]