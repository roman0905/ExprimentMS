from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 基础配置类，统一datetime格式
class BaseModelWithConfig(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None
        }
    )

class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class RoleEnum(str, Enum):
    Admin = "Admin"
    User = "User"

class ModuleEnum(str, Enum):
    BATCH_MANAGEMENT = "batch_management"
    PERSON_MANAGEMENT = "person_management"
    EXPERIMENT_MANAGEMENT = "experiment_management"
    COMPETITOR_DATA = "competitor_data"
    FINGER_BLOOD_DATA = "finger_blood_data"
    SENSOR_DATA = "sensor_data"

# 批次相关模式
class BatchBase(BaseModelWithConfig):
    batch_number: str
    start_time: datetime
    end_time: Optional[datetime] = None

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BatchBase):
    pass

class BatchResponse(BatchBase):
    batch_id: int

# 人员相关模式
class PersonBase(BaseModel):
    person_name: str
    gender: Optional[GenderEnum] = None
    age: Optional[int] = None
    batch_id: Optional[int] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class PersonResponse(PersonBase):
    person_id: int
    batch_number: Optional[str] = None
    
    class Config:
        from_attributes = True

# 实验相关模式
class ExperimentMemberBase(BaseModel):
    person_id: int

class ExperimentMemberResponse(ExperimentMemberBase):
    id: int
    experiment_id: int
    person_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class ExperimentBase(BaseModel):
    batch_id: int
    experiment_content: Optional[str] = None

class ExperimentCreate(ExperimentBase):
    member_ids: List[int] = []

class ExperimentUpdate(BaseModel):
    batch_id: Optional[int] = None
    experiment_content: Optional[str] = None
    member_ids: Optional[List[int]] = None

class ExperimentResponse(BaseModelWithConfig):
    experiment_id: int
    batch_id: int
    experiment_content: Optional[str] = None
    created_time: Optional[datetime] = None
    batch_number: Optional[str] = None
    members: List[ExperimentMemberResponse] = []

# 竞品文件相关模式
class CompetitorFileBase(BaseModel):
    person_id: int
    batch_id: int
    file_path: str

class CompetitorFileCreate(CompetitorFileBase):
    pass

class CompetitorFileResponse(BaseModelWithConfig):
    competitor_file_id: int
    person_id: int
    batch_id: int
    file_path: str
    upload_time: datetime
    person_name: Optional[str] = None
    batch_number: Optional[str] = None
    file_size: Optional[int] = None  # 文件大小（字节）
    filename: Optional[str] = None  # 从文件路径提取的文件名

# 指尖血数据相关模式
class FingerBloodDataBase(BaseModelWithConfig):
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

# 传感器相关模式
class SensorBase(BaseModelWithConfig):
    sensor_name: str
    person_id: int
    batch_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    end_reason: Optional[str] = None

class SensorCreate(SensorBase):
    pass

class SensorUpdate(SensorBase):
    pass

class SensorResponse(SensorBase):
    sensor_id: int
    person_name: Optional[str] = None
    batch_number: Optional[str] = None

# 通用响应模式
class MessageResponse(BaseModel):
    message: str

# 用户权限相关模式
class UserPermissionBase(BaseModel):
    module: ModuleEnum
    can_read: bool = False
    can_write: bool = False
    can_delete: bool = False

class UserPermissionCreate(UserPermissionBase):
    user_id: int

class UserPermissionUpdate(UserPermissionBase):
    pass

class UserPermissionResponse(UserPermissionBase):
    permission_id: int
    user_id: int
    
    class Config:
        from_attributes = True

# 用户相关模式
class UserBase(BaseModel):
    username: str
    role: RoleEnum

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None

class UserResponse(BaseModelWithConfig):
    user_id: int
    username: str
    role: RoleEnum
    createTime: datetime
    updateTime: datetime
    permissions: List[UserPermissionResponse] = []

class UserListResponse(BaseModelWithConfig):
    user_id: int
    username: str
    role: RoleEnum
    createTime: datetime
    updateTime: datetime

# 登录相关模式
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

# 权限分配相关模式
class AssignPermissionsRequest(BaseModel):
    user_id: int
    permissions: List[UserPermissionBase]

# 活动记录相关模式
class ActivityBase(BaseModel):
    activity_type: str
    description: str

class ActivityCreate(ActivityBase):
    user_id: Optional[int] = None

class ActivityResponse(ActivityBase):
    activity_id: int
    createTime: datetime
    user_id: Optional[int] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True