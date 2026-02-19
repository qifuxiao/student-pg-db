'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-13 07:02:52
FilePath: /student_pg_db/tests/test_data_generator.py
'''
import pytest
from datetime import date
from student_pg_db.utils.data_generator import DataGenerator

@pytest.mark.unit
def test_generate_single_student(generator):
    """测试单个学生数据的字段合法性"""
    student = generator.generate_student(index=1)
    
    # 验证学号格式
    assert student.student_id.startswith("S202")
    # 验证逻辑：入学年份应在 2022-2024 之间 
    assert 2022 <= student.enrollment_date.year <= 2024
    # 验证 GPA 范围 
    assert 2.0 <= float(student.gpa) <= 4.0
    # 验证必填字段
    assert student.name is not None
    assert student.major in generator.majors

@pytest.mark.unit
def test_batch_generation_uniqueness(generator):
    """测试批量生成时学号的唯一性"""
    count = 50
    students = generator.generate_students(count)
    assert len(students) == count
    
    student_ids = [s.student_id for s in students]
    assert len(set(student_ids)) == count  # 学号不重复