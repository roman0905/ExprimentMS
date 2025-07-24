#!/bin/bash

# 实验数据管理系统部署脚本

set -e

echo "开始部署实验数据管理系统..."

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p backend/uploads/competitor_files
mkdir -p mysql/init

# 检查环境配置文件
if [ ! -f ".env.production" ]; then
    echo "警告: .env.production文件不存在，请先配置环境变量"
    echo "可以复制.env.production模板并修改其中的配置"
fi

# 停止现有服务
echo "停止现有服务..."
docker-compose down

# 构建镜像
echo "构建Docker镜像..."
docker-compose build --no-cache

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 检查健康状态
echo "检查应用健康状态..."
for i in {1..10}; do
    if curl -f http://localhost/api/health &> /dev/null; then
        echo "✅ 应用启动成功！"
        echo "前端地址: http://localhost"
        echo "后端API: http://localhost/api"
        echo "API文档: http://localhost/api/docs"
        echo "默认管理员账户: admin / admin123 (请及时修改)"
        exit 0
    fi
    echo "等待应用启动... ($i/10)"
    sleep 10
done

echo "❌ 应用启动失败，请检查日志:"
echo "docker-compose logs"
exit 1