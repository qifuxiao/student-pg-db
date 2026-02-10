'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-06 02:35:55
FilePath: /student_pg_db/tests/integration/test_manager.py
'''
"""数据库管理器集成测试"""
import pytest
from student_pg_db.database.manager import DatabaseManager


@pytest.mark.integration
class TestDatabaseManager:
    """数据库管理器测试"""
    
    # def test_create_database_idempotent(self):
    #     """创建数据库应幂等（多次调用不报错）"""
    #     manager = DatabaseManager()
        
    #     # 第一次创建
    #     assert manager.create_database() is True
        
    #     # 第二次创建（应跳过）
    #     assert manager.create_database() is True  # 不应抛出异常
    
    def test_create_user_idempotent(self):
        """创建用户应幂等"""
        manager = DatabaseManager()
        
        # 第一次创建
        assert manager.create_user_and_grant_privileges() is True
        
        # 第二次创建（应跳过）
        assert manager.create_user_and_grant_privileges() is True
    
    def test_create_table_idempotent(self):
        """创建表应幂等"""
        manager = DatabaseManager()
        
        # 第一次创建
        assert manager.create_student_table() is True
        
        # 第二次创建（应跳过）
        assert manager.create_student_table() is True
    
    def test_get_table_schema(self):
        """获取表结构应包含关键字段"""
        manager = DatabaseManager()
        schema = manager.get_table_schema()
        
        column_names = [col["column_name"] for col in schema]
        assert "id" in column_names
        assert "student_id" in column_names
        assert "name" in column_names
        assert "gpa" in column_names
        assert "major" in column_names