'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-13 05:34:54
FilePath: /student_pg_db/src/student_pg_db/api/routes/students.py
'''
from fastapi import APIRouter, Depends, HTTPException
from student_pg_db.database.repository import StudentRepository
from student_pg_db.schemas.student import StudentCreate, StudentOut

router = APIRouter(prefix="/students", tags=["students"])

@router.post("", response_model=StudentOut)
def create_student(dto: StudentCreate):
    return StudentRepository().create_from_schema(dto)

@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int):
    student = StudentRepository().get_by_id(student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.delete("/{student_id}")
def delete_student(student_id: int):
    StudentRepository().delete(student_id)
    return {"status": "ok"}