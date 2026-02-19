'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 11:06:30
FilePath: /student_pg_db/src/student_pg_db/models/students.py
'''
from sqlalchemy import String, Integer, Date, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base,TimestampMixin


from sqlalchemy import String, Integer, Date, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="自增主键ID"
    )
    student_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="学号，唯一标识符"
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="学生姓名"
    )
    gender: Mapped[str | None] = mapped_column(
        String(10), comment="性别，取值范围：male, female, other"
    )
    date_of_birth: Mapped[str] = mapped_column(
        Date, nullable=False, comment="出生日期"
    )
    enrollment_date: Mapped[str] = mapped_column(
        Date, server_default=func.current_date(), comment="入学日期"
    )
    major: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="所属专业名称"
    )
    class_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="行政班级名称，例如：计算机2401班"
    )
    email: Mapped[str | None] = mapped_column(
        String(100), comment="电子邮箱地址"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), comment="联系电话/手机号"
    )
    address: Mapped[str | None] = mapped_column(
        Text, comment="家庭或通讯详细地址"
    )
    gpa: Mapped[float | None] = mapped_column(
        Numeric(3, 2), comment="平均学分绩点（GPA），范围0.00-4.00"
    )
    status: Mapped[str] = mapped_column(
        String(32), server_default="active", comment="学籍状态：active(在读), inactive(休学/离校), graduated(毕业)"
    )
