"""
学生数据 Schema 层
职责：API 输入验证、输出序列化、业务规则校验
设计原则：
  1. 与 ORM 模型解耦（避免循环依赖）
  2. 字段验证前置（减少数据库错误）
  3. 明确输入/输出契约（提升 API 可维护性）
"""
from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import (
    BaseModel, 
    Field, 
    ConfigDict, 
    field_validator,
    computed_field,
    EmailStr
)
from enum import Enum


# ==================== 枚举定义（增强类型安全） ====================
class GenderEnum(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class StudentStatusEnum(str, Enum):
    """学生状态枚举"""
    ACTIVE = "active"
    GRADUATED = "graduated"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"


# ==================== 基础 Schema（公共字段） ====================
class StudentBase(BaseModel):
    """学生基础信息（创建/更新共享）"""
    student_id: str = Field(
        ...,
        min_length=5,
        max_length=64,
        pattern=r"^[A-Z]\d{4,}$",  # 格式: S2024001
        description="学号（字母+数字，如 S2024001）",
        examples=["S2024001", "CS2023123"]
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="学生姓名",
        examples=["张三", "李四"]
    )
    gender: Optional[GenderEnum] = Field(
        None,
        description="性别",
        examples=["male", "female"]
    )
    date_of_birth: date = Field(
        ...,
        description="出生日期",
        examples=["2005-08-15"]
    )
    enrollment_date: Optional[date] = Field(
        None,
        description="入学日期（默认当前日期）",
        examples=["2023-09-01"]
    )
    major: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="专业名称",
        examples=["计算机科学与技术", "人工智能"]
    )
    class_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="班级名称",
        examples=["CS2023-01", "AI2024-02"]
    )
    email: Optional[EmailStr] = Field(
        None,
        description="电子邮箱",
        examples=["zhangsan@university.edu"]
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        pattern=r"^\+?[\d\s\-()]{7,20}$",
        description="联系电话",
        examples=["+8613800138000", "139-1234-5678"]
    )
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="家庭住址",
        examples=["北京市海淀区中关村大街1号"]
    )
    gpa: Optional[float] = Field(
        None,
        ge=0.0,
        le=4.0,
        description="平均绩点（0.0-4.0）",
        examples=[3.75, 2.9]
    )
    status: Optional[StudentStatusEnum] = Field(
        StudentStatusEnum.ACTIVE,
        description="学生状态",
        examples=["active", "graduated"]
    )
    

    # 年龄验证（业务规则）
    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v: date) -> date:
        """验证年龄在 15-30 岁之间"""
        from datetime import date as dt_date
        age = (dt_date.today() - v).days // 365
        if not (15 <= age <= 30):
            raise ValueError(f"学生年龄应在 15-30 岁之间（当前 {age} 岁）")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "S2024001",
                "name": "张三",
                "gender": "male",
                "date_of_birth": "2005-08-15",
                "enrollment_date": "2023-09-01",
                "major": "计算机科学与技术",
                "class_name": "CS2023-01",
                "email": "zhangsan@university.edu",
                "phone": "+8613800138000",
                "address": "北京市海淀区中关村大街1号",
                "gpa": 3.75,
                "status": "active"
                
            }
        }
    )


# ==================== 创建 Schema ====================
class StudentCreate(StudentBase):
    """创建学生请求（必填字段校验）"""
    # 重写必填字段（移除默认值，确保创建时必须提供）
    student_id: str = Field(
        ...,
        min_length=5,
        max_length=64,
        pattern=r"^[A-Z]\d{4,}$"
    )
    name: str = Field(..., min_length=2, max_length=50)
    date_of_birth: date = Field(...)
    major: str = Field(..., min_length=2, max_length=100)
    class_name: str = Field(..., min_length=3, max_length=50)
    
    # 创建时不允许提供 ID 和时间戳
    model_config = ConfigDict(
        extra="forbid",  # 禁止额外字段
        json_schema_extra={
            "description": "创建学生时的请求体，必填字段：student_id, name, date_of_birth, major, class_name"
        }
    )


