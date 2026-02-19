'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-13 07:03:06
FilePath: /student_pg_db/tests/test_repository.py
'''
import pytest
from student_pg_db.database.repository import StudentRepository
from student_pg_db.models.students import Student

@pytest.mark.integration
def test_create_and_get_student(db_session, generator):
    """测试学生的创建和查询功能"""
    repo = StudentRepository(db_session)
    
    # 1. 创建测试数据
    mock_student = generator.generate_student(1)
    repo.add(mock_student)
    db_session.commit()
    
    # 2. 查询数据
    saved_student = repo.get_by_student_id(mock_student.student_id)
    
    assert saved_student is not None
    assert saved_student.name == mock_student.name
    assert saved_student.email == mock_student.email

@pytest.mark.integration
def test_update_student_status(db_session, generator):
    """测试更新学生状态"""
    repo = StudentRepository(db_session)
    student = generator.generate_student(2)
    repo.add(student)
    db_session.commit()
    
    # 执行更新
    repo.update_status(student.student_id, "graduated")
    
    updated_student = repo.get_by_student_id(student.student_id)
    assert updated_student.status == "graduated"