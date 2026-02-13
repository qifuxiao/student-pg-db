'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-05 09:40:42
FilePath: /student_pg_db/src/student_pg_db/cli.py
'''
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import sys
import traceback  # ✅ 添加导入


from .database.repository import StudentRepository
from .utils.data_generator import DataGenerator

app = typer.Typer(
    name="student-db",
    help="Production student database management system",
    add_completion=False
)
console = Console()


@app.command()
def seed(count: int = 100):
    """一键生成模拟数据 """
    from .utils.data_generator import DataGenerator
    from .core.session import SessionLocal
    
    with SessionLocal() as session:
        generator = DataGenerator()
        students = generator.generate_students(count)
        session.add_all(students)
        session.commit()
    print(f"✅ 成功生成 {count} 条学生数据")
@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Student Database Management System - Production Edition"""
    if verbose:
        console.print(f"[dim]Running in verbose mode[/dim]")
        console.print(f"[dim]Package location: {Path(__file__).parent.parent}[/dim]")

if __name__ == "__main__":
    app()