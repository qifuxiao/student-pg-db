'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 09:43:17
FilePath: /student_pg_db/src/student_pg_db/models/base.py
'''

from pydantic import BaseModel, Field, ConfigDict  # ✅ 导入 ConfigDict
from datetime import datetime
from typing import Optional

class BaseDBModel(BaseModel):
    """数据库基础模型（Pydantic V2 兼容）"""
    id: Optional[int] = Field(None, description="主键ID")
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    # ✅ Pydantic V2 配置（替代废弃的 class Config）
    model_config = ConfigDict(
        from_attributes=True,        # ✅ 替代 orm_mode = True
        arbitrary_types_allowed=True  # ✅ V2 仍支持此选项
    )
    
    def update_timestamp(self) -> 'BaseDBModel':
        """
        更新时间戳（Pydantic V2 兼容）
        
        注意：Pydantic V2 默认模型是不可变的（frozen=False 时可变），
        但为安全起见，返回新实例而非修改原实例
        """
        return self.model_copy(
            update={"updated_at": datetime.now()}
        )