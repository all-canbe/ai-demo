# Document Analyzer Backend

基于 FastAPI 的文档分析后端服务，包含 Redis 缓存和 Celery 异步任务队列。

## 技术栈

- **FastAPI** - 高性能 Python Web 框架
- **PostgreSQL** - 关系型数据库
- **Redis** - 缓存服务
- **Celery** - 异步任务队列
- **Docker** - 容器化部署

## 快速开始

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| FastAPI | 8000 | Web API |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |

### API 文档

启动后访问：http://localhost:8000/docs

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接
│   ├── models.py        # 数据模型
│   ├── redis_cache.py   # Redis缓存服务
│   ├── celery.py        # Celery配置
│   ├── tasks.py         # 异步任务
│   ├── routes.py        # API路由
│   └── main.py          # FastAPI入口
├── Dockerfile
├── requirements.txt
└── start.sh
```

## 环境变量

参考 `.env` 文件配置环境变量。
