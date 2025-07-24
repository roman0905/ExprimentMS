# 实验数据管理系统后端 API

## 系统概述

本系统是基于 FastAPI + SQLAlchemy + MySQL 构建的实验数据管理系统后端，提供完整的 RESTful API 接口，支持实验批次、人员、数据等全生命周期管理。

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (JSON Web Tokens)
- **数据验证**: Pydantic
- **文档**: 自动生成 Swagger UI

## 核心功能模块

### 1. 用户认证与权限管理 (`/api/auth`)
- **用户注册登录**: 支持用户注册、登录和JWT认证
- **权限控制**: 基于角色和模块的细粒度权限管理
- **用户管理**: 管理员可进行用户创建、编辑、删除和权限分配
- **密码安全**: 使用bcrypt进行密码哈希加密

### 2. 批次管理 (`/api/batches`)
- **批次CRUD**: 批次的创建、查询、更新和删除
- **唯一性验证**: 批次号唯一性检查
- **关联检查**: 删除前检查是否有关联数据

### 3. 人员管理 (`/api/persons`)
- **人员信息管理**: 受试人员基本信息的完整CRUD操作
- **搜索功能**: 支持按姓名模糊搜索
- **批次关联**: 人员与实验批次的关联管理

### 4. 实验管理 (`/api/experiments`)
- **实验记录**: 实验信息的创建、查询、更新和删除
- **成员管理**: 实验参与人员的分配和管理
- **数据筛选**: 支持按批次和人员筛选实验记录

### 5. 竞品文件管理 (`/api/competitorFiles`)
- **文件操作**: 支持文件上传、下载、重命名和删除
- **存储管理**: 文件物理存储与数据库记录同步
- **数据导出**: Excel格式的文件列表导出功能
- **筛选查询**: 按批次、人员和时间范围筛选

### 6. 指尖血数据管理 (`/api/fingerBloodData`)
- **血糖数据**: 指尖血糖值的录入、查询和管理
- **时间筛选**: 支持按采集时间范围查询
- **数据导出**: 血糖数据的Excel导出功能
- **统计分析**: 血糖数据的基本统计信息

### 7. 传感器管理 (`/api/sensors`)
- **设备管理**: 传感器设备信息的完整管理
- **使用记录**: 传感器使用时间的记录和追踪
- **状态监控**: 传感器运行状态的实时监控

### 8. 活动日志 (`/api/activities`)
- **操作记录**: 用户操作行为的完整记录
- **审计追踪**: 系统操作的审计日志功能
- **日志查询**: 支持按用户和时间查询操作记录

## 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- pip

### 本地开发

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   
   创建 `.env` 文件：
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/experiment_db
   SECRET_KEY=your-secret-key-here
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=admin123
   ```

3. **启动服务**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker部署

参考项目根目录的 `Docker部署说明.md` 文件进行容器化部署。

## API 文档

启动服务后，可以通过以下地址访问 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 默认登录信息

- **用户名**: admin
- **密码**: admin123

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── database.py          # 数据库连接配置
│   ├── models/              # SQLAlchemy 数据模型
│   ├── schemas/             # Pydantic 数据验证模式
│   ├── routers/             # API 路由模块
│   ├── core/                # 核心功能（配置、安全、依赖）
│   └── utils/               # 工具函数
├── uploads/                 # 文件上传存储目录
├── requirements.txt         # Python 依赖包
└── .env                     # 环境变量配置
```

## API 使用示例

### 1. 用户登录

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
```

### 2. 获取批次列表

```bash
curl -X GET "http://localhost:8000/api/batches/" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 创建新批次

```bash
curl -X POST "http://localhost:8000/api/batches/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "batch_number": "BATCH003",
       "start_time": "2024-01-03T09:00:00",
       "end_time": "2024-01-03T17:00:00"
     }'
```

### 4. 上传竞品文件

```bash
curl -X POST "http://localhost:8000/api/competitorFiles/upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "batch_id=1" \
     -F "person_id=1" \
     -F "file=@/path/to/your/file.pdf"
```

## 开发规范

### API设计原则
- 遵循 RESTful API 设计规范
- 使用统一的响应格式和错误处理
- 实现完整的CRUD操作和数据验证
- 提供详细的API文档和示例

### 安全措施
- JWT Token 认证机制
- 密码bcrypt哈希加密
- 基于角色的权限控制
- SQL注入防护和输入验证

## 部署说明

### 生产环境配置

- 修改 `SECRET_KEY` 为安全的随机字符串
- 设置合适的数据库连接池参数
- 配置日志记录
- 使用 HTTPS

### Docker 部署

可以创建 Dockerfile 进行容器化部署：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 许可证

MIT License