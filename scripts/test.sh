#!/bin/bash
set -e

echo "🧪=========================================="
echo "   学生数据库系统 - 集成测试套件"
echo "=========================================="

# # 1. 清理旧容器和卷（确保干净环境）
# echo "1️⃣  清理旧测试环境..."
# cd ./Docker
# docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# # 2. 启动测试数据库（自动创建 student_test 数据库和用户）
# echo "2️⃣  启动测试数据库容器..."
# docker-compose -f docker-compose.test.yml up -d

# # 3. 等待数据库就绪
# echo "3️⃣  等待数据库初始化（约15秒）..."
# sleep 15

# 4. 验证数据库健康状态
# if ! docker-compose -f docker-compose.test.yml ps | grep -q "Up"; then
#     echo "❌ 容器未启动，查看日志:"
#     docker-compose -f docker-compose.test.yml logs
#     exit 1
# fi
# echo "✅ 测试数据库已就绪 (端口 5433)"
cp .env.prod.example .env.test  # 使用测试环境变量文件
# 5️⃣ 关键：在导入任何 Python 代码前设置环境变量！
echo "2️⃣  设置测试环境变量..."
export DB_HOST=localhost
export DB_PORT=5433
export DB_ADMIN_USER=student_test_app          # ✅ 核心：不是 postgres
export DB_ADMIN_PASSWORD=test_secure_pass_123
export DB_ADMIN_DB=student_test                # ✅ 核心：管理操作在 student_test 库执行
export DB_NAME=student_test
export DB_USER=student_test_app
export DB_PASSWORD=test_secure_pass_123

# 6. 验证连接（诊断用）
echo "🔍 验证数据库连接..."
if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_ADMIN_USER -d $DB_ADMIN_DB -c "SELECT current_user, current_database();" 2>&1 | grep -q "student_test_app"; then
    echo "✅ 数据库连接验证成功 (用户: student_test_app, 数据库: student_test)"
else
    echo "❌ 数据库连接失败，请检查环境变量配置"
    echo "   当前配置:"
    echo "     DB_ADMIN_USER=$DB_ADMIN_USER"
    echo "     DB_ADMIN_DB=$DB_ADMIN_DB"
    echo "     DB_PORT=$DB_PORT"
    exit 1
fi

# 7. 应用初始化（创建 students 表）
echo "3️⃣  应用初始化（创建 students 表）..."
cd /home/alexqi/develop/student_pg_db
poetry run student-db init 2>&1 | grep -E "✅|ℹ️|跳过|已存在|成功" || true

# 8. 运行测试（此时 conftest.py 会读取正确的环境变量）
echo "4️⃣  运行测试套件..."
if poetry run pytest tests/ -v --tb=short -m "integration or unit" 2>&1; then
    TEST_PASSED=1
else
    TEST_FAILED=1
fi

# 9. 清理
# echo "5️⃣  清理测试环境..."
# cd /home/alexqi/develop/student_pg_db/Docker
# docker-compose -f docker-compose.test.yml down -v

# 10. 结果
if [ -n "$TEST_PASSED" ]; then
    echo -e "\n✅=========================================="
    echo "   所有测试通过！"
    echo "=========================================="
    exit 0
else
    echo -e "\n❌=========================================="
    echo "   测试失败！详细错误见上方输出"
    echo "=========================================="
    exit 1
fi