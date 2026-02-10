import random
from datetime import date
from faker import Faker
from typing import List
from ..models.students import Student, StudentStatus

class DataGenerator:
    def __init__(self, locale: str = "zh_CN"):
        self.fake = Faker(locale)
        self.majors = [
            "计算机科学与技术", "软件工程", "人工智能", "数据科学", "网络安全",
            "电子信息工程", "通信工程", "自动化", "金融学", "法学", "英语"
        ]
        self.classes = [f"{m[:2]}{y}-{c:02d}" for m in self.majors for y in [2022, 2023, 2024] for c in range(1, 5)]

    def generate_student(self, index: int = 0) -> Student:
        """生成单个学生记录，确保符合 Pydantic V2 和数据库约束"""
        
        # 1. 确定日期逻辑（符合 15-30 岁校验）
        enroll_year = random.choice([2022, 2023, 2024])
        enroll_date = date(enroll_year, 9, 1)
        age = random.randint(18, 25)
        dob = date(enroll_year - age, random.randint(1, 12), random.randint(1, 28))

        # 2. 生成字段并强制截断（防御性编程）
        name = self.fake.name()[:100]  # 匹配模型 100
        major = random.choice(self.majors)[:100]
        
        # 3. 构造学号（确保 20 位以内）
        student_id = f"S{enroll_year}{str(index).zfill(5)}{random.randint(10, 99)}"

        return Student(
            student_id=student_id,
            name=name,
            gender=random.choice(["male", "female", "other"]),
            date_of_birth=dob,
            enrollment_date=enroll_date,
            major=major,
            class_name=random.choice(self.classes)[:50],
            email=self.fake.email()[:100],
            phone=self.fake.phone_number()[:20],
            address=self.fake.address()[:500],
            gpa=round(random.uniform(2.0, 4.0), 2),
            status=StudentStatus.ACTIVE,
            scholarship_amount=0.0
        )

    def generate_students(self, count: int = 100) -> List[Student]:
        return [self.generate_student(i) for i in range(count)]