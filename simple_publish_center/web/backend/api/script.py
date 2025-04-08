from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
import json
import uuid
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from core.config import settings
from models.script import Script, ScriptType, ScriptLanguage
from schemas.workflow import ScriptCreate, ScriptUpdate, ScriptResponse

router = APIRouter()

# 获取脚本列表
@router.get("/scripts", response_model=Dict[str, Any])
async def get_scripts(
    script_type: Optional[str] = Query(None, description="脚本类型过滤"),
    language: Optional[str] = Query(None, description="脚本语言过滤"),
    name: Optional[str] = Query(None, description="脚本名称搜索"),
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取脚本列表
    """
    # 构建查询
    query = db.query(Script)
    
    # 应用筛选条件
    if script_type:
        query = query.filter(Script.type == script_type)
    if language:
        query = query.filter(Script.language == language)
    if name:
        query = query.filter(Script.name.ilike(f"%{name}%"))
    
    # 按创建时间倒序排序
    query = query.order_by(Script.created_at.desc())
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    scripts = query.offset((page - 1) * size).limit(size).all()
    
    # 构建响应
    result = []
    for script in scripts:
        script_data = {
            "id": script.id,
            "name": script.name,
            "type": script.type,
            "language": script.language,
            "description": script.description,
            "created_at": script.created_at,
            "updated_at": script.updated_at,
            "created_by": script.created_by
        }
        result.append(script_data)
    
    return {
        "code": 200,
        "message": "获取脚本列表成功",
        "data": {
            "records": result,
            "total": total,
            "page": page,
            "size": size
        }
    }

# 创建脚本
@router.post("/scripts", response_model=Dict[str, Any])
async def create_script(
    script_data: ScriptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建新脚本
    """
    # 检查同名脚本是否存在
    existing_script = db.query(Script).filter(Script.name == script_data.name).first()
    if existing_script:
        raise HTTPException(status_code=400, detail="同名脚本已存在")
    
    # 创建脚本记录
    script_id = str(uuid.uuid4())
    new_script = Script(
        id=script_id,
        name=script_data.name,
        description=script_data.description,
        type=script_data.type,
        language=script_data.language,
        content=script_data.content,
        created_by=current_user.username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_script)
    db.commit()
    db.refresh(new_script)
    
    # 保存脚本文件
    script_dir = os.path.join(settings.SCRIPTS_DIR, script_id)
    os.makedirs(script_dir, exist_ok=True)
    
    file_extension = ".py" if script_data.language == ScriptLanguage.PYTHON else ".sh"
    file_path = os.path.join(script_dir, f"script{file_extension}")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_data.content)
    
    return {
        "code": 200,
        "message": "创建脚本成功",
        "data": {
            "id": new_script.id,
            "name": new_script.name
        }
    }

