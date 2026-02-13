'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-06 02:33:02
FilePath: /student_pg_db/tests/unit/test_models.py
'''
"""Pydantic 模型单元测试 - 无数据库依赖"""
import pytest
from datetime import date, datetime
from student_pg_db.models.students import Student
from student_pg_db.schemas import StudentStatusEnum


class TestStudentModel:
    """学生模型验证测试"""
    
    def test_valid_student(self):
        """有效学生数据应通过验证"""
        student = Student(
            student_id="S20240001",
            name="张三",
            gender="male",
            date_of_birth=date(2005, 8, 15),
            enrollment_date=date(2023, 9, 1),
            major="计算机科学与技术",
            class_name="CS2023-01"
        )
        assert student.name == "张三"
        assert student.status == StudentStatusEnum.ACTIVE
    
    def test_invalid_age_too_young(self):
        """年龄过小应抛出验证错误"""
        with pytest.raises(ValueError, match="15-30岁"):
            Student(
                student_id="S20240002",
                name="李四",
                gender="female",
                date_of_birth=date(2015, 1, 1),  # 9岁
                enrollment_date=date(2023, 9, 1),
                major="计算机",
                class_name="CS2023"
            )
    
    def test_invalid_age_too_old(self):
        """年龄过大应抛出验证错误"""
        with pytest.raises(ValueError, match="15-30岁"):
            Student(
                student_id="S20240003",
                name="王五",
                gender="male",
                date_of_birth=date(1980, 1, 1),  # 44岁
                enrollment_date=date(2023, 9, 1),
                major="计算机",
                class_name="CS2023"
            )
    
    def test_gpa_validation(self):
        """GPA 边界值验证"""
        # 有效值
        s1 = Student(
            student_id="S20240004",
            name="赵六",
            gender="female",
            date_of_birth=date(2004, 5, 20),
            enrollment_date=date(2022, 9, 1),
            major="金融学",
            class_name="FIN2022",
            gpa=4.0
        )
        assert s1.gpa == 4.0
        
        # 无效值（超过上限）
        with pytest.raises(ValueError):
            Student(
                student_id="S20240005",
                name="钱七",
                gender="male",
                date_of_birth=date(2004, 5, 20),
                enrollment_date=date(2022, 9, 1),
                major="金融学",
                class_name="FIN2022",
                gpa=4.1
            )
    
    def test_from_orm_mode(self):
        """测试 Pydantic V2 from_attributes 模式（ORM 兼容）"""
        class MockORM:
            id = 1
            student_id = "S20240006"
            name = "孙八"
            gender = "other"
            date_of_birth = date(2003, 11, 30)
            enrollment_date = date(2021, 9, 1)
            major = "人工智能"
            class_name = "AI2021"
            gpa = 3.85
        
        student = Student.model_validate(MockORM())
        assert student.name == "孙八"
        assert student.gpa == 3.85