from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .core.session import get_session
from .database.repository import StudentRepository
from .schemas.student import StudentCreate, StudentResponse, StudentUpdate
from .models.students import Student
from fastapi import FastAPI
from student_pg_db.api.routes.students import router




app = FastAPI(title="Student Management System")
app.include_router(router)

@app.post("/students/")
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_session)
):
    repo = StudentRepository(db)
    student = repo.create(Student(**data.model_dump()))
    return student

@app.get("/students/", response_model=list[StudentResponse])
def list_students(
    skip: int = 0, 
    limit: int = Query(100, le=1000), 
    db: Session = Depends(get_session)
):
    repo = StudentRepository(db)
    return repo.list_all(offset=skip, limit=limit)

@app.get("/students/{id}", response_model=StudentResponse)
def get_student(id: int, db: Session = Depends(get_session)):
    repo = StudentRepository(db)
    student = repo.get_by_id(id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.patch("/students/{id}", response_model=StudentResponse)
def update_student(id: int, data: StudentUpdate, db: Session = Depends(get_session)):
    repo = StudentRepository(db)
    # 只更新传入的字段
    updated = repo.update(id, **data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Update failed: Student not found")
    return updated