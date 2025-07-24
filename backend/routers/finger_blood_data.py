from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import pandas as pd
import tempfile
import os

from database import get_db
from models import FingerBloodFile, Batch, Person, User
from schemas import FingerBloodDataResponse, FingerBloodDataCreate, FingerBloodDataUpdate, MessageResponse
from routers.activities import log_activity
from routers.auth import get_current_user, check_module_permission
from models import ModuleEnum

router = APIRouter(prefix="/api/fingerBloodData", tags=["指尖血数据管理"])

@router.get("/", response_model=List[FingerBloodDataResponse])
def get_finger_blood_data(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间筛选"),
    end_time: Optional[datetime] = Query(None, description="结束时间筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.FINGER_BLOOD_DATA, "read"))
):
    """获取指尖血数据列表"""
    query = db.query(FingerBloodFile).join(Batch).join(Person)
    
    if batch_id:
        query = query.filter(FingerBloodFile.batch_id == batch_id)
    
    if person_id:
        query = query.filter(FingerBloodFile.person_id == person_id)
    
    if start_time:
        query = query.filter(FingerBloodFile.collection_time >= start_time)
    
    if end_time:
        query = query.filter(FingerBloodFile.collection_time <= end_time)
    
    data = query.order_by(FingerBloodFile.collection_time.desc()).offset(skip).limit(limit).all()
    
    # 添加关联信息
    result = []
    for item in data:
        data_dict = {
            "finger_blood_file_id": item.finger_blood_file_id,
            "person_id": item.person_id,
            "batch_id": item.batch_id,
            "collection_time": item.collection_time,
            "blood_glucose_value": float(item.blood_glucose_value),
            "person_name": item.person.person_name if item.person else None,
            "batch_number": item.batch.batch_number if item.batch else None
        }
        result.append(FingerBloodDataResponse(**data_dict))
    
    return result

@router.post("/", response_model=FingerBloodDataResponse)
def create_finger_blood_data(
    data: FingerBloodDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.FINGER_BLOOD_DATA, "write"))
):
    """新增指尖血数据"""
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == data.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == data.person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    db_data = FingerBloodFile(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    result = FingerBloodDataResponse(
        finger_blood_file_id=db_data.finger_blood_file_id,
        person_id=db_data.person_id,
        batch_id=db_data.batch_id,
        collection_time=db_data.collection_time,
        blood_glucose_value=float(db_data.blood_glucose_value),
        person_name=person.person_name,
        batch_number=batch.batch_number
    )
    
    return result

@router.get("/{data_id}", response_model=FingerBloodDataResponse)
def get_finger_blood_data_item(
    data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.FINGER_BLOOD_DATA, "read"))
):
    """获取单条指尖血数据详情"""
    data = db.query(FingerBloodFile).filter(FingerBloodFile.finger_blood_file_id == data_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    result = FingerBloodDataResponse(
        finger_blood_file_id=data.finger_blood_file_id,
        person_id=data.person_id,
        batch_id=data.batch_id,
        collection_time=data.collection_time,
        blood_glucose_value=float(data.blood_glucose_value),
        person_name=data.person.person_name if data.person else None,
        batch_number=data.batch.batch_number if data.batch else None
    )
    
    return result

@router.put("/{data_id}", response_model=FingerBloodDataResponse)
def update_finger_blood_data(
    data_id: int,
    data: FingerBloodDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.FINGER_BLOOD_DATA, "write"))
):
    """更新指尖血数据"""
    db_data = db.query(FingerBloodFile).filter(FingerBloodFile.finger_blood_file_id == data_id).first()
    if not db_data:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == data.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == data.person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    for field, value in data.dict().items():
        setattr(db_data, field, value)
    
    db.commit()
    db.refresh(db_data)
    
    result = FingerBloodDataResponse(
        finger_blood_file_id=db_data.finger_blood_file_id,
        person_id=db_data.person_id,
        batch_id=db_data.batch_id,
        collection_time=db_data.collection_time,
        blood_glucose_value=float(db_data.blood_glucose_value),
        person_name=person.person_name,
        batch_number=batch.batch_number
    )
    
    return result

@router.delete("/{data_id}", response_model=MessageResponse)
def delete_finger_blood_data(
    data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.FINGER_BLOOD_DATA, "delete"))
):
    """删除指尖血数据"""
    db_data = db.query(FingerBloodFile).filter(FingerBloodFile.finger_blood_file_id == data_id).first()
    if not db_data:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    db.delete(db_data)
    db.commit()
    return MessageResponse(message="数据删除成功")

@router.get("/export/excel")
def export_finger_blood_data(
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间筛选"),
    end_time: Optional[datetime] = Query(None, description="结束时间筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.FINGER_BLOOD_DATA, "read"))
):
    """导出指尖血数据为Excel文件"""
    try:
        # 构建查询
        query = db.query(FingerBloodFile).join(Batch).join(Person)
        
        if batch_id:
            query = query.filter(FingerBloodFile.batch_id == batch_id)
        
        if person_id:
            query = query.filter(FingerBloodFile.person_id == person_id)
        
        if start_time:
            query = query.filter(FingerBloodFile.collection_time >= start_time)
        
        if end_time:
            query = query.filter(FingerBloodFile.collection_time <= end_time)
        
        data = query.order_by(FingerBloodFile.collection_time.desc()).all()
        
        # 准备导出数据
        export_data = []
        for item in data:
            export_data.append({
                "指尖血数据ID": item.finger_blood_file_id,
                "人员姓名": item.person.person_name if item.person else "",
                "批次编号": item.batch.batch_number if item.batch else "",
                "采集时间": item.collection_time.strftime("%Y-%m-%d %H:%M:%S") if item.collection_time else "",
                "血糖值": float(item.blood_glucose_value)
            })
        
        # 创建DataFrame
        df = pd.DataFrame(export_data)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            df.to_excel(tmp_file.name, index=False, engine="openpyxl")
            temp_file_path = tmp_file.name
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"指尖血数据导出_{timestamp}.xlsx"
        
        # 记录活动日志
        log_activity(db, "导出指尖血数据", f"导出了{len(export_data)}条指尖血数据")
        
        # 返回文件
        return FileResponse(
            path=temp_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")