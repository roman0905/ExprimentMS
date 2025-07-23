from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

# 导入路由
from routers import batches, persons, experiments, competitor_files, finger_blood_data, sensors, auth
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 创建上传目录
    upload_dirs = [
        "uploads/competitor_files",
    ]
    for dir_path in upload_dirs:
        os.makedirs(dir_path, exist_ok=True)
    print("上传目录创建完成")
    
    yield
    # 关闭时的清理工作
    print("应用正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title="实验数据管理系统 API",
    description="为实验研究提供中心化数据管理平台的后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于文件下载）
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(batches.router)
app.include_router(persons.router)
app.include_router(experiments.router)
app.include_router(competitor_files.router)
app.include_router(finger_blood_data.router)
app.include_router(sensors.router)

# 根路径
@app.get("/")
def read_root():
    return {
        "message": "实验数据管理系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return HTTPException(
        status_code=500,
        detail=f"内部服务器错误: {str(exc)}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )