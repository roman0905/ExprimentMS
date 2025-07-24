from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Batch, User
from schemas import BatchCreate, BatchUpdate, BatchResponse, MessageResponse
from routers.auth import get_current_user, check_module_permission
from models import ModuleEnum

router = APIRouter(prefix="/api/batches", tags=["批次管理"])

@router.get("/", response_model=List[BatchResponse])
def get_batches(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    search: Optional[str] = Query(None, description="按批次号搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.BATCH_MANAGEMENT, "read"))
):
    """获取批次列表"""
    query = db.query(Batch)
    
    if search:
        query = query.filter(Batch.batch_number.contains(search))
    
    batches = query.offset(skip).limit(limit).all()
    return batches

@router.post("/", response_model=BatchResponse)
def create_batch(
    batch: BatchCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.BATCH_MANAGEMENT, "write"))
):
    """创建新批次"""
    # 检查批次号是否已存在
    existing_batch = db.query(Batch).filter(Batch.batch_number == batch.batch_number).first()
    if existing_batch:
        raise HTTPException(status_code=400, detail="批次号已存在")
    
    db_batch = Batch(**batch.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(
    batch_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.BATCH_MANAGEMENT, "read"))
):
    """获取单个批次详情"""
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    return batch

@router.put("/{batch_id}", response_model=BatchResponse)
def update_batch(
    batch_id: int, 
    batch: BatchUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.BATCH_MANAGEMENT, "write"))
):
    """更新批次信息"""
    db_batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    # 检查批次号是否与其他批次冲突
    if batch.batch_number != db_batch.batch_number:
        existing_batch = db.query(Batch).filter(
            Batch.batch_number == batch.batch_number,
            Batch.batch_id != batch_id
        ).first()
        if existing_batch:
            raise HTTPException(status_code=400, detail="批次号已存在")
    
    for field, value in batch.dict().items():
        setattr(db_batch, field, value)
    
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.delete("/{batch_id}", response_model=MessageResponse)
def delete_batch(
    batch_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.BATCH_MANAGEMENT, "delete"))
):
    """删除批次"""
    db_batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    # 检查是否有关联的实验、文件等
    if db_batch.experiments or db_batch.competitor_files or db_batch.finger_blood_files or db_batch.sensors:
        raise HTTPException(status_code=400, detail="该批次下还有关联数据，无法删除")
    
    db.delete(db_batch)
    db.commit()
    return MessageResponse(message="批次删除成功")