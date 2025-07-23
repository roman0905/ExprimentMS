# 实验数据管理系统后端 API

基于 FastAPI 构建的实验数据管理系统后端服务，提供完整的 RESTful API 接口。

## 技术栈

- **Web 框架**: FastAPI 0.104.1
- **数据库 ORM**: SQLAlchemy 2.0.23
- **数据库**: MySQL 8.0+
- **认证**: JWT (JSON Web Tokens)
- **文档**: 自动生成的 Swagger UI

## 功能模块

### 1. 认证管理 (`/api/auth`)
- 用户登录/登出
- JWT 令牌验证
- 用户信息获取

### 2. 批次管理 (`/api/batches`)
- 批次的增删改查
- 批次搜索和分页
- 批次关联数据检查

### 3. 人员管理 (`/api/persons`)
- 人员信息的增删改查
- 人员搜索和分页
- 人员关联数据检查

### 4. 实验管理 (`/api/experiments`)
- 实验记录的增删改查
- 实验数据筛选（按批次、人员）
- 关联批次和人员信息显示

### 5. 竞品数据管理 (`/api/competitor-files`)
- 文件上传/下载
- 文件列表查询和筛选
- 文件删除（包括物理文件）

### 6. 指尖血数据管理 (`/api/finger-blood-data`)
- 血糖数据的增删改查
- 时间范围筛选
- 数据统计和分析

### 7. 传感器管理 (`/api/sensors`)
- 传感器记录的增删改查
- 传感器使用时间管理
- 设备关联信息

## 安装和运行

### 1. 环境要求

- Python 3.11+
- MySQL 8.0+

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 数据库配置

创建 MySQL 数据库：

```sql
CREATE DATABASE experiment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

配置数据库连接（修改 `database.py` 中的 `DATABASE_URL`）：

```python
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/experiment_db"
```

或设置环境变量：

```bash
export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/experiment_db"
```

### 4. 初始化数据库

```bash
python init_db.py
```

重置数据库（删除所有数据）：

```bash
python init_db.py --reset
```

### 5. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

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
├── main.py                 # 主应用文件
├── database.py            # 数据库连接配置
├── models.py              # 数据库模型
├── schemas.py             # Pydantic 模式
├── init_db.py             # 数据库初始化脚本
├── requirements.txt       # 依赖包列表
├── routers/               # API 路由
│   ├── __init__.py
│   ├── auth.py           # 认证路由
│   ├── batches.py        # 批次管理路由
│   ├── persons.py        # 人员管理路由
│   ├── experiments.py    # 实验管理路由
│   ├── competitor_files.py # 竞品数据路由
│   ├── finger_blood_data.py # 指尖血数据路由
│   └── sensors.py        # 传感器管理路由
└── uploads/              # 文件上传目录
    └── competitor_files/ # 竞品文件存储
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
curl -X POST "http://localhost:8000/api/competitor-files/upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "batch_id=1" \
     -F "person_id=1" \
     -F "file=@/path/to/your/file.pdf"
```

## 开发说明

### 1. 添加新的 API 端点

1. 在相应的路由文件中添加新的端点函数
2. 定义相应的 Pydantic 模式（如果需要）
3. 在 `main.py` 中注册路由（如果是新的路由文件）

### 2. 数据库模型修改

1. 修改 `models.py` 中的模型定义
2. 运行数据库迁移或重新初始化数据库
3. 更新相应的 Pydantic 模式

### 3. 认证和权限

当前实现了简单的 JWT 认证，可以根据需要扩展：

- 添加角色权限控制
- 实现用户注册功能
- 添加密码重置功能

## 部署说明

### 1. 生产环境配置

- 修改 `SECRET_KEY` 为安全的随机字符串
- 设置合适的数据库连接池参数
- 配置日志记录
- 使用 HTTPS

### 2. Docker 部署

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

## 故障排除

### 1. 数据库连接问题

- 检查 MySQL 服务是否运行
- 验证数据库连接字符串
- 确认数据库用户权限

### 2. 文件上传问题

- 检查 `uploads` 目录权限
- 确认磁盘空间充足
- 验证文件大小限制

### 3. 认证问题

- 检查 JWT 令牌是否过期
- 验证 SECRET_KEY 配置
- 确认请求头格式正确

## 许可证

本项目仅供学习和研究使用。