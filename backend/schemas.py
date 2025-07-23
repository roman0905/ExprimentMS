from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

# 批次相关模式
class BatchBase(BaseModel):
    batch_number: str
    start_time: datetime
    end_time: Optional[datetime] = None

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BatchBase):
    pass

class BatchResponse(BatchBase):
    batch_id: int
    
    class Config:
        from_attributes = True

# 人员相关模式
class PersonBase(BaseModel):
    person_name: str
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age: Optional[int] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class PersonResponse(PersonBase):
    person_id: int
    
    class Config:
        from_attributes = True

# 实验相关模式
class ExperimentBase(BaseModel):
    batch_id: int
    person_id: int
    experiment_content: Optional[str] = None

class ExperimentCreate(ExperimentBase):
    pass

class ExperimentUpdate(ExperimentBase):
    pass

class ExperimentResponse(ExperimentBase):
    experiment_id: int
    batch_number: Optional[str] = None
    person_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# 竞品文件相关模式
class CompetitorFileBase(BaseModel):
    person_id: int
    batch_id: int
    file_name: str

class CompetitorFileCreate(CompetitorFileBase):
    file_path: str

class CompetitorFileResponse(CompetitorFileBase):
    competitor_file_id: int
    file_path: str
    upload_time: datetime
    person_name: Optional[str] = None
    batch_number: Optional[str] = None
    
    class Config:
        from_attributes = True

# 指尖血数据相关模式
class FingerBloodDataBase(BaseModel):
    person_id: int
    batch_id: int
    collection_time: datetime
    blood_glucose_value: float

class FingerBloodDataCreate(FingerBloodDataBase):
    pass

class FingerBloodDataUpdate(FingerBloodDataBase):
    pass

class FingerBloodDataResponse(FingerBloodDataBase):
    finger_blood_file_id: int
    person_name: Optional[str] = None
    batch_number: Optional[str] = None
    
    class Config:
        from_attributes = True

# 传感器相关模式
class SensorBase(BaseModel):
    sensor_name: str
    person_id: int
    batch_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

class SensorCreate(SensorBase):
    pass

class SensorUpdate(SensorBase):
    pass

class SensorResponse(SensorBase):
    sensor_id: int
    person_name: Optional[str] = None
    batch_number: Optional[str] = None
    
    class Config:
        from_attributes = True

# 通用响应模式
class MessageResponse(BaseModel):
    message: str

# 登录相关模式
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: dict