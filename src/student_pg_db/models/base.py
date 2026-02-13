'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-12 03:04:42
FilePath: /student_pg_db/src/student_pg_db/models/base.py
'''

from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import String, Integer, Date, Numeric, Text, func
from datetime import datetime

# 基础模型类，所有模型都继承自它
class Base(DeclarativeBase):
    pass
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(Date, server_default=func.current_date())
    updated_at: Mapped[datetime] = mapped_column(Date, server_default=func.current_date(), onupdate=func.current_date())
