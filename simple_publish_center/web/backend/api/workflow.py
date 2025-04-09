from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from models.workflow import Workflow, WorkflowInstance, NodeExecution, WorkflowStatus, InstanceStatus
from schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowListResponse,
    WorkflowRunRequest, WorkflowInstanceResponse, WorkflowInstanceDetailResponse,
    WorkflowInstanceListResponse, NodeExecutionResponse
)

router = APIRouter()

# 获取工作流列表
@router.get("/workflows", response_model=WorkflowListResponse)
async def get_workflows(
    name: Optional[str] = Query(None, description="工作流名称搜索"),
    status: Optional[str] = Query(None, description="工作流状态筛选"),
    tag: Optional[str] = Query(None, description="标签筛选"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取工作流列表，支持分页、排序和筛选
    """
    # 构建查询
    query = db.query(Workflow)
    
    # 应用筛选条件
    if name:
        query = query.filter(Workflow.name.like(f"%{name}%"))
    if status:
        query = query.filter(Workflow.status == status)
    if tag:
        query = query.filter(Workflow.tags.like(f"%{tag}%"))
    
    # 应用排序
    if sort_order.lower() == "asc":
        query = query.order_by(getattr(Workflow, sort_by))
    else:
        query = query.order_by(getattr(Workflow, sort_by).desc())
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    workflows = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 构建响应
    result = []
    for workflow in workflows:
        workflow_data = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "tags": workflow.tags_list,
            "status": workflow.status,
            "creator": "admin",  # 实际应用中应该关联用户表
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at,
            "definition": json.loads(workflow.definition) if workflow.definition else None
        }
        result.append(workflow_data)
    
    return {
        "records": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }

# 创建工作流
@router.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(
    workflow: WorkflowCreate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建新的工作流
    """
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        creator_id=current_user.username,  # 实际应用中应使用用户ID
        definition=json.dumps(workflow.definition) if workflow.definition else None,
        status=WorkflowStatus.DRAFT
    )
    
    if workflow.tags:
        db_workflow.tags_list = workflow.tags
    
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    
    return {
        "code": 200,
        "message": "工作流创建成功",
        "data": {
            "id": db_workflow.id,
            "name": db_workflow.name
        }
    }

# 获取工作流详情
@router.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(
    workflow_id: str = Path(..., description="工作流ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取工作流详情
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    workflow_data = {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "tags": workflow.tags_list,
        "status": workflow.status,
        "creator": "admin",  # 实际应用中应该关联用户表
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
        "definition": json.loads(workflow.definition) if workflow.definition else None
    }
    
    return {
        "code": 200,
        "message": "获取工作流成功",
        "data": workflow_data
    }

# 更新工作流
@router.put("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def update_workflow(
    workflow_id: str = Path(..., description="工作流ID"),
    workflow_update: WorkflowUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新工作流信息
    """
    db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    if workflow_update.name is not None:
        db_workflow.name = workflow_update.name
    if workflow_update.description is not None:
        db_workflow.description = workflow_update.description
    if workflow_update.tags is not None:
        db_workflow.tags_list = workflow_update.tags
    if workflow_update.definition is not None:
        db_workflow.definition = json.dumps(workflow_update.definition)
    if workflow_update.status is not None:
        db_workflow.status = workflow_update.status
    
    db_workflow.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_workflow)
    
    return {
        "code": 200,
        "message": "工作流更新成功",
        "data": {
            "id": db_workflow.id,
            "name": db_workflow.name
        }
    }

# 删除工作流
@router.delete("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def delete_workflow(
    workflow_id: str = Path(..., description="工作流ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除工作流
    """
    db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 检查是否有关联的实例
    instances = db.query(WorkflowInstance).filter(WorkflowInstance.workflow_id == workflow_id).count()
    if instances > 0:
        raise HTTPException(status_code=400, detail="该工作流有关联的执行实例，无法删除")
    
    db.delete(db_workflow)
    db.commit()
    
    return {
        "code": 200,
        "message": "工作流删除成功",
        "data": None
    }

# 运行工作流
@router.post("/workflows/{workflow_id}/run", response_model=Dict[str, Any])
async def run_workflow(
    workflow_id: str = Path(..., description="工作流ID"),
    run_request: WorkflowRunRequest = Body(default={}),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    运行工作流
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    if workflow.status != WorkflowStatus.DEPLOYED:
        raise HTTPException(status_code=400, detail="只能运行已部署的工作流")
    
    # 创建工作流实例
    instance = WorkflowInstance(
        workflow_id=workflow_id,
        status=InstanceStatus.PENDING,
        params=json.dumps(run_request.parameters) if run_request.parameters else None,
        triggered_by=current_user.username,  # 实际应用中应使用用户ID
        graph=workflow.definition  # 复制工作流定义作为执行图
    )
    
    db.add(instance)
    db.commit()
    db.refresh(instance)
    
    # 实际应用中，这里应启动异步任务执行工作流
    # 简化示例，直接修改状态为运行中
    instance.status = InstanceStatus.RUNNING
    db.commit()
    
    return {
        "code": 200,
        "message": "工作流已提交运行",
        "data": {
            "instance_id": instance.id
        }
    }

# 部署工作流
@router.post("/workflows/{workflow_id}/deploy", response_model=Dict[str, Any])
async def deploy_workflow(
    workflow_id: str = Path(..., description="工作流ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    部署工作流，将状态更改为已部署
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    if not workflow.definition:
        raise HTTPException(status_code=400, detail="工作流定义为空，无法部署")
    
    workflow.status = WorkflowStatus.DEPLOYED
    workflow.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "code": 200,
        "message": "工作流部署成功",
        "data": None
    }

# 获取工作流的执行实例列表
@router.get("/workflows/{workflow_id}/instances", response_model=WorkflowInstanceListResponse)
async def get_workflow_instances(
    workflow_id: str = Path(..., description="工作流ID"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取工作流的执行实例列表
    """
    # 检查工作流是否存在
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 查询实例
    query = db.query(WorkflowInstance).filter(WorkflowInstance.workflow_id == workflow_id)
    
    # 按开始时间倒序排序
    query = query.order_by(WorkflowInstance.started_at.desc())
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    instances = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 构建响应
    result = []
    for instance in instances:
        instance_data = {
            "id": instance.id,
            "workflow_id": instance.workflow_id,
            "workflow_name": workflow.name,
            "status": instance.status,
            "started_at": instance.started_at,
            "ended_at": instance.ended_at,
            "triggered_by": instance.triggered_by,
            "params": json.loads(instance.params) if instance.params else None
        }
        result.append(instance_data)
    
    return {
        "records": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }

# 停止工作流实例
@router.post("/instances/{instance_id}/stop", response_model=Dict[str, Any])
async def stop_instance(
    instance_id: str = Path(..., description="实例ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    停止正在运行的工作流实例
    """
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    if instance.status != InstanceStatus.RUNNING:
        raise HTTPException(status_code=400, detail="只能停止运行中的实例")
    
    # 实际应用中，这里应该发送停止信号给执行引擎
    # 简化示例，直接修改状态
    instance.status = InstanceStatus.STOPPED
    instance.ended_at = datetime.utcnow()
    
    # 更新所有未完成的节点执行记录为已停止
    running_nodes = db.query(NodeExecution).filter(
        NodeExecution.instance_id == instance_id,
        NodeExecution.status.in_([InstanceStatus.PENDING, InstanceStatus.RUNNING])
    ).all()
    
    for node in running_nodes:
        node.status = InstanceStatus.STOPPED
        node.ended_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "code": 200,
        "message": "实例已停止",
        "data": None
    }

# 获取工作流实例详情
@router.get("/instances/{instance_id}", response_model=Dict[str, Any])
async def get_instance(
    instance_id: str = Path(..., description="实例ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取工作流实例详情
    """
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    workflow = db.query(Workflow).filter(Workflow.id == instance.workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="关联的工作流不存在")
    
    # 获取节点执行记录
    node_executions = db.query(NodeExecution).filter(NodeExecution.instance_id == instance_id).all()
    
    # 构建节点执行数据
    nodes_data = []
    for node in node_executions:
        node_data = {
            "id": node.id,
            "node_id": node.node_id,
            "node_name": node.node_name,
            "node_type": node.node_type,
            "status": node.status,
            "started_at": node.started_at,
            "ended_at": node.ended_at,
            "output": node.output,
            "error": node.error
        }
        nodes_data.append(node_data)
    
    # 构建实例数据
    instance_data = {
        "id": instance.id,
        "workflow_id": instance.workflow_id,
        "workflow_name": workflow.name,
        "status": instance.status,
        "started_at": instance.started_at,
        "ended_at": instance.ended_at,
        "triggered_by": instance.triggered_by,
        "params": json.loads(instance.params) if instance.params else None,
        "graph": json.loads(instance.graph) if instance.graph else None,
        "node_executions": nodes_data
    }
    
    return {
        "code": 200,
        "message": "获取实例详情成功",
        "data": instance_data
    }

# 获取节点执行记录
@router.get("/instances/{instance_id}/nodes", response_model=Dict[str, Any])
async def get_node_executions(
    instance_id: str = Path(..., description="实例ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取工作流实例的节点执行记录
    """
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    # 获取节点执行记录
    node_executions = db.query(NodeExecution).filter(NodeExecution.instance_id == instance_id).all()
    
    # 构建响应
    result = []
    for node in node_executions:
        node_data = {
            "id": node.id,
            "nodeId": node.node_id,
            "nodeName": node.node_name,
            "nodeType": node.node_type,
            "status": node.status,
            "startTime": node.started_at,
            "endTime": node.ended_at,
            "retryCount": node.retry_count,
            "error": node.error
        }
        result.append(node_data)
    
    return {
        "code": 200,
        "message": "获取节点执行记录成功",
        "data": result
    }

# 获取节点日志
@router.get("/instances/{instance_id}/nodes/{node_id}/logs", response_model=Dict[str, Any])
async def get_node_logs(
    instance_id: str = Path(..., description="实例ID"),
    node_id: str = Path(..., description="节点ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取节点执行日志
    """
    node_execution = db.query(NodeExecution).filter(
        NodeExecution.instance_id == instance_id,
        NodeExecution.node_id == node_id
    ).first()
    
    if not node_execution:
        raise HTTPException(status_code=404, detail="节点执行记录不存在")
    
    # 实际应用中，应该从日志文件中读取日志
    # 简化示例，返回模拟日志
    log_content = f"""
    === 节点执行日志 ===
    节点名称: {node_execution.node_name}
    节点类型: {node_execution.node_type}
    开始时间: {node_execution.started_at}
    结束时间: {node_execution.ended_at or '未结束'}
    状态: {node_execution.status}
    
    === 输出内容 ===
    {node_execution.output or '无输出'}
    
    === 错误信息 ===
    {node_execution.error or '无错误'}
    """
    
    return {
        "code": 200,
        "message": "获取节点日志成功",
        "data": log_content.strip()
    } 