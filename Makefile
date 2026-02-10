SHELL := /bin/bash
VENV := $(shell poetry env info -p)

.PHONY: all setup install build run init generate test clean

all: setup

# 初始化开发环境（首次运行）
setup:
	@echo "🔧 Initializing Poetry environment..."
	@poetry install --no-interaction
	@echo "✅ Development environment ready!"

# 安装到系统（生产部署）
install:
	@echo "📦 Installing package system-wide..."
	@poetry build
	@pip install dist/student_db_system-1.0.0-py3-none-any.whl --force-reinstall --no-deps
	@echo "✅ Package installed at: $(VENV)/lib/python3.*/site-packages/student_db"

# 构建分发包
build:
	@poetry build
	@ls -lh dist/

# 运行命令行工具（开发模式）
run:
	@poetry run student-db --help

# 初始化数据库（生产环境安全模式）
init:
	@echo "🛡️  Initializing database in SAFE MODE (no data loss)..."
	@poetry run student-db init --safe-mode
	@echo "✅ Database initialized"

# 生成模拟数据
generate:
	@poetry run student-db generate --count 100 --locale zh_CN

# 运行测试
test:
	@poetry run pytest tests/ -v --tb=short

# 清理构建产物
clean:
	@rm -rf dist/ build/ *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 生产部署检查
deploy-check:
	@echo "🔍 Production deployment check:"
	@poetry check && echo "✅ Poetry config valid"
	@poetry run mypy student_db/ --strict && echo "✅ Type check passed"
	@poetry run black --check student_db/ && echo "✅ Code style valid"
	@poetry run ruff check student_db/ && echo "✅ Linting passed"
	@echo "✅ All checks passed - ready for deployment"