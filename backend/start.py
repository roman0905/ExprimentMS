#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端服务启动脚本
"""

import uvicorn
import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """启动 FastAPI 服务"""
    
    # 检查环境变量
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"启动实验数据管理系统后端服务...")
    print(f"服务地址: http://{host}:{port}")
    print(f"API 文档: http://{host}:{port}/docs")
    print(f"重载模式: {'开启' if reload else '关闭'}")
    print("-" * 50)
    
    try:
        # 启动服务
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            reload_dirs=[str(current_dir)] if reload else None,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()