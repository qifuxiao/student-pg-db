'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-06 02:35:24
FilePath: /student_pg_db/tests/integration/test_repository.py
'''
"""数据库仓库集成测试 - 需要真实数据库连接"""
import pytest
from datetime import date
from student_pg_db.models.students import Student
from student_pg_db.schemas import StudentStatusEnum


@pytest.mark.integration
class TestStudentRepository:
    """学生仓库集成测试"""
    
    def test_insert_single_student(self, repo, sample_student):
        """插入单个学生应成功"""
        student_id = repo.insert_student(sample_student)
        assert student_id is not None
        
        # 验证可查询回来
        retrieved = repo.get_student_by_id(sample_student.student_id)
        assert retrieved is not None
        assert retrieved.name == sample_student.name
        assert retrieved.gpa == sample_student.gpa
    
    def test_insert_batch_students(self, repo, sample_students):
        """批量插入应返回正确数量"""
        count = repo.insert_students_batch(sample_students)
        assert count == len(sample_students)
        
        # 验证总数
        stats = repo.get_statistics()
        assert stats["total_students"] >= len(sample_students)
    
    def test_query_by_major(self, populated_repo):
        """按专业查询应返回匹配结果"""
        students = populated_repo.get_students_by_major("计算机科学与技术", limit=5)
        assert len(students) > 0
        assert all("计算机" in s.major for s in students)
    
    def test_query_top_students(self, populated_repo):
        """GPA 排名查询应按降序返回"""
        students = populated_repo.get_top_students(limit=10)
        assert len(students) > 0
        
        # 验证 GPA 降序
        gpas = [s.gpa for s in students if s.gpa is not None]
        assert gpas == sorted(gpas, reverse=True)
    
    def test_update_gpa(self, repo, sample_student):
        """更新 GPA 应持久化到数据库"""
        # 先插入
        repo.insert_student(sample_student)
        
        # 更新
        new_gpa = 3.95
        success = repo.update_student_gpa(sample_student.student_id, new_gpa)
        assert success
        
        # 验证
        updated = repo.get_student_by_id(sample_student.student_id)
        assert updated.gpa == new_gpa
    
    def test_statistics_accuracy(self, populated_repo):
        """统计数据应准确反映数据库状态"""
        stats = populated_repo.get_statistics()
        
        assert stats["total_students"] > 0
        assert stats["active_students"] >= 0
        assert stats["average_gpa"] is not None
        assert len(stats["top_majors"]) > 0