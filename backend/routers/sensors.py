from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Sensor, Batch, Person, User
from schemas import SensorCreate, SensorUpdate, SensorResponse, MessageResponse
from routers.auth import get_current_user, check_module_permission
from models import ModuleEnum

router = APIRouter(prefix="/api/sensors", tags=["传感器管理"])

@router.get("/", response_model=List[SensorResponse])
def get_sensors(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.SENSOR_DATA, "read"))
):
    """获取传感器列表"""
    query = db.query(Sensor).join(Batch).join(Person)
    
    if batch_id:
        query = query.filter(Sensor.batch_id == batch_id)
    
    if person_id:
        query = query.filter(Sensor.person_id == person_id)
    
    sensors = query.offset(skip).limit(limit).all()
    
    # 添加关联信息
    result = []
    for sensor in sensors:
        sensor_dict = {
            "sensor_id": sensor.sensor_id,
            "sensor_name": sensor.sensor_name,
            "person_id": sensor.person_id,
            "batch_id": sensor.batch_id,
            "start_time": sensor.start_time,
            "end_time": sensor.end_time,
            "end_reason": sensor.end_reason,
            "person_name": sensor.person.person_name if sensor.person else None,
            "batch_number": sensor.batch.batch_number if sensor.batch else None
        }
        result.append(SensorResponse(**sensor_dict))
    
    return result

@router.post("/", response_model=SensorResponse)
def create_sensor(
    sensor: SensorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.SENSOR_DATA, "write"))
):
    """新增传感器记录"""
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == sensor.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == sensor.person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    db_sensor = Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    
    result = SensorResponse(
        sensor_id=db_sensor.sensor_id,
        sensor_name=db_sensor.sensor_name,
        person_id=db_sensor.person_id,
        batch_id=db_sensor.batch_id,
        start_time=db_sensor.start_time,
        end_time=db_sensor.end_time,
        end_reason=db_sensor.end_reason,
        person_name=person.person_name,
        batch_number=batch.batch_number
    )
    
    return result

@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.SENSOR_DATA, "read"))
):
    """获取单个传感器详情"""
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="传感器不存在")
    
    result = SensorResponse(
        sensor_id=sensor.sensor_id,
        sensor_name=sensor.sensor_name,
        person_id=sensor.person_id,
        batch_id=sensor.batch_id,
        start_time=sensor.start_time,
        end_time=sensor.end_time,
        end_reason=sensor.end_reason,
        person_name=sensor.person.person_name if sensor.person else None,
        batch_number=sensor.batch.batch_number if sensor.batch else None
    )
    
    return result

@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(
    sensor_id: int,
    sensor: SensorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.SENSOR_DATA, "write"))
):
    """更新传感器信息"""
    db_sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="传感器不存在")
    
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == sensor.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == sensor.person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    for field, value in sensor.dict().items():
        setattr(db_sensor, field, value)
    
    db.commit()
    db.refresh(db_sensor)
    
    result = SensorResponse(
        sensor_id=db_sensor.sensor_id,
        sensor_name=db_sensor.sensor_name,
        person_id=db_sensor.person_id,
        batch_id=db_sensor.batch_id,
        start_time=db_sensor.start_time,
        end_time=db_sensor.end_time,
        end_reason=db_sensor.end_reason,
        person_name=person.person_name,
        batch_number=batch.batch_number
    )
    
    return result

@router.delete("/{sensor_id}", response_model=MessageResponse)
def delete_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.SENSOR_DATA, "delete"))
):
    """删除传感器记录"""
    db_sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="传感器不存在")
    
    db.delete(db_sensor)
    db.commit()
    return MessageResponse(message="传感器记录删除成功")