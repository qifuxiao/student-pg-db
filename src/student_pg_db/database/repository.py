# src/student_pg_db/database/repository.py
from typing import List, Optional
from psycopg2.extras import execute_values  # ✅ 新增导入
from ..models.students import Student
from ..core.connection import DatabaseConnection

class StudentRepository:
    """学生数据仓库 - 封装所有数据库操作"""
    
    def __init__(self):
        self.db_conn = DatabaseConnection()
    
    def insert_student(self, student: Student) -> int:
        """插入单个学生记录"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO students (
                    student_id, name, gender, date_of_birth, enrollment_date,
                    major, class_name, email, phone, address, gpa, status,
                    scholarship_amount, emergency_contact_name, emergency_contact_phone
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (student_id) DO NOTHING
                RETURNING id
            """, (
                student.student_id,
                student.name,
                student.gender,
                student.date_of_birth,
                student.enrollment_date,
                student.major,
                student.class_name,
                student.email,
                student.phone,
                student.address,
                student.gpa,
                student.status.value,
                student.scholarship_amount,
                student.emergency_contact_name,
                student.emergency_contact_phone
            ))
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def insert_students_batch(self, students: List[Student]) -> int:
        """
        批量插入学生记录（正确处理冲突并返回实际插入数量）
        ✅ 修复：使用 execute_values + RETURNING 精确计数
        """
        self.db_conn.connect_app()
        if students:
            s = students[0]
            data_map = s.model_dump()
            print("\n🔍 [长度诊断] 第一条数据长度检查:")
            for k, v in data_map.items():
                if isinstance(v, str):
                    print(f"字段: {k:25} | 长度: {len(v):3} | 内容: {v}")
        with self.db_conn.get_cursor() as cursor:
            # 准备数据
            records = [
                (
                    s.student_id,
                    s.name,
                    s.gender,
                    s.date_of_birth,
                    s.enrollment_date,
                    s.major,
                    s.class_name,
                    s.email,
                    s.phone,
                    s.address,
                    s.gpa,
                    s.status.value,
                    s.scholarship_amount,
                    s.emergency_contact_name,
                    s.emergency_contact_phone
                )
                for s in students
            ]
            
            # ✅ 关键修复：使用 execute_values 批量插入 + RETURNING 获取实际插入的ID
            result = execute_values(
                cursor,
                """
                INSERT INTO students (
                    student_id, name, gender, date_of_birth, enrollment_date,
                    major, class_name, email, phone, address, gpa, status,
                    scholarship_amount, emergency_contact_name, emergency_contact_phone
                ) VALUES %s
                ON CONFLICT (student_id) DO NOTHING
                RETURNING id
                """,
                records,
                fetch=True  # ✅ 获取返回结果
            )
            
            return len(result)  # ✅ 实际插入的数量（跳过冲突的记录）
    
    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """根据学号查询学生"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM students WHERE student_id = %s
            """, (student_id,))
            row = cursor.fetchone()
            return Student(**dict(row)) if row else None
    
    def get_students_by_major(self, major: str, limit: int = 20) -> List[Student]:
        """根据专业查询学生"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM students 
                WHERE major = %s 
                ORDER BY gpa DESC NULLS LAST
                LIMIT %s
            """, (major, limit))
            return [Student(**dict(row)) for row in cursor.fetchall()]
    
    def get_top_students(self, limit: int = 10) -> List[Student]:
        """获取GPA最高的学生"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM students 
                WHERE gpa IS NOT NULL 
                ORDER BY gpa DESC 
                LIMIT %s
            """, (limit,))
            return [Student(**dict(row)) for row in cursor.fetchall()]
    
    def update_student_gpa(self, student_id: str, new_gpa: float) -> bool:
        """更新学生GPA"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            cursor.execute("""
                UPDATE students 
                SET gpa = %s 
                WHERE student_id = %s
            """, (new_gpa, student_id))
            return cursor.rowcount > 0
    
    def get_statistics(self) -> dict:
        """获取学生统计数据"""
        self.db_conn.connect_app()
        
        with self.db_conn.get_cursor() as cursor:
            # 基础统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_students,
                    COUNT(*) FILTER (WHERE status = 'active') as active_students,
                    COUNT(*) FILTER (WHERE status = 'graduated') as graduated_students,
                    AVG(gpa) as average_gpa
                FROM students
            """)
            stats = cursor.fetchone()
            
            # 专业分布
            cursor.execute("""
                SELECT major, COUNT(*) as count 
                FROM students 
                GROUP BY major 
                ORDER BY count DESC
                LIMIT 5
            """)
            major_stats = cursor.fetchall()
            
            return {
                "total_students": stats['total_students'],
                "active_students": stats['active_students'],
                "graduated_students": stats['graduated_students'],
                "average_gpa": round(float(stats['average_gpa']), 2) if stats['average_gpa'] else None,
                "top_majors": [{"major": r['major'], "count": r['count']} for r in major_stats],
            }