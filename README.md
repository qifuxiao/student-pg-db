<!--
 * @Author: qifuxiao 867225266@qq.com
 * @Date: 2026-02-05 09:25:52
 * @FilePath: /student_pg_db/README.md
-->
# 学生数据库管理系统

面向对象设计的 PostgreSQL 学生信息管理项目，包含完整的数据库初始化、数据建模和模拟数据生成功能。

## 🌟 特性

- **分层架构**：连接管理、业务逻辑、数据模型清晰分离
- **完整字段**：学生表包含15+业务字段（学号、姓名、性别、出生日期、入学日期、专业、班级、邮箱、电话、地址、GPA、状态、奖学金、紧急联系人等）
- **数据验证**：Pydantic 模型提供强类型验证和业务规则
- **模拟数据**：Faker 生成符合中国语境的100条真实感学生数据
- **性能优化**：自动创建索引和更新时间触发器
- **事务安全**：完整的错误处理和事务回滚机制

## 🚀 快速开始

# 部署流程
1. 使用docker compose 部署数据库
- 生产环境 
`/home/alexqi/develop/student_pg_db/Docker/docker-compose.yml`
- 测试环境
`/home/alexqi/develop/student_pg_db/Docker/docker-compose.test.yml`
2. 核心用途：环境隔离
| 配置文件 | 用途 | 加载时机 | 示例场景 |
| :--- | :--- | :--- | :--- |
| `.env` | 开发环境 | `docker-compose up` 自动加载 | 本地开发、调试 |
| `.env.prod` | 生产环境 | `docker-compose --env-file .env.prod up` | 生产部署 |
| `.env.test` | 测试环境 | `docker-compose -f docker-compose.test.yml --env-file .env.test up` | CI/CD 流水线 |
2.1 开发测试命令：
2.1.1 创建pg_dev数据库镜像
`sh scripts.run_docker_dev.sh`
3. 测试环境部署
创建测试环境实际配置文件
`cp .env.test.example .env.test`

4. alembic 管理数据库
4.1 初始化
`poetry run alembic init alembic`
4.2 生成迁移+建表
`alembic revision --autogenerate -m "init students table"`
`alembic upgrade head`

# 每日开发步骤
修改完代码后

## 本地开发安装方式（Editable 安装）
`poetry install` 
## 更新数据库
<!-- 
poetry run alembic revision --autogenerate -m "xxx"
poetry run alembic upgrade head

 -->
 ## pytest + Poetry
 `APP_ENV=test poetry run pytest -v`