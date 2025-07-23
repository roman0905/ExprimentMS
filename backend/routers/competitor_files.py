from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
from database import get_db
from models import CompetitorFile, Batch, Person
from schemas import CompetitorFileResponse, MessageResponse

router = APIRouter(prefix="/api/competitor-files", tags=["竞品数据管理"])

# 文件上传目录
UPLOAD_DIR = "uploads/competitor_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[CompetitorFileResponse])
def get_competitor_files(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    db: Session = Depends(get_db)
):
    """获取竞品文件列表"""
    query = db.query(CompetitorFile).join(Batch).join(Person)
    
    if batch_id:
        query = query.filter(CompetitorFile.batch_id == batch_id)
    
    if person_id:
        query = query.filter(CompetitorFile.person_id == person_id)
    
    files = query.offset(skip).limit(limit).all()
    
    # 添加关联信息
    result = []
    for file in files:
        file_dict = {
            "competitor_file_id": file.competitor_file_id,
            "person_id": file.person_id,
            "batch_id": file.batch_id,
            "file_path": file.file_path,
            "person_name": file.person.person_name if file.person else None,
            "batch_number": file.batch.batch_number if file.batch else None
        }
        result.append(CompetitorFileResponse(**file_dict))
    
    return result

@router.post("/upload", response_model=CompetitorFileResponse)
async def upload_competitor_file(
    batch_id: int = Form(...),
    person_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传竞品文件"""
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 保存文件信息到数据库
    db_file = CompetitorFile(
        person_id=person_id,
        batch_id=batch_id,
        file_path=file_path
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    result = CompetitorFileResponse(
        competitor_file_id=db_file.competitor_file_id,
        person_id=db_file.person_id,
        batch_id=db_file.batch_id,
        file_path=db_file.file_path,
        person_name=person.person_name,
        batch_number=batch.batch_number
    )
    
    return result

@router.get("/download/{file_id}")
def download_competitor_file(file_id: int, db: Session = Depends(get_db)):
    """下载竞品文件"""
    file_record = db.query(CompetitorFile).filter(CompetitorFile.competitor_file_id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=404, detail="文件已被删除或移动")
    
    # 从文件路径中提取文件名
    filename = os.path.basename(file_record.file_path)
    
    return FileResponse(
        path=file_record.file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@router.delete("/{file_id}", response_model=MessageResponse)
def delete_competitor_file(file_id: int, db: Session = Depends(get_db)):
    """删除竞品文件"""
    file_record = db.query(CompetitorFile).filter(CompetitorFile.competitor_file_id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除物理文件
    if os.path.exists(file_record.file_path):
        try:
            os.remove(file_record.file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")
    
    # 删除数据库记录
    db.delete(file_record)
    db.commit()
    
    return MessageResponse(message="文件删除成功")