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

from .database.manager import DatabaseManager
from .database.repository import StudentRepository
from .utils.data_generator import DataGenerator

app = typer.Typer(
    name="student-db",
    help="Production student database management system",
    add_completion=False
)
console = Console()

@app.command()
def init():
    """Initialize database schema (idempotent operation)"""
    try:
        manager = DatabaseManager()
        
        with console.status("[bold green]Creating database..."):
            manager.create_database()
        
        with console.status("[bold green]Creating application user..."):
            manager.create_user_and_grant_privileges()
        
        with console.status("[bold green]Creating student table..."):
            manager.create_student_table()
        
        # 显示表结构
        schema = manager.get_table_schema()
        table = Table(title="Students Table Schema", show_header=True, header_style="bold magenta")
        table.add_column("Column", style="dim", width=25)
        table.add_column("Type", width=20)
        table.add_column("Nullable", justify="center", width=10)
        
        for col in schema:
            table.add_row(
                col['column_name'],
                col['data_type'],
                "✓" if col['is_nullable'] == 'YES' else "✗"
            )
        
        console.print(table)
        console.print(Panel.fit(
            "[bold green]✅ Database initialization successful![/bold green]\n"
            "💡 Next: Generate sample data with 'student-db generate --count 100'",
            title="Success",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Initialization failed:[/bold red]\n{str(e)}",
            title="Error",
            border_style="red"
        ))
        raise typer.Exit(code=1)

@app.command()
def generate(
    count: int = typer.Option(100, "--count", "-n", help="Number of students to generate"),
    locale: str = typer.Option("zh_CN", "--locale", "-l", help="Faker locale (zh_CN/en_US)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing to DB")
):
    """Generate realistic student data"""
    try:
        generator = DataGenerator(locale=locale)
        repo = StudentRepository()
        
        console.print(f"[bold blue]Generating {count} student records (locale: {locale})...[/bold blue]")
        
        with console.status("[bold yellow]Creating student objects..."):
            students = generator.generate_students(count)
        
        if dry_run:
            console.print("[bold yellow] Dry run mode - previewing first 3 records:[/bold yellow]")
            for i, student in enumerate(students[:3], 1):
                console.print(f"\n[bold]{i}. {student.name}[/bold] ({student.student_id})")
                console.print(f"   Major: {student.major} | GPA: {student.gpa or 'N/A'}")
            console.print(f"\n[bold]Total records: {count}[/bold] (not written to database)")
            return
        
        with console.status(f"[bold green]Inserting {count} records into database..."):
            inserted = repo.insert_students_batch(students)
        
        stats = repo.get_statistics()
        console.print(Panel.fit(
            f"[bold green]✅ Successfully inserted {inserted} records![/bold green]\n\n"
            f"📊 Statistics:\n"
            f"   • Total students: {stats['total_students']}\n"
            f"   • Active students: {stats['active_students']}\n"
            f"   • Avg GPA: {stats['average_gpa']}\n"
            f"   • Top major: {stats['top_majors'][0]['major']} ({stats['top_majors'][0]['count']} students)",
            title="Data Generation Complete",
            border_style="green"
        ))
        
    except Exception as e:
        import traceback
        error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        console.print(Panel.fit(
            f"[bold red]❌ Data generation failed:[/bold red]\n{str(e)}\n{error_msg}",
            title="Error",
            border_style="red"
        ))
        raise typer.Exit(code=1)

@app.command()
def stats():
    """Show database statistics"""
    try:
        repo = StudentRepository()
        stats = repo.get_statistics()
        
        table = Table(title="Student Database Statistics", show_header=False)
        table.add_row("[bold]Total Students[/bold]", f"[green]{stats['total_students']}[/green]")
        table.add_row("[bold]Active Students[/bold]", f"[green]{stats['active_students']}[/green]")
        table.add_row("[bold]Graduated[/bold]", f"[blue]{stats['graduated_students']}[/blue]")
        table.add_row("[bold]Average GPA[/bold]", f"[yellow]{stats['average_gpa']}[/yellow]")
        table.add_row("[bold]Majors[/bold]", f"[cyan]{len(stats['majors_list'])}[/cyan]")
        
        console.print(table)
        
        # 专业分布
        major_table = Table(title="Top 5 Majors", show_header=True, header_style="bold magenta")
        major_table.add_column("Rank", justify="right", style="cyan", width=6)
        major_table.add_column("Major", style="green")
        major_table.add_column("Students", justify="right", style="yellow")
        
        for i, major in enumerate(stats['top_majors'], 1):
            major_table.add_row(str(i), major['major'], str(major['count']))
        
        console.print(major_table)
        
    except Exception as e:
        console.print(f"[bold red]❌ Failed to retrieve statistics: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def version():
    """Show package version"""
    from student_pg_db import __version__
    console.print(f"[bold blue]Student DB System v{__version__}[/bold blue]")
@app.command()
def checkgpa(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of students to list")
):
    """ list top students by GPA """
    try: 
        repo = StudentRepository()
        top_students = repo.get_top_students(limit)
        
        table = Table(title=f"Top {limit} Students by GPA", show_header=True, header_style="bold magenta")
        table.add_column("Rank", justify="right", style="cyan", width=6)
        table.add_column("Student ID", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("GPA", justify="right", style="blue")
        
        for i, student in enumerate(top_students, 1):
            table.add_row(str(i), student.student_id, student.name, str(student.gpa))
        
        console.print(table)
    except Exception as e:
        import traceback
        error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        console.print(f"[bold red]❌ Failed to retrieve top students: {e}\n{error_msg}[/bold red]")
        raise typer.Exit(code=1)
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