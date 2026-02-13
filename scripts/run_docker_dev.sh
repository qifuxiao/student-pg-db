#!/bin/sh
set -e

echo "🧪=========================================="
echo "   学生数据库系统 - 开发环境启动"
echo "=========================================="

# ✅ POSIX 兼容：获取脚本目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | xargs 2>/dev/null || true)
    echo "✅ 加载开发环境变量: $ENV_FILE"
else
    echo "⚠️  未找到 $ENV_FILE，使用默认值"
    export DB_ADMIN_USER=postgres
    export DB_ADMIN_PASSWORD=123456
    export DB_PORT=5432
fi

cd "$PROJECT_ROOT/Docker"
echo "1️⃣  清理旧开发环境..."
# ✅ 关键修复：指定项目名 -p dev（隔离资源）
docker-compose -p dev -f docker-compose.yml down -v 2>/dev/null || true
rm -rf logs && mkdir logs 2>/dev/null || true

echo "2️⃣  启动开发数据库容器..."
# ✅ 关键修复：指定项目名 -p dev
docker-compose -p dev -f docker-compose.yml up -d
sleep 15

echo "✅ 开发数据库已就绪 (端口 $DB_PORT)"