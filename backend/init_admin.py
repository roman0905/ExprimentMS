#!/usr/bin/env python3
"""
数据库初始化脚本 - 创建默认管理员用户
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, RoleEnum
from passlib.context import CryptContext

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_database():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            # 创建默认管理员用户
            hashed_password = pwd_context.hash("admin123")
            admin_user = User(
                username="admin",
                password_hash=hashed_password,
                role=RoleEnum.Admin
            )
            db.add(admin_user)
            db.commit()
            print("默认管理员用户创建成功:")
            print("用户名: admin")
            print("密码: admin123")
            print("请在生产环境中修改默认密码！")
        else:
            print("管理员用户已存在")
    
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    init_database()