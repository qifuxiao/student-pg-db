# 1. 清理旧容器和卷（确保干净环境）

echo "1️⃣  清理旧测试环境..."
cd ./Docker
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# 2. 启动测试数据库（自动创建 student_test 数据库和用户）
echo "2️⃣  启动测试数据库容器..."
docker-compose -f docker-compose.test.yml up -d

# 3. 等待数据库就绪
echo "3️⃣  等待数据库初始化（约15秒）..."
sleep 15

4. 验证数据库健康状态
if ! docker-compose -f docker-compose.test.yml ps | grep -q "Up"; then
    echo "❌ 容器未启动，查看日志:"
    docker-compose -f docker-compose.test.yml logs
    exit 1
fi
echo "✅ 测试数据库已就绪 (端口 5433)"