# 获取脚本详情
@router.get("/scripts/{script_id}", response_model=Dict[str, Any])
async def get_script_detail(
    script_id: str = Path(..., description="脚本ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取脚本详情
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    script_data = {
        "id": script.id,
        "name": script.name,
        "description": script.description,
        "type": script.type,
        "language": script.language,
        "content": script.content,
        "created_at": script.created_at,
        "updated_at": script.updated_at,
        "created_by": script.created_by
    }
    
    return {
        "code": 200,
        "message": "获取脚本详情成功",
        "data": script_data
    }

# 更新脚本
@router.put("/scripts/{script_id}", response_model=Dict[str, Any])
async def update_script(
    script_id: str = Path(..., description="脚本ID"),
    script_data: ScriptUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新脚本内容
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    # 检查同名脚本
    if script_data.name != script.name:
        existing_script = db.query(Script).filter(Script.name == script_data.name).first()
        if existing_script:
            raise HTTPException(status_code=400, detail="同名脚本已存在")
    
    # 更新脚本记录
    script.name = script_data.name
    script.description = script_data.description
    script.content = script_data.content
    script.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(script)
    
    # 更新脚本文件
    script_dir = os.path.join(settings.SCRIPTS_DIR, script_id)
    os.makedirs(script_dir, exist_ok=True)
    
    file_extension = ".py" if script.language == ScriptLanguage.PYTHON else ".sh"
    file_path = os.path.join(script_dir, f"script{file_extension}")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_data.content)
    
    return {
        "code": 200,
        "message": "更新脚本成功",
        "data": {
            "id": script.id,
            "name": script.name
        }
    }

# 删除脚本
@router.delete("/scripts/{script_id}", response_model=Dict[str, Any])
async def delete_script(
    script_id: str = Path(..., description="脚本ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除脚本
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    # 删除脚本记录
    db.delete(script)
    db.commit()
    
    # 删除脚本文件
    script_dir = os.path.join(settings.SCRIPTS_DIR, script_id)
    if os.path.exists(script_dir):
        import shutil
        shutil.rmtree(script_dir)
    
    return {
        "code": 200,
        "message": "删除脚本成功",
        "data": None
    }

# 测试脚本执行
@router.post("/scripts/{script_id}/test", response_model=Dict[str, Any])
async def test_script(
    script_id: str = Path(..., description="脚本ID"),
    parameters: Dict[str, Any] = Body({}, description="测试参数"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    测试脚本执行
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    # 实际应用中应启动子进程执行脚本并返回结果
    # 这里只返回模拟结果
    
    # 根据脚本类型执行不同的测试
    if script.type == ScriptType.DATA_COLLECTION:
        result = {
            "success": True,
            "data": [
                {"id": 1, "name": "测试数据1", "value": 100},
                {"id": 2, "name": "测试数据2", "value": 200}
            ],
            "execution_time": "1.24s"
        }
    elif script.type == ScriptType.DATA_PROCESSING:
        result = {
            "success": True,
            "processed_rows": 245,
            "execution_time": "2.56s"
        }
    else:
        result = {
            "success": True,
            "output": "脚本执行成功",
            "execution_time": "0.87s"
        }
    
    return {
        "code": 200,
        "message": "脚本测试执行成功",
        "data": {
            "script_id": script_id,
            "script_name": script.name,
            "result": result
        }
    }

# 上传脚本文件
@router.post("/scripts/upload", response_model=Dict[str, Any])
async def upload_script(
    file: UploadFile = File(...),
    script_name: str = Query(..., description="脚本名称"),
    script_type: str = Query(..., description="脚本类型"),
    language: str = Query(..., description="脚本语言"),
    description: str = Query("", description="脚本描述"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    上传脚本文件
    """
    # 检查同名脚本
    existing_script = db.query(Script).filter(Script.name == script_name).first()
    if existing_script:
        raise HTTPException(status_code=400, detail="同名脚本已存在")
    
    # 检查文件类型
    file_ext = os.path.splitext(file.filename)[1].lower()
    if (language == ScriptLanguage.PYTHON and file_ext != ".py") or \
       (language == ScriptLanguage.SHELL and file_ext != ".sh"):
        raise HTTPException(status_code=400, detail="文件类型与脚本语言不匹配")
    
    # 读取文件内容
    content = await file.read()
    content_str = content.decode("utf-8")
    
    # 创建脚本记录
    script_id = str(uuid.uuid4())
    new_script = Script(
        id=script_id,
        name=script_name,
        description=description,
        type=script_type,
        language=language,
        content=content_str,
        created_by=current_user.username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_script)
    db.commit()
    db.refresh(new_script)
    
    # 保存脚本文件
    script_dir = os.path.join(settings.SCRIPTS_DIR, script_id)
    os.makedirs(script_dir, exist_ok=True)
    
    file_path = os.path.join(script_dir, f"script{file_ext}")
    
    with open(file_path, "wb") as f:
        await file.seek(0)
        f.write(await file.read())
    
    return {
        "code": 200,
        "message": "上传脚本成功",
        "data": {
            "id": new_script.id,
            "name": new_script.name
        }
    } 