#!/bin/sh
set -e

echo "🧪=========================================="
echo "   学生数据库系统 - 集成测试套件"
echo "=========================================="

# ✅ POSIX 兼容：获取脚本目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
ENV_FILE="$PROJECT_ROOT/.env.test"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | xargs 2>/dev/null || true)
    echo "✅ 加载测试环境变量: $ENV_FILE"
else
    echo "⚠️  未找到 $ENV_FILE，使用默认值"
    export DB_ADMIN_USER=postgres
    export DB_ADMIN_PASSWORD=test_password
    export DB_ADMIN_DB=student_test
    export DB_PORT=5433
fi

cd "$PROJECT_ROOT/Docker"
echo "1️⃣  清理旧测试环境..."
# ✅ 关键修复：指定项目名 -p test（隔离资源）
docker-compose -p test -f docker-compose.test.yml down -v 2>/dev/null || true
rm -rf logs && mkdir logs 2>/dev/null || true

echo "2️⃣  启动测试数据库容器..."
# ✅ 关键修复：指定项目名 -p test
docker-compose -p test -f docker-compose.test.yml up -d
sleep 5

echo "3️⃣  等待数据库初始化（最多 30 秒）..."
i=1
while [ $i -le 30 ]; do
    if docker-compose -p test -f docker-compose.test.yml ps | grep -q "Up"; then
        echo "✅ 数据库已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 超时：数据库未启动，查看日志:"
        docker-compose -p test -f docker-compose.test.yml logs
        exit 1
    fi
    sleep 1
    printf "."
    i=$((i + 1))
done
echo ""

echo "4️⃣  验证数据库连接..."
if PGPASSWORD="$DB_ADMIN_PASSWORD" psql -h 127.0.0.1 -p "$DB_PORT" -U "$DB_ADMIN_USER" -d "$DB_ADMIN_DB" -c "SELECT '✅' as status;" 2>&1 | grep -q "✅"; then
    echo "✅ 连接验证成功"
else
    echo "❌ 连接失败，请检查环境变量和容器状态"
    docker-compose -p test -f docker-compose.test.yml logs
    exit 1
fi

# echo "5️⃣  应用初始化（创建 students 表）..."
# cd "$PROJECT_ROOT"
# poetry run student-db init 2>&1 | grep -E "✅|跳过|已存在" || true

# echo "6️⃣  运行测试套件..."
# if poetry run pytest tests/ -v --tb=short -m "integration or unit" 2>&1; then
#     TEST_PASSED=1
# else
#     TEST_FAILED=1
# fi

# echo "7️⃣  清理测试环境..."
# cd "$PROJECT_ROOT/Docker"
# docker-compose -p test -f docker-compose.test.yml down -v

# if [ -n "${TEST_PASSED:-}" ]; then
#     echo ""
#     echo "✅=========================================="
#     echo "   所有测试通过！"
#     echo "=========================================="
#     exit 0
# else
#     echo ""
#     echo "❌=========================================="
#     echo "   测试失败！"
#     echo "=========================================="
#     exit 1
# fi