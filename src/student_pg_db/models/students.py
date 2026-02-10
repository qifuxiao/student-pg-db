'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 11:06:30
FilePath: /student_pg_db/src/student_pg_db/models/students.py
'''
from pydantic import model_validator, Field, field_validator, EmailStr, ConfigDict, StringConstraints
from datetime import date, datetime
from typing import Optional
from enum import Enum
from typing_extensions import Annotated
from .base import BaseDBModel

class StudentStatus(str, Enum):
    ACTIVE = "active"
    GRADUATED = "graduated"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"

class Student(BaseDBModel):
    """学生数据模型"""
    
    id: Optional[int] = None
    # 统一将 VARCHAR 长度限制提升到 100，确保与数据库修改同步
    student_id: Annotated[str, StringConstraints(max_length=100)]
    name: Annotated[str, StringConstraints(max_length=100)]
    gender: str = Field(..., pattern="^(male|female|other)$")
    date_of_birth: date = Field(..., description="出生日期")
    enrollment_date: date = Field(default_factory=date.today)
    major: Annotated[str, StringConstraints(max_length=100)]
    class_name: Annotated[str, StringConstraints(max_length=50)]
    
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?1?\d{9,15}$")
    address: Optional[str] = Field(None, max_length=500)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    status: StudentStatus = Field(default=StudentStatus.ACTIVE)
    scholarship_amount: float = Field(default=0.0, ge=0)
    
    emergency_contact_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    emergency_contact_phone: Optional[str] = Field(None, pattern=r"^\+?1?\d{9,15}$")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v: date) -> date:
        age = (date.today() - v).days // 365
        if not (15 <= age <= 30):
            raise ValueError('年龄须在15-30岁之间')
        return v

    @model_validator(mode='after')
    def validate_date_logic(self) -> 'Student':
        """跨字段校验：入学日期 vs 出生日期"""
        # 注意：V2 模式下，self 已经是模型实例，直接访问属性即可
        if self.enrollment_date <= self.date_of_birth:
            raise ValueError("入学日期必须晚于出生日期")
        return self
    model_config = ConfigDict(from_attributes=True)