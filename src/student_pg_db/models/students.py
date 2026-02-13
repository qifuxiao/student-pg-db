'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 11:06:30
FilePath: /student_pg_db/src/student_pg_db/models/students.py
'''
from sqlalchemy import String, Integer, Date, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base,TimestampMixin


class Student(Base,TimestampMixin):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(10))
    date_of_birth: Mapped[str] = mapped_column(Date, nullable=False)
    enrollment_date: Mapped[str] = mapped_column(Date, server_default=func.current_date())
    major: Mapped[str] = mapped_column(String(100), nullable=False)
    class_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    gpa: Mapped[float | None] = mapped_column(Numeric(3, 2))
    status: Mapped[str] = mapped_column(String(32), server_default="active")
