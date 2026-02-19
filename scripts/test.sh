#!/bin/bash
###
 # @Author: qifuxiao 867225266@qq.com
 # @Date: 2026-02-06 03:27:40
 # @FilePath: /student_pg_db/scripts/test.sh
### 
set -e

echo "🧪=========================================="
echo "   学生数据库系统 - 集成测试套件"
echo "=========================================="

APP_ENV=test 
# 7. 应用初始化（创建 students 表）
echo "3️⃣  应用初始化（创建 students 表）..."
cd /home/alexqi/develop/student_pg_db
# poetry run alembic init alembic
poetry run alembic revision --autogenerate -m "xxx"
poetry run alembic upgrade head
poetry run student-db seed --count 100 2>&1 | grep -E "✅|ℹ️|跳过|已存在|成功" || true

