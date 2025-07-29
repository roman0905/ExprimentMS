from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
import pandas as pd
import tempfile
from database import get_db
from models import CompetitorFile, Batch, Person, User, ModuleEnum
from schemas import CompetitorFileResponse, MessageResponse
from routers.activities import log_activity
from routers.auth import get_current_user, check_module_permission
from utils import format_file_size

router = APIRouter(prefix="/api/competitorFiles", tags=["竞品数据管理"])

# 文件上传目录 - 使用绝对路径确保跨平台兼容性
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "competitor_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[CompetitorFileResponse])
def get_competitor_files(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.COMPETITOR_DATA, "read"))
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
        # 获取文件大小
        file_size = None
        if os.path.exists(file.file_path):
            try:
                file_size = os.path.getsize(file.file_path)
            except OSError:
                file_size = None
        
        file_dict = {
            "competitor_file_id": file.competitor_file_id,
            "person_id": file.person_id,
            "batch_id": file.batch_id,
            "file_path": file.file_path,
            "upload_time": file.upload_time,
            "person_name": file.person.person_name if file.person else None,
            "batch_number": file.batch.batch_number if file.batch else None,
            "file_size": file_size,
            "filename": os.path.basename(file.file_path)
        }
        result.append(CompetitorFileResponse(**file_dict))
    
    return result

@router.post("/upload", response_model=CompetitorFileResponse)
async def upload_competitor_file(
    batch_id: int = Form(...),
    person_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.COMPETITOR_DATA, "write"))
):
    """上传竞品文件"""
    # 验证批次和人员是否存在
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=400, detail="指定的批次不存在")
    
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if not person:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    # 使用原始文件名，如果重名则覆盖
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 检查是否已存在相同的文件记录
    existing_file = db.query(CompetitorFile).filter(
        CompetitorFile.file_path == file_path,
        CompetitorFile.batch_id == batch_id,
        CompetitorFile.person_id == person_id
    ).first()
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 如果存在相同记录，直接返回现有记录；否则创建新记录
    if existing_file:
        db_file = existing_file
    else:
        db_file = CompetitorFile(
            person_id=person_id,
            batch_id=batch_id,
            file_path=file_path
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
    
    # 获取上传文件的大小
    file_size = None
    if os.path.exists(file_path):
        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            file_size = None
    
    result = CompetitorFileResponse(
        competitor_file_id=db_file.competitor_file_id,
        person_id=db_file.person_id,
        batch_id=db_file.batch_id,
        file_path=db_file.file_path,
        upload_time=db_file.upload_time,
        person_name=person.person_name,
        batch_number=batch.batch_number,
        file_size=file_size,
        filename=os.path.basename(db_file.file_path)
    )
    
    return result

@router.get("/download/{file_id}")
def download_competitor_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.COMPETITOR_DATA, "read"))
):
    """下载竞品文件"""
    file_record = db.query(CompetitorFile).filter(CompetitorFile.competitor_file_id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=404, detail="文件已被删除或移动")
    
    # 从文件路径提取文件名
    filename = os.path.basename(file_record.file_path)
    
    return FileResponse(
        path=file_record.file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@router.put("/{file_id}/rename", response_model=CompetitorFileResponse)
def rename_competitor_file(
    file_id: int,
    rename_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.COMPETITOR_DATA, "write"))
):
    """重命名竞品文件"""
    file_record = db.query(CompetitorFile).filter(CompetitorFile.competitor_file_id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    new_file_name = rename_data.get("new_file_name")
    if not new_file_name:
        raise HTTPException(status_code=400, detail="新文件名不能为空")
    
    # 验证文件名格式
    import re
    if not re.match(r'^[^<>:"/\\|?*]+$', new_file_name):
        raise HTTPException(status_code=400, detail="文件名包含非法字符")
    
    # 获取原文件路径和目录
    old_file_path = file_record.file_path
    file_dir = os.path.dirname(old_file_path)
    
    # 构建新文件路径
    new_file_path = os.path.join(file_dir, new_file_name)
    
    # 检查新文件是否已存在
    if os.path.exists(new_file_path) and new_file_path != old_file_path:
        raise HTTPException(status_code=400, detail="目标文件名已存在")
    
    # 重命名物理文件
    if os.path.exists(old_file_path):
        try:
            os.rename(old_file_path, new_file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件重命名失败: {str(e)}")
    
    # 更新数据库记录
    file_record.file_path = new_file_path
    db.commit()
    db.refresh(file_record)
    
    # 获取关联信息
    batch = db.query(Batch).filter(Batch.batch_id == file_record.batch_id).first()
    person = db.query(Person).filter(Person.person_id == file_record.person_id).first()
    
    # 获取文件大小
    file_size = None
    if os.path.exists(new_file_path):
        try:
            file_size = os.path.getsize(new_file_path)
        except OSError:
            file_size = None
    
    result = CompetitorFileResponse(
        competitor_file_id=file_record.competitor_file_id,
        person_id=file_record.person_id,
        batch_id=file_record.batch_id,
        file_path=file_record.file_path,
        upload_time=file_record.upload_time,
        person_name=person.person_name if person else None,
        batch_number=batch.batch_number if batch else None,
        file_size=file_size,
        filename=os.path.basename(file_record.file_path)
    )
    
    return result

@router.delete("/{file_id}", response_model=MessageResponse)
def delete_competitor_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.COMPETITOR_DATA, "delete"))
):
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

@router.get("/export")
def export_competitor_files(
    batch_id: Optional[int] = Query(None, description="按批次筛选"),
    person_id: Optional[int] = Query(None, description="按人员筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_module_permission(ModuleEnum.COMPETITOR_DATA, "read"))
):
    """导出竞品文件数据为Excel"""
    query = db.query(CompetitorFile).join(Batch).join(Person)
    
    if batch_id:
        query = query.filter(CompetitorFile.batch_id == batch_id)
    
    if person_id:
        query = query.filter(CompetitorFile.person_id == person_id)
    
    files = query.all()
    
    # 准备导出数据
    export_data = []
    for file in files:
        # 获取文件大小
        file_size = None
        if os.path.exists(file.file_path):
            try:
                file_size = os.path.getsize(file.file_path)
            except OSError:
                file_size = None
        
        # 格式化文件大小
        file_size_str = format_file_size(file_size)
        
        # 从文件路径获取文件名
        filename = os.path.basename(file.file_path) if file.file_path else "未知文件"
        
        export_data.append({
            "文件ID": file.competitor_file_id,
            "文件名": filename,
            "关联批次": file.batch.batch_number if file.batch else "未知批次",
            "关联人员": file.person.person_name if file.person else "未知人员",
            "文件大小": file_size_str,
            "文件路径": file.file_path
        })
    
    # 创建DataFrame
    df = pd.DataFrame(export_data)
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        # 写入Excel文件
        with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='竞品数据', index=False)
            
            # 调整列宽
            worksheet = writer.sheets['竞品数据']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # 记录活动
        filter_desc = []
        if batch_id:
            batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
            if batch:
                filter_desc.append(f"批次：{batch.batch_number}")
        if person_id:
            person = db.query(Person).filter(Person.person_id == person_id).first()
            if person:
                filter_desc.append(f"人员：{person.person_name}")
        
        filter_text = f"（筛选条件：{', '.join(filter_desc)}）" if filter_desc else ""
        log_activity(db, "data_export", f"导出了竞品数据{filter_text}")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"竞品数据导出_{timestamp}.xlsx"
        
        return FileResponse(
            path=tmp_file.name,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )