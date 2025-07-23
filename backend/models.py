from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class GenderEnum(enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class Batch(Base):
    __tablename__ = "batches"
    
    batch_id = Column(Integer, primary_key=True, index=True, comment="批次唯一标识符")
    batch_number = Column(String(50), unique=True, nullable=False, comment="批次号名，确保唯一性")
    start_time = Column(DateTime, nullable=False, comment="批次开始时间")
    end_time = Column(DateTime, nullable=True, comment="批次结束时间")
    
    # 关系
    experiments = relationship("Experiment", back_populates="batch")
    competitor_files = relationship("CompetitorFile", back_populates="batch")
    finger_blood_files = relationship("FingerBloodFile", back_populates="batch")
    sensors = relationship("Sensor", back_populates="batch")

class Person(Base):
    __tablename__ = "persons"
    
    person_id = Column(Integer, primary_key=True, index=True, comment="人员唯一标识符")
    person_name = Column(String(100), nullable=False, comment="人员名字")
    gender = Column(Enum(GenderEnum), nullable=True, comment="性别")
    height_cm = Column(DECIMAL(5, 2), nullable=True, comment="身高，单位厘米")
    weight_kg = Column(DECIMAL(5, 2), nullable=True, comment="体重，单位千克")
    age = Column(Integer, nullable=True, comment="年龄")
    
    # 关系
    experiments = relationship("Experiment", back_populates="person")
    competitor_files = relationship("CompetitorFile", back_populates="person")
    finger_blood_files = relationship("FingerBloodFile", back_populates="person")
    sensors = relationship("Sensor", back_populates="person")

class Experiment(Base):
    __tablename__ = "experiments"
    
    experiment_id = Column(Integer, primary_key=True, index=True, comment="实验唯一标识符")
    batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False, comment="关联的批次ID")
    person_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False, comment="关联的人员ID")
    experiment_content = Column(Text, nullable=True, comment="实验具体内容描述")
    
    # 关系
    batch = relationship("Batch", back_populates="experiments")
    person = relationship("Person", back_populates="experiments")

class CompetitorFile(Base):
    __tablename__ = "competitor_files"
    
    competitor_file_id = Column(Integer, primary_key=True, index=True, comment="竞品文件唯一标识符")
    person_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False, comment="关联的人员ID")
    batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False, comment="关联的批次ID")
    file_name = Column(String(255), nullable=False, comment="竞品文件名")
    file_path = Column(String(512), nullable=False, comment="文件存储路径")
    upload_time = Column(DateTime, default=datetime.utcnow, comment="上传时间")
    
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
    
    # 关系
    person = relationship("Person", back_populates="sensors")
    batch = relationship("Batch", back_populates="sensors")