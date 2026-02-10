'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-06 02:26:46
FilePath: /student_pg_db/tests/conftest.py
'''

"""
测试基础设施 - 数据库隔离与 fixture 管理
关键设计：每个测试在独立事务中运行，结束后自动回滚，保证测试隔离性

✅ 修复说明：
1. 完全移除硬编码的 os.environ.update()
2. 为测试数据添加唯一前缀，避免跨测试冲突
3. 增强连接失败诊断
4. 适配测试环境：使用 student_test_app 用户 + student_test 数据库
"""
import os
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from unittest.mock import patch
import uuid  # ✅ 新增：用于生成唯一标识

# ✅ 关键修复：完全移除硬编码！配置由外部环境变量控制

from student_pg_db.config import DatabaseConfig
from student_pg_db.core.connection import DatabaseConnection
from student_pg_db.database.manager import DatabaseManager
from student_pg_db.database.repository import StudentRepository
from student_pg_db.utils.data_generator import DataGenerator
from student_pg_db.models.students import Student, StudentStatus


@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    """
    会话级 fixture：初始化测试数据库结构（只执行一次）
    """
    # 诊断：打印当前配置
    print(f"\n🔍 测试配置:")
    print(f"   DB_HOST={DatabaseConfig.HOST}")
    print(f"   DB_PORT={DatabaseConfig.PORT}")
    print(f"   DB_ADMIN_USER={DatabaseConfig.ADMIN_USER}")
    print(f"   DB_ADMIN_DB={DatabaseConfig.ADMIN_DB}")
    print(f"   DB_NAME={DatabaseConfig.APP_DB_NAME}")
    
    # 1. 尝试连接管理数据库
    try:
        admin_conn = psycopg2.connect(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            dbname=DatabaseConfig.ADMIN_DB,
            user=DatabaseConfig.ADMIN_USER,
            password=DatabaseConfig.ADMIN_PASSWORD
        )
        admin_conn.autocommit = True
        print(f"✅ 成功连接管理数据库: {DatabaseConfig.ADMIN_DB} (用户: {DatabaseConfig.ADMIN_USER})")
    except psycopg2.OperationalError as e:
        print(f"\n❌ 无法连接管理数据库，请检查环境变量配置:")
        print(f"   - 确保 DB_ADMIN_USER={DatabaseConfig.ADMIN_USER} 在数据库中存在")
        print(f"   - 确保 DB_ADMIN_DB={DatabaseConfig.ADMIN_DB} 可被该用户访问")
        print(f"   - 完整错误: {e}")
        raise
    
    # 2. 检查应用数据库是否存在（幂等）
    with admin_conn.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = %s
        """, (DatabaseConfig.APP_DB_NAME,))
        
        if not cursor.fetchone():
            cursor.execute(
                f"CREATE DATABASE {DatabaseConfig.APP_DB_NAME} WITH OWNER {DatabaseConfig.ADMIN_USER} ENCODING 'UTF8'"
            )
            print(f"✅ 创建应用数据库: {DatabaseConfig.APP_DB_NAME}")
        else:
            print(f"ℹ️  应用数据库已存在: {DatabaseConfig.APP_DB_NAME}")
    
    admin_conn.close()
    
    # 3. 初始化表结构
    manager = DatabaseManager()
    manager.create_student_table()
    print(f"✅ 表结构初始化完成")
    
    yield  # 所有测试执行


@pytest.fixture
def db_transaction():
    """
    函数级 fixture：提供带事务的数据库连接
    核心机制：每个测试在独立事务中运行，结束后自动回滚 → 零数据污染
    """
    conn = psycopg2.connect(
        host=DatabaseConfig.HOST,
        port=DatabaseConfig.PORT,
        dbname=DatabaseConfig.APP_DB_NAME,
        user=DatabaseConfig.APP_USER,
        password=DatabaseConfig.APP_PASSWORD,
        cursor_factory=RealDictCursor
    )
    conn.autocommit = False
    
    original_get_connection = DatabaseConnection.get_connection
    
    def mock_get_connection(self):
        return conn
    
    with patch.object(DatabaseConnection, 'get_connection', mock_get_connection):
        yield conn
        conn.rollback()  # ✅ 关键：回滚事务
        conn.close()


@pytest.fixture
def repo(db_transaction):
    """提供已连接的 StudentRepository"""
    return StudentRepository()


@pytest.fixture
def generator():
    """提供数据生成器"""
    return DataGenerator(locale="zh_CN")


# ✅ 关键修复：为测试数据添加唯一前缀，避免跨测试冲突
@pytest.fixture
def sample_student(generator, request):
    """
    单个学生测试数据（带唯一前缀）
    使用测试函数名 + 随机数确保全局唯一性
    """
    # 生成唯一前缀（测试函数名 + 随机6位十六进制）
    prefix = f"{request.node.name}_{uuid.uuid4().hex[:6]}"
    student = generator.generate_student(1)
    student.student_id = f"{prefix}_TEST001"
    student.name = f"测试_{prefix}"
    student.major = "测试专业"
    student.class_name = "TEST2024"
    return student


# ✅ 关键修复：批量测试数据也添加唯一前缀
@pytest.fixture
def sample_students(generator, request):
    """
    10条学生测试数据（带唯一前缀）
    确保跨测试无冲突
    """
    prefix = f"{request.node.name}_{uuid.uuid4().hex[:6]}"
    students = generator.generate_students(10)
    for i, s in enumerate(students):
        s.student_id = f"{prefix}_TEST{i:03d}"
        s.name = f"测试_{prefix}_{i}"
    return students


@pytest.fixture
def populated_repo(repo, sample_students):
    """
    预填充数据的仓库（用于查询测试）
    注意：数据会在测试结束后自动回滚
    """
    repo.insert_students_batch(sample_students)
    return repo
@pytest.fixture(scope="session", autouse=True)
def db_teardown():
    """测试会话结束时自动清理连接"""
    yield
    db_conn = DatabaseConnection()
    db_conn.close()