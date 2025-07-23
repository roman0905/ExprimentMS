from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Experiment, Batch, Person
from schemas import ExperimentCreate, ExperimentUpdate, ExperimentResponse, MessageResponse

router = APIRouter(prefix="/api/experiments", tags=["实验管理"])

@router.get("/", response_model=List[ExperimentResponse])
def get_experiments(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    db: Session = Depends(get_db)
):
    """获取实验列表"""
    query = db.query(Experiment).join(Batch).join(Person)
    
    if batch_id:
        query = query.filter(Experiment.batch_id == batch_id)
    
    if person_id:
        query = query.filter(Experiment.person_id == person_id)
    
    experiments = query.offset(skip).limit(limit).all()
    
    # 添加关联信息
    result = []
    for exp in experiments:
        exp_dict = {
            "experiment_id": exp.experiment_id,
            "batch_id": exp.batch_id,
            "person_id": exp.person_id,
            "experiment_content": exp.experiment_content,
            "batch_number": exp.batch.batch_number if exp.batch else None,
            "person_name": exp.person.person_name if exp.person else None
        }
        result.append(ExperimentResponse(**exp_dict))
    
    return result

@router.post("/", response_model=ExperimentResponse)
def create_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    """创建新实验记录"""
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == experiment.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == experiment.person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    db_experiment = Experiment(**experiment.dict())
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    
    # 返回包含关联信息的响应
    result = ExperimentResponse(
        experiment_id=db_experiment.experiment_id,
        batch_id=db_experiment.batch_id,
        person_id=db_experiment.person_id,
        experiment_content=db_experiment.experiment_content,
        batch_number=batch.batch_number,
        person_name=person.person_name
    )
    
    return result

@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """获取单个实验详情"""
    experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    result = ExperimentResponse(
        experiment_id=experiment.experiment_id,
        batch_id=experiment.batch_id,
        person_id=experiment.person_id,
        experiment_content=experiment.experiment_content,
        batch_number=experiment.batch.batch_number if experiment.batch else None,
        person_name=experiment.person.person_name if experiment.person else None
    )
    
    return result

@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(experiment_id: int, experiment: ExperimentUpdate, db: Session = Depends(get_db)):
    """更新实验信息"""
    db_experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == experiment.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == experiment.person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    for field, value in experiment.dict().items():
        setattr(db_experiment, field, value)
    
    db.commit()
    db.refresh(db_experiment)
    
    result = ExperimentResponse(
        experiment_id=db_experiment.experiment_id,
        batch_id=db_experiment.batch_id,
        person_id=db_experiment.person_id,
        experiment_content=db_experiment.experiment_content,
        batch_number=batch.batch_number,
        person_name=person.person_name
    )
    
    return result

@router.delete("/{experiment_id}", response_model=MessageResponse)
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """删除实验记录"""
    db_experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    db.delete(db_experiment)
    db.commit()
    return MessageResponse(message="实验记录删除成功")