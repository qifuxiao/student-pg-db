'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 11:25:22
FilePath: /student_pg_db/src/student_pg_db/database/repository.py
'''
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update
from ..models.students import Student

class StudentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, student: Student):
        self.session.add(student)
        self.session.flush()  # 不要 commit
        return student
    def get_by_id(self, id: int) -> Optional[Student]:
        """按 ID 查询 """
        return self.session.get(Student, id)

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Student]:
        """批量获取学生（默认100条）"""
        stmt = select(Student).offset(offset).limit(limit)
        return list(self.session.scalars(stmt).all())

    def update(self, id: int, **kwargs) -> Optional[Student]:
        """更新学生信息 """
        stmt = update(Student).where(Student.id == id).values(**kwargs).returning(Student)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.scalar_one_or_none()

    def delete(self, id: int) -> bool:
        """删除学生记录 """
        stmt = delete(Student).where(Student.id == id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0