# ==================== 更新 Schema ====================
class StudentUpdate(BaseModel):
    """更新学生请求（所有字段可选）"""
    student_id: Optional[str] = Field(
        None,
        min_length=5,
        max_length=64,
        pattern=r"^[A-Z]\d{4,}$"
    )
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    enrollment_date: Optional[date] = None
    major: Optional[str] = Field(None, min_length=2, max_length=100)
    class_name: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(
        None,
        max_length=20,
        pattern=r"^\+?[\d\s\-()]{7,20}$"
    )
    address: Optional[str] = Field(None, max_length=500)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    status: Optional[StudentStatusEnum] = None
    

    model_config = ConfigDict(
        extra="ignore",  # 忽略额外字段
        json_schema_extra={
            "description": "更新学生时的请求体，所有字段均为可选",
            "example": {
                "gpa": 3.9,
                "status": "graduated"
            }
        }
    )


# ==================== 数据库基础 Schema ====================
class StudentInDBBase(StudentBase):
    id: int = Field(..., description="数据库主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")
    
    @computed_field
    @property
    def age(self) -> int:
        """安全计算当前年龄"""
        # 增加防御性判断，防止字段缺失时崩溃
        if not hasattr(self, 'date_of_birth') or self.date_of_birth is None:
            return 0
            
        from datetime import date as dt_date
        return (dt_date.today() - self.date_of_birth).days // 365


# ==================== 响应 Schema ====================
class Student(StudentInDBBase,):
    """学生完整响应模型（API 返回）"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "学生完整信息（含计算字段）",
            "example": {
                "id": 1,
                "student_id": "S2024001",
                "name": "张三",
                "gender": "male",
                "date_of_birth": "2005-08-15",
                "enrollment_date": "2023-09-01",
                "major": "计算机科学与技术",
                "class_name": "CS2023-01",
                "email": "zhangsan@university.edu",
                "phone": "+8613800138000",
                "address": "北京市海淀区中关村大街1号",
                "gpa": 3.75,
                "status": "active",
                
                "emergency_contact_name": "张父",
                "emergency_contact_phone": "+8613900139000",
                "created_at": "2024-01-15T08:30:00",
                "updated_at": "2024-02-01T14:20:00",
                "age": 18,
                "enrollment_years": 0.5
            }
        }
    )


# ==================== 列表响应 Schema ====================
class StudentListResponse(BaseModel):
    """学生列表分页响应"""
    data: List[Student] = Field(..., description="学生数据列表")
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(1, ge=1, description="当前页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    total_pages: int = Field(..., ge=0, description="总页数")
    
    @computed_field
    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages
    
    @computed_field
    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [  # 包含 Student 模型示例
                    {
                        "id": 1,
                        "student_id": "S2024001",
                        "name": "张三",
                        "age": 18,
                        "gpa": 3.75,
                        "major": "计算机科学与技术",
                        "status": "active"
                    }
                ],
                "total": 150,
                "page": 1,
                "size": 10,
                "total_pages": 15,
                "has_next": True,
                "has_prev": False
            }
        }
    )


# ==================== 查询参数 Schema ====================
class StudentQuery(BaseModel):
    """学生查询参数（用于 GET /students）"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    major: Optional[str] = Field(None, description="专业筛选")
    class_name: Optional[str] = Field(None, description="班级筛选")
    status: Optional[StudentStatusEnum] = Field(None, description="状态筛选")
    min_gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="最小GPA")
    max_gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="最大GPA")
    student_id: Optional[str] = Field(None, description="学号模糊查询")
    name: Optional[str] = Field(None, description="姓名模糊查询")
    sort_by: Optional[Literal["gpa", "enrollment_date", "name"]] = Field(
        "enrollment_date",
        description="排序字段"
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        "desc",
        description="排序方向"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "size": 20,
                "major": "计算机",
                "min_gpa": 3.5,
                "status": "active",
                "sort_by": "gpa",
                "order": "desc"
            }
        }
    )
# 共享的基础字段
class StudentBase(BaseModel):
    student_id: str = Field(..., description="学号", examples=["S2024001"])
    name: str = Field(..., min_length=2, max_length=50)
    gender: str = Field(..., pattern="^(male|female|other)$")
    date_of_birth: date
    enrollment_date: date
    major: str
    class_name: str
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)

# 用于创建接口的输入模型
class StudentCreate(StudentBase):
    model_config = ConfigDict(extra="forbid")


# 用于 API 返回的输出模型
class StudentResponse(StudentInDBBase):
    """
    统一使用这个类作为 FastAPI 的 response_model
    """
    model_config = ConfigDict(
        from_attributes=True,  # 允许直接从 ORM 对象转换
        json_schema_extra={ "description": "学生信息完整响应" }
    )