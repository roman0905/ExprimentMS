from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class GenderEnum(enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class RoleEnum(enum.Enum):
    Admin = "Admin"
    User = "User"

class ModuleEnum(enum.Enum):
    BATCH_MANAGEMENT = "batch_management"
    PERSON_MANAGEMENT = "person_management"
    EXPERIMENT_MANAGEMENT = "experiment_management"
    COMPETITOR_DATA = "competitor_data"
    FINGER_BLOOD_DATA = "finger_blood_data"
    SENSOR_DATA = "sensor_data"

class Batch(Base):
    __tablename__ = "batches"
    
    batch_id = Column(Integer, primary_key=True, index=True, comment="批次唯一标识符")
    batch_number = Column(String(50), unique=True, nullable=False, comment="批次号名，确保唯一性")
    start_time = Column(DateTime, nullable=False, comment="批次开始时间")
    end_time = Column(DateTime, nullable=True, comment="批次结束时间")
    
    # 关系
    persons = relationship("Person", back_populates="batch")
    experiments = relationship("Experiment", back_populates="batch")
    competitor_files = relationship("CompetitorFile", back_populates="batch")
    finger_blood_files = relationship("FingerBloodFile", back_populates="batch")
    sensors = relationship("Sensor", back_populates="batch")

class Person(Base):
    __tablename__ = "persons"
    
    person_id = Column(Integer, primary_key=True, index=True, comment="人员唯一标识符")
    person_name = Column(String(100), nullable=False, comment="人员名字")
    gender = Column(Enum(GenderEnum), nullable=True, comment="性别")
    age = Column(Integer, nullable=True, comment="年龄")
    batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=True, comment="关联的批次ID")
    
    # 关系
    batch = relationship("Batch", back_populates="persons")
    competitor_files = relationship("CompetitorFile", back_populates="person")
    finger_blood_files = relationship("FingerBloodFile", back_populates="person")
    sensors = relationship("Sensor", back_populates="person")
    experiment_members = relationship("ExperimentMember", back_populates="person")

class Experiment(Base):
    __tablename__ = "experiments"
    
    experiment_id = Column(Integer, primary_key=True, index=True, comment="实验唯一标识符")
    batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False, comment="关联的批次ID")
    experiment_content = Column(Text, nullable=True, comment="实验具体内容描述")
    created_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    
    # 关系
    batch = relationship("Batch", back_populates="experiments")
    members = relationship("ExperimentMember", back_populates="experiment", cascade="all, delete-orphan")

class CompetitorFile(Base):
    __tablename__ = "competitor_files"
    
    competitor_file_id = Column(Integer, primary_key=True, index=True, comment="竞品文件唯一标识符")
    person_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False, comment="关联的人员ID")
    batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False, comment="关联的批次ID")
    file_path = Column(String(512), nullable=False, comment="文件存储路径")
    upload_time = Column(DateTime, nullable=False, default=datetime.now, comment="文件上传时间")
    
    # 关系
    person = relationship("Person", back_populates="competitor_files")
    batch = relationship("Batch", back_populates="competitor_files")

class FingerBloodFile(Base):
    __tablename__ = "finger_blood_files"
    
    finger_blood_file_id = Column(Integer, primary_key=True, index=True, comment="指尖血文件唯一标识符")
    person_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False, comment="关联的人员ID")
    batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False, comment="关联的批次ID")
    collection_time = Column(DateTime, nullable=False, comment="采集时间")
    blood_glucose_value = Column(DECIMAL(5, 2), nullable=False, comment="血糖值")
    
    # 关系
    person = relationship("Person", back_populates="finger_blood_files")
    batch = relationship("Batch", back_populates="finger_blood_files")

class Sensor(Base):
    __tablename__ = "sensors"
    
    sensor_id = Column(Integer, primary_key=True, index=True, comment="传感器唯一标识符")
    sensor_name = Column(String(100), nullable=False, comment="传感器名称")
    person_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False, comment="关联的人员ID")
    batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False, comment="关联的批次ID")
    start_time = Column(DateTime, nullable=False, comment="传感器开始使用时间")
    end_time = Column(DateTime, nullable=True, comment="传感器结束使用时间")
    end_reason = Column(String(255), nullable=True, comment="传感器结束使用原因")
    
    # 关系
    person = relationship("Person", back_populates="sensors")
    batch = relationship("Batch", back_populates="sensors")

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, comment="用户唯一标识符")
    username = Column(String(50), unique=True, nullable=False, comment="登录用户名")
    password_hash = Column(String(255), nullable=False, comment="哈希加密后的密码")
    role = Column(Enum(RoleEnum), nullable=False, comment="用户角色 (Admin/User)")
    createTime = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updateTime = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    
    # 关系
    permissions = relationship("UserPermission", back_populates="user")

class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    permission_id = Column(Integer, primary_key=True, index=True, comment="权限唯一标识符")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="关联的用户ID")
    module = Column(Enum(ModuleEnum), nullable=False, comment="模块名称")
    can_read = Column(Boolean, default=False, comment="读取权限")
    can_write = Column(Boolean, default=False, comment="写入权限")
    can_delete = Column(Boolean, default=False, comment="删除权限")
    
    # 关系
    user = relationship("User", back_populates="permissions")

class Activity(Base):
    __tablename__ = "activities"
    
    activity_id = Column(Integer, primary_key=True, index=True, comment="活动唯一标识符")
    activity_type = Column(String(50), nullable=False, comment="活动类型")
    description = Column(Text, nullable=False, comment="活动描述")
    createTime = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, comment="操作用户ID")
    
    # 关系
    user = relationship("User")

class ExperimentMember(Base):
    __tablename__ = "experiment_members"
    
    id = Column(Integer, primary_key=True, index=True, comment="关联唯一标识符")
    experiment_id = Column(Integer, ForeignKey("experiments.experiment_id"), nullable=False, comment="实验ID")
    person_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False, comment="人员ID")
    
    # 关系
    experiment = relationship("Experiment", back_populates="members")
    person = relationship("Person", back_populates="experiment_members")