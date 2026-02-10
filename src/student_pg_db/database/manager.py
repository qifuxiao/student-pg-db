'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 11:22:24
FilePath: /student_pg_db/src/student_pg_db/database/manager.py
'''
from typing import List
import psycopg2 
from psycopg2 import sql,OperationalError
from psycopg2.extras import RealDictCursor

from ..core.connection import DatabaseConnection
from ..config import DatabaseConfig

class DatabaseManager:
    """数据库和表管理器"""
    
    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.config = DatabaseConfig()
    
    def create_tables(self):
        """创建学生信息表"""
        # 建议直接将 VARCHAR(20) 修改为更合理的长度
        query = """
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            student_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,         
            gender VARCHAR(10) NOT NULL,
            date_of_birth DATE NOT NULL,
            enrollment_date DATE NOT NULL,
            major VARCHAR(100) NOT NULL,         
            class_name VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(100),
            address TEXT,
            gpa DECIMAL(3, 2),
            status VARCHAR(100) DEFAULT 'active',
            scholarship_amount DECIMAL(10, 2) DEFAULT 0.0,
            emergency_contact_name VARCHAR(100), 
            emergency_contact_phone VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
    
    def create_user_and_grant_privileges(self) -> bool:
        """创建应用用户并授权（幂等）"""
        # 测试环境优化：如果 ADMIN_USER == APP_USER，跳过创建
        if self.config.ADMIN_USER == self.config.APP_USER:
            print(f"ℹ️  跳过用户创建（ADMIN_USER == APP_USER）")
            return True
        
        self.db_conn.connect_admin()
        
        with self.db_conn.get_cursor() as cursor:
            # 检查用户是否存在
            cursor.execute("""
                SELECT 1 FROM pg_roles WHERE rolname = %s
            """, (self.config.APP_USER,))
            
            if cursor.fetchone():
                print(f"✅ 用户 '{self.config.APP_USER}' 已存在")
                return True
            
            # 创建用户
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(self.config.APP_USER)
                ),
                (self.config.APP_PASSWORD,)
            )
            print(f"✅ 用户 '{self.config.APP_USER}' 创建成功")
        
        # 授予权限（在目标数据库中执行）
        try:
            # 临时连接到目标数据库
            conn_str = (
                f"host={self.config.HOST} "
                f"port={self.config.PORT} "
                f"dbname={self.config.APP_DB_NAME} "
                f"user={self.config.ADMIN_USER} "
                f"password={self.config.ADMIN_PASSWORD}"
            )
            conn = psycopg2.connect(conn_str)
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("GRANT CREATE, USAGE ON SCHEMA public TO {}").format(
                        sql.Identifier(self.config.APP_USER)
                    )
                )
                print(f"✅ Schema 'public' 权限授予 '{self.config.APP_USER}'")
            conn.close()
        except OperationalError as e:
            # 测试环境常见：数据库刚创建需等待
            if "does not exist" in str(e).lower():
                import time
                print("⚠️  目标数据库未就绪，等待 2 秒重试...")
                time.sleep(2)
                # 重试一次
                conn = psycopg2.connect(conn_str)
                conn.autocommit = True
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql.SQL("GRANT CREATE, USAGE ON SCHEMA public TO {}").format(
                            sql.Identifier(self.config.APP_USER)
                        )
                    )
                conn.close()
            else:
                raise
        
        return True
    
    def create_student_table(self) -> bool:
        """创建学生表"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            # 创建表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    student_id VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
                    date_of_birth DATE NOT NULL,
                    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    major VARCHAR(100) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    phone VARCHAR(20),
                    address TEXT,
                    gpa NUMERIC(3,2) CHECK (gpa >= 0.00 AND gpa <= 4.00),
                    status VARCHAR(20) DEFAULT 'active' 
                        CHECK (status IN ('active', 'graduated', 'suspended', 'withdrawn')),
                    scholarship_amount NUMERIC(10,2) DEFAULT 0.00,
                    emergency_contact_name VARCHAR(50),
                    emergency_contact_phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引优化查询
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_students_major ON students(major);
                CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_name);
                CREATE INDEX IF NOT EXISTS idx_students_gpa ON students(gpa DESC);
                CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);
            """)
            
            # 创建更新时间触发器
            cursor.execute(f"""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            cursor.execute(f"""
                DROP TRIGGER IF EXISTS trigger_update_updated_at ON students;
                CREATE TRIGGER trigger_update_updated_at
                    BEFORE UPDATE ON students
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            """)
            
            print("✅ 学生表 'students' 创建成功（含15+字段和索引）")
            return True
    
    def get_table_schema(self) -> List[dict]:
        """获取表结构信息"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = 'students'
                ORDER BY ordinal_position
            """)
            return cursor.fetchall()
    def create_user_and_grant_privileges(self) -> bool:
        """创建应用用户并授权（含 schema 权限）"""
        self.db_conn.connect_admin()
        
        with self.db_conn.get_cursor() as cursor:
            # 检查用户是否存在
            cursor.execute("""
                SELECT 1 FROM pg_roles WHERE rolname = %s
            """, (self.config.APP_USER,))
            
            if cursor.fetchone():
                print(f"✅ 用户 '{self.config.APP_USER}' 已存在")
            else:
                # 创建用户
                cursor.execute(
                    sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                        sql.Identifier(self.config.APP_USER)
                    ),
                    (self.config.APP_PASSWORD,)
                )
                print(f"✅ 用户 '{self.config.APP_USER}' 创建成功")
            
            # 授予数据库级权限
            cursor.execute(
                sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                    sql.Identifier(self.config.APP_DB_NAME),
                    sql.Identifier(self.config.APP_USER)
                )
            )
            print(f"✅ 数据库 '{self.config.APP_DB_NAME}' 权限授予 '{self.config.APP_USER}'")
        
        # 【关键修复】授予 schema 级权限（必须在目标数据库中执行）
        # 临时用 postgres 用户连接到 student_management 数据库
        conn_str = (
            f"host={self.config.HOST} "
            f"port={self.config.PORT} "
            f"dbname={self.config.APP_DB_NAME} "
            f"user={self.config.ADMIN_USER} "
            f"password={self.config.ADMIN_PASSWORD}"
        )
        
        try:
            # 重试机制：数据库刚创建可能需要短暂等待
            for attempt in range(3):
                try:
                    conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
                    conn.autocommit = True
                    with conn.cursor() as cursor:
                        # 授予 public schema 的 CREATE 和 USAGE 权限
                        cursor.execute(
                            sql.SQL("GRANT CREATE, USAGE ON SCHEMA public TO {}").format(
                                sql.Identifier(self.config.APP_USER)
                            )
                        )
                        print(f"✅ Schema 'public' 权限 (CREATE, USAGE) 授予 '{self.config.APP_USER}'")
                    conn.close()
                    break
                except psycopg2.OperationalError as e:
                    if attempt < 2:
                        import time
                        print(f"⚠️  数据库连接失败（尝试 {attempt+1}/3），等待 2 秒重试...")
                        time.sleep(2)
                    else:
                        raise
        except Exception as e:
            print(f"❌ 授予 schema 权限时出错: {e}")
            raise
        
        return True