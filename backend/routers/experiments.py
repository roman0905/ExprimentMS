from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Experiment, Batch, Person, ExperimentMember, User, ModuleEnum
from schemas import ExperimentCreate, ExperimentUpdate, ExperimentResponse, MessageResponse, ExperimentMemberResponse
from routers.activities import log_activity
from routers.auth import get_current_user, check_module_permission

router = APIRouter(prefix="/api/experiments", tags=["实验管理"])

@router.get("/", response_model=List[ExperimentResponse])
def get_experiments(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.EXPERIMENT_MANAGEMENT, "read"))
):
    """获取实验列表"""
    query = db.query(Experiment).join(Batch)
    
    if batch_id:
        query = query.filter(Experiment.batch_id == batch_id)
    
    if person_id:
        query = query.join(ExperimentMember).filter(ExperimentMember.person_id == person_id)
    
    experiments = query.order_by(Experiment.experiment_id.desc()).offset(skip).limit(limit).all()
    
    # 添加关联信息
    result = []
    for exp in experiments:
        # 获取实验成员
        members = []
        for member in exp.members:
            person = db.query(Person).filter(Person.person_id == member.person_id).first()
            member_dict = {
                "id": member.id,
                "experiment_id": member.experiment_id,
                "person_id": member.person_id,
                "person_name": person.person_name if person else None
            }
            members.append(ExperimentMemberResponse(**member_dict))
        
        exp_dict = {
            "experiment_id": exp.experiment_id,
            "batch_id": exp.batch_id,
            "experiment_content": exp.experiment_content,
            "created_time": exp.created_time,
            "batch_number": exp.batch.batch_number if exp.batch else None,
            "members": members
        }
        result.append(ExperimentResponse(**exp_dict))
    
    return result

@router.post("/", response_model=ExperimentResponse)
def create_experiment(
    experiment: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.EXPERIMENT_MANAGEMENT, "write"))
):
    """创建新实验记录"""
    # 验证批次是否存在
    batch = db.query(Batch).filter(Batch.batch_id == experiment.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    # 验证所有成员是否存在
    for person_id in experiment.member_ids:
        person = db.query(Person).filter(Person.person_id == person_id).first()
        if not person:
            raise HTTPException(status_code=400, detail=f"人员ID {person_id} 不存在")
    
    # 验证至少有一个成员
    if not experiment.member_ids:
        raise HTTPException(status_code=400, detail="至少需要一个实验成员")
    
    # 创建实验记录
    db_experiment = Experiment(
        batch_id=experiment.batch_id,
        experiment_content=experiment.experiment_content
    )
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    
    # 添加实验成员
    members = []
    for person_id in experiment.member_ids:
        member = ExperimentMember(
            experiment_id=db_experiment.experiment_id,
            person_id=person_id
        )
        db.add(member)
        members.append(member)
    
    db.commit()
    
    # 记录活动
    member_names = []
    for member in members:
        person = db.query(Person).filter(Person.person_id == member.person_id).first()
        if person:
            member_names.append(person.person_name)
    
    activity_desc = f"创建了实验 {db_experiment.experiment_id}，批次：{batch.batch_number}，成员：{', '.join(member_names)}"
    log_activity(db, "experiment_create", activity_desc)
    
    # 构建响应
    member_responses = []
    for member in members:
        person = db.query(Person).filter(Person.person_id == member.person_id).first()
        member_dict = {
            "id": member.id,
            "experiment_id": member.experiment_id,
            "person_id": member.person_id,
            "person_name": person.person_name if person else None
        }
        member_responses.append(ExperimentMemberResponse(**member_dict))
    
    result = ExperimentResponse(
        experiment_id=db_experiment.experiment_id,
        batch_id=db_experiment.batch_id,
        experiment_content=db_experiment.experiment_content,
        created_time=db_experiment.created_time,
        batch_number=batch.batch_number,
        members=member_responses
    )
    
    return result

@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.EXPERIMENT_MANAGEMENT, "read"))
):
    """获取单个实验详情"""
    experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 获取实验成员
    members = []
    for member in experiment.members:
        person = db.query(Person).filter(Person.person_id == member.person_id).first()
        member_dict = {
            "id": member.id,
            "experiment_id": member.experiment_id,
            "person_id": member.person_id,
            "person_name": person.person_name if person else None
        }
        members.append(ExperimentMemberResponse(**member_dict))
    
    result = ExperimentResponse(
        experiment_id=experiment.experiment_id,
        batch_id=experiment.batch_id,
        experiment_content=experiment.experiment_content,
        created_time=experiment.created_time,
        batch_number=experiment.batch.batch_number if experiment.batch else None,
        members=members
    )
    
    return result

@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(
    experiment_id: int,
    experiment: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.EXPERIMENT_MANAGEMENT, "write"))
):
    """更新实验信息"""
    db_experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 验证批次是否存在
    batch = db.query(Batch).filter(Batch.batch_id == experiment.batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    # 更新基本信息
    db_experiment.batch_id = experiment.batch_id
    db_experiment.experiment_content = experiment.experiment_content
    
    # 更新成员列表（如果提供）
    if experiment.member_ids is not None:
        # 验证所有成员是否存在
        for person_id in experiment.member_ids:
            person = db.query(Person).filter(Person.person_id == person_id).first()
            if not person:
                raise HTTPException(status_code=400, detail=f"人员ID {person_id} 不存在")
        
        # 删除现有成员
        db.query(ExperimentMember).filter(ExperimentMember.experiment_id == experiment_id).delete()
        
        # 添加新成员
        for person_id in experiment.member_ids:
            member = ExperimentMember(
                experiment_id=experiment_id,
                person_id=person_id
            )
            db.add(member)
    
    db.commit()
    db.refresh(db_experiment)
    
    # 记录活动
    log_activity(db, "experiment_update", f"更新了实验 {experiment_id}")
    
    # 获取更新后的成员信息
    members = []
    for member in db_experiment.members:
        person = db.query(Person).filter(Person.person_id == member.person_id).first()
        member_dict = {
            "id": member.id,
            "experiment_id": member.experiment_id,
            "person_id": member.person_id,
            "person_name": person.person_name if person else None
        }
        members.append(ExperimentMemberResponse(**member_dict))
    
    result = ExperimentResponse(
        experiment_id=db_experiment.experiment_id,
        batch_id=db_experiment.batch_id,
        experiment_content=db_experiment.experiment_content,
        created_time=db_experiment.created_time,
        batch_number=batch.batch_number,
        members=members
    )
    
    return result

@router.delete("/{experiment_id}", response_model=MessageResponse)
def delete_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.EXPERIMENT_MANAGEMENT, "write"))
):
    """删除实验记录"""
    db_experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 记录活动
    log_activity(db, "experiment_delete", f"删除了实验 {experiment_id}")
    
    # 删除实验记录（级联删除会自动删除相关的实验成员记录）
    db.delete(db_experiment)
    db.commit()
    return MessageResponse(message="实验记录删除成功")

@router.post("/{experiment_id}/members", response_model=MessageResponse)
def add_experiment_member(
    experiment_id: int,
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.EXPERIMENT_MANAGEMENT, "write"))
):
    """为实验添加成员"""
    # 验证实验是否存在
    experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 验证人员是否存在
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    # 检查是否已经是成员
    existing_member = db.query(ExperimentMember).filter(
        ExperimentMember.experiment_id == experiment_id,
        ExperimentMember.person_id == person_id
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="该人员已经是实验成员")
    
    # 添加成员
    member = ExperimentMember(
        experiment_id=experiment_id,
        person_id=person_id
    )
    db.add(member)
    db.commit()
    
    # 记录活动
    log_activity(db, "experiment_member_add", f"为实验 {experiment_id} 添加了成员 {person.person_name}")
    
    return MessageResponse(message=f"成功添加成员 {person.person_name}")

@router.delete("/{experiment_id}/members/{person_id}", response_model=MessageResponse)
def remove_experiment_member(
    experiment_id: int,
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.EXPERIMENT_MANAGEMENT, "write"))
):
    """从实验中移除成员"""
    # 验证实验是否存在
    experiment = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 查找成员记录
    member = db.query(ExperimentMember).filter(
        ExperimentMember.experiment_id == experiment_id,
        ExperimentMember.person_id == person_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="该人员不是实验成员")
    
    # 检查是否是最后一个成员
    member_count = db.query(ExperimentMember).filter(
        ExperimentMember.experiment_id == experiment_id
    ).count()
    if member_count <= 1:
        raise HTTPException(status_code=400, detail="不能移除最后一个实验成员")
    
    # 获取人员信息用于记录
    person = db.query(Person).filter(Person.person_id == person_id).first()
    person_name = person.person_name if person else f"ID:{person_id}"
    
    # 移除成员
    db.delete(member)
    db.commit()
    
    # 记录活动
    log_activity(db, "experiment_member_remove", f"从实验 {experiment_id} 移除了成员 {person_name}")
    
    return MessageResponse(message=f"成功移除成员 {person_name}")