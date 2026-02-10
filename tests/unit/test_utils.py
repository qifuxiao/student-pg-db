'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-06 02:34:42
FilePath: /student_pg_db/tests/unit/test_utils.py
'''
"""工具函数单元测试"""
import pytest
from datetime import date
from student_pg_db.utils.data_generator import DataGenerator


class TestDataGenerator:
    """数据生成器测试"""
    
    @pytest.fixture
    def generator(self):
        return DataGenerator(locale="zh_CN")
    
    def test_generate_single_student(self, generator):
        """生成单个学生应包含所有必填字段"""
        student = generator.generate_student(1)
        assert student.student_id.startswith("S202")
        assert len(student.name) >= 2
        assert student.gender in ["male", "female", "other"]
        assert isinstance(student.date_of_birth, date)
        assert isinstance(student.enrollment_date, date)
        assert 2022 <= student.enrollment_date.year <= 2024
    
    def test_generate_batch_students(self, generator):
        """批量生成应返回指定数量的学生"""
        students = generator.generate_students(25)
        assert len(students) == 25
        # 检查学号唯一性
        student_ids = [s.student_id for s in students]
        assert len(student_ids) == len(set(student_ids))
    
    def test_gpa_distribution(self, generator):
        """GPA 分布应符合预期（大部分在 2.0-4.0 之间）"""
        students = generator.generate_students(100)
        gpas = [s.gpa for s in students if s.gpa is not None]
        assert len(gpas) > 80  # 至少 80% 有 GPA
        assert all(2.0 <= gpa <= 4.0 for gpa in gpas)
    
    def test_class_generation(self, generator):
        """班级名称生成应符合预期格式"""
        assert len(generator.classes) > 0
        sample_class = generator.classes[0]
        # 格式：专业前2字 + 年份 + "-" + 班级编号
        # 例如："计算2024-01"
        assert "-" in sample_class
        assert any(str(year) in sample_class for year in [2022, 2023, 2024])