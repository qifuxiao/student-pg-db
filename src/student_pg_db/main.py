'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 11:25:54
FilePath: /student_pg_db/src/student_pg_db/main.py
'''


import os
import sys
from pathlib import Path
from .config import DatabaseConfig
from .database.manager import DatabaseManager
from .database.repository import StudentRepository
from .utils.data_generator import DataGenerator

def setup_environment():
    """设置环境变量（开发环境）"""
    env_path = Path('.env')
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write("""# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_ADMIN_USER=postgres
DB_ADMIN_PASSWORD=postgres
DB_ADMIN_DB=postgres
DB_NAME=student_management
DB_USER=student_app
DB_PASSWORD=student_secure_pass
""")
        print("✅ .env 配置文件已创建，请根据实际环境修改密码")

def initialize_database():
    """初始化数据库（创建DB、用户、表）"""
    print("\n🔧 初始化数据库...")
    
    manager = DatabaseManager()
    
    try:
        # 1. 创建数据库
        manager.create_database()
        
        # 2. 创建用户并授权
        manager.create_user_and_grant_privileges()
        
        # 3. 创建学生表
        manager.create_student_table()
        
        # 4. 显示表结构
        print("\n📋 学生表结构:")
        schema = manager.get_table_schema()
        for col in schema:
            print(f"  • {col['column_name']:25s} | {col['data_type']:15s} | Null: {col['is_nullable']:5s} | Default: {col['column_default']}")
        
        print("\n✅ 数据库初始化完成!")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generate_sample_data(count: int = 100):
    """生成并插入模拟数据"""
    print(f"\n🧪 生成 {count} 条模拟学生数据...")
    
    generator = DataGenerator()
    repository = StudentRepository()
    
    try:
        students = generator.generate_students(count)
        inserted = repository.insert_students_batch(students)
        print(f"✅ 成功插入 {inserted} 条学生记录")
        
        # 显示前3条数据示例
        print("\n📊 数据示例 (前3条):")
        for i, student in enumerate(students[:3], 1):
            print(f"\n  [{i}] 学号: {student.student_id}")
            print(f"      姓名: {student.name} | 专业: {student.major}")
            print(f"      GPA: {student.gpa or 'N/A'} | 状态: {student.status.value}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 数据生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_statistics():
    """显示数据库统计信息"""
    print("\n📈 数据库统计信息:")
    
    repository = StudentRepository()
    stats = repository.get_statistics()
    
    print(f"  • 总学生数: {stats['total_students']}")
    print(f"  • 在读学生: {stats['active_students']}")
    print(f"  • 已毕业: {stats['graduated_students']}")
    print(f"  • 平均GPA: {stats['average_gpa']}")
    print(f"\n  • 专业分布 (Top 5):")
    for major in stats['top_majors']:
        print(f"    - {major['major']}: {major['count']} 人")

def main():
    """主函数"""
    print("="*60)
    print("🎓 学生数据库管理系统")
    print("="*60)
    
    # 1. 设置环境
    setup_environment()
    
    # 2. 初始化数据库
    if not initialize_database():
        sys.exit(1)
    
    # 3. 生成模拟数据
    if not generate_sample_data(100):
        sys.exit(1)
    
    # 4. 显示统计信息
    show_statistics()
    
    # 5. 提供访问提示
    print("\n" + "="*60)
    print("✅ 系统准备就绪！")
    print("="*60)
    print("\n💡 后续使用指南:")
    print("   1. 在您的应用中导入 StudentRepository:")
    print("      from database.repository import StudentRepository")
    print("\n   2. 基本用法示例:")
    print("      repo = StudentRepository()")
    print("      student = repo.get_student_by_id('S2024001')")
    print("      top_students = repo.get_top_students(10)")
    print("\n   3. 数据库连接参数:")
    print(f"      Host: {DatabaseConfig.HOST}")
    print(f"      Port: {DatabaseConfig.PORT}")
    print(f"      Database: {DatabaseConfig.APP_DB_NAME}")
    print(f"      User: {DatabaseConfig.APP_USER}")
    print("\n   4. 表结构: students (15+ 字段，含索引和触发器)")
    print("="*60)

if __name__ == "__main__":
    main()