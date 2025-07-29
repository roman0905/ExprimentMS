from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserPermission, RoleEnum, ModuleEnum
from schemas import (
    LoginRequest, RegisterRequest, LoginResponse, UserCreate, UserUpdate, UserResponse,
    UserListResponse, UserPermissionCreate, UserPermissionResponse,
    AssignPermissionsRequest, MessageResponse
)

router = APIRouter(prefix="/api/auth", tags=["认证管理"])

# JWT配置
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """获取密码哈希"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    """验证用户"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def check_admin_permission(current_user: User = Depends(get_current_user)):
    """检查管理员权限"""
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

def check_module_permission(module: ModuleEnum, permission_type: str = "read"):
    """检查模块权限"""
    def permission_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 管理员拥有所有权限
        if current_user.role == RoleEnum.Admin:
            return current_user
        
        # 检查用户权限
        user_permission = db.query(UserPermission).filter(
            UserPermission.user_id == current_user.user_id,
            UserPermission.module == module
        ).first()
        
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有访问 {module.value} 模块的权限"
            )
        
        if permission_type == "read" and not user_permission.can_read:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有读取 {module.value} 模块的权限"
            )
        elif permission_type == "write" and not user_permission.can_write:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有写入 {module.value} 模块的权限"
            )
        elif permission_type == "delete" and not user_permission.can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有删除 {module.value} 模块的权限"
            )
        
        return current_user
    return permission_checker

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value
        }
    )

@router.post("/register", response_model=LoginResponse)
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == register_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 密码强度验证
    if len(register_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少6位"
        )
    
    # 创建新用户，默认角色为普通用户
    hashed_password = get_password_hash(register_data.password)
    db_user = User(
        username=register_data.username,
        password_hash=hashed_password,
        role=RoleEnum.User  # 默认为普通用户
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 注册成功后自动登录
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "user_id": db_user.user_id,
            "username": db_user.username,
            "role": db_user.role.value
        }
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    # 加载用户权限
    permissions = db.query(UserPermission).filter(UserPermission.user_id == current_user.user_id).all()
    current_user.permissions = permissions
    return current_user

@router.post("/logout")
def logout():
    """用户登出（前端处理删除token）"""
    return {"message": "登出成功"}

# 用户管理相关路由
@router.get("/users", response_model=List[UserListResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(check_admin_permission)):
    """获取用户列表（仅管理员）"""
    users = db.query(User).all()
    return users

@router.post("/users", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(check_admin_permission)):
    """创建用户（仅管理员）"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(check_admin_permission)):
    """更新用户（仅管理员）"""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新用户信息
    if user_data.username is not None:
        # 检查用户名是否已被其他用户使用
        existing_user = db.query(User).filter(User.username == user_data.username, User.user_id != user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        db_user.username = user_data.username
    
    if user_data.password is not None:
        db_user.password_hash = get_password_hash(user_data.password)
    
    if user_data.role is not None:
        db_user.role = user_data.role
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_admin_permission)):
    """删除用户（仅管理员）"""
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除用户权限
    db.query(UserPermission).filter(UserPermission.user_id == user_id).delete()
    # 删除用户
    db.delete(db_user)
    db.commit()
    
    return MessageResponse(message="用户删除成功")

# 权限管理相关路由
@router.get("/users/{user_id}/permissions", response_model=List[UserPermissionResponse])
def get_user_permissions(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_admin_permission)):
    """获取用户权限（仅管理员）"""
    permissions = db.query(UserPermission).filter(UserPermission.user_id == user_id).all()
    return permissions

@router.post("/assign-permissions", response_model=MessageResponse)
def assign_permissions(request: AssignPermissionsRequest, db: Session = Depends(get_db), current_user: User = Depends(check_admin_permission)):
    """分配权限给用户（仅管理员）"""
    # 检查用户是否存在
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除用户现有权限
    db.query(UserPermission).filter(UserPermission.user_id == request.user_id).delete()
    
    # 添加新权限
    for perm in request.permissions:
        db_permission = UserPermission(
            user_id=request.user_id,
            module=perm.module,
            can_read=perm.can_read,
            can_write=perm.can_write,
            can_delete=perm.can_delete
        )
        db.add(db_permission)
    
    db.commit()
    
    return MessageResponse(message="权限分配成功")