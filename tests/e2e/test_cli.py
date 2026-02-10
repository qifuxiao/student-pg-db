'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-06 02:36:24
FilePath: /student_pg_db/tests/e2e/test_cli.py
'''
"""CLI 命令端到端测试 - 模拟真实用户操作"""
import subprocess
import json
from pathlib import Path
import pytest

class TestCLIE2E:
    """CLI 命令测试"""
    
    @pytest.fixture(autouse=True)
    def setup_test_env(self, tmp_path):
        """为每个测试创建隔离的临时环境"""
        # 保存原始工作目录
        original_cwd = Path.cwd()
        
        # 切换到临时目录
        test_env = tmp_path / "test_env"
        test_env.mkdir()
        (test_env / ".env").write_text(f"""
DB_HOST=localhost
DB_PORT=5433
DB_ADMIN_USER=postgres
DB_ADMIN_PASSWORD=test_password
DB_NAME=student_test
DB_USER=student_test_app
DB_PASSWORD=test_secure_pass
""")
        yield test_env
        
        # 恢复原始目录
        import os
        os.chdir(original_cwd)
    
    def run_cli(self, *args):
        """运行 CLI 命令并返回结果"""
        result = subprocess.run(
            ["poetry", "run", "student-db", *args],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())  # 在项目根目录运行
        )
        return result
    
    def test_cli_help(self):
        """CLI 应提供帮助信息"""
        result = self.run_cli("--help")
        assert result.returncode == 0
        assert "init" in result.stdout.lower()
        assert "generate" in result.stdout.lower()
        assert "list" in result.stdout.lower()
    
    def test_cli_init_command(self):
        """init 命令应成功初始化数据库"""
        result = self.run_cli("init")
        assert result.returncode == 0
        assert "success" in result.stdout.lower() or "成功" in result.stdout
    
    def test_cli_generate_command(self):
        """generate 命令应成功生成测试数据"""
        # 先初始化
        self.run_cli("init")
        
        # 生成5条测试数据（小数量加速测试）
        result = self.run_cli("generate", "--count", "5", "--dry-run")
        assert result.returncode == 0
        assert "preview" in result.stdout.lower() or "预览" in result.stdout
    
    def test_cli_list_command(self):
        """list 命令应显示学生列表"""
        # 初始化 + 生成数据
        self.run_cli("init")
        self.run_cli("generate", "--count", "10")
        
        # 查询列表
        result = self.run_cli("list", "--limit", "5")
        assert result.returncode == 0
        assert "学号" in result.stdout or "student_id" in result.stdout
    
    def test_cli_stats_command(self):
        """stats 命令应显示统计信息"""
        # 初始化 + 生成数据
        self.run_cli("init")
        self.run_cli("generate", "--count", "20")
        
        result = self.run_cli("stats")
        assert result.returncode == 0
        assert "total" in result.stdout.lower() or "总计" in result.stdout