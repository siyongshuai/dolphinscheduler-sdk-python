from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from models.workflow import WorkflowInstance, NodeExecution, Workflow, InstanceStatus
from schemas.workflow import (
    WorkflowInstanceResponse, WorkflowInstanceListResponse, NodeExecutionResponse
)

router = APIRouter()

# 获取实例列表
@router.get("/instances", response_model=Dict[str, Any])
async def get_instances(
    workflow_id: Optional[str] = Query(None, description="工作流ID过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取工作流执行实例列表
    """
    # 构建查询
    query = db.query(WorkflowInstance)
    
    # 应用筛选条件
    if workflow_id:
        query = query.filter(WorkflowInstance.workflow_id == workflow_id)
    if status:
        query = query.filter(WorkflowInstance.status == status)
    
    # 按开始时间倒序排序
    query = query.order_by(WorkflowInstance.started_at.desc())
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    instances = query.offset((page - 1) * size).limit(size).all()
    
    # 构建响应
    result = []
    for instance in instances:
        # 获取关联的工作流名称
        workflow = db.query(Workflow).filter(Workflow.id == instance.workflow_id).first()
        workflow_name = workflow.name if workflow else "未知工作流"
        
        instance_data = {
            "id": instance.id,
            "workflowId": instance.workflow_id,
            "workflowName": workflow_name,
            "status": instance.status,
            "startTime": instance.started_at,
            "endTime": instance.ended_at,
            "triggeredBy": instance.triggered_by,
            "params": json.loads(instance.params) if instance.params else None
        }
        result.append(instance_data)
    
    return {
        "code": 200,
        "message": "获取实例列表成功",
        "data": {
            "records": result,
            "total": total,
            "page": page,
            "size": size
        }
    }

# 获取实例详情
@router.get("/instances/{instance_id}", response_model=Dict[str, Any])
async def get_instance_detail(
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
    
    # 获取关联的工作流
    workflow = db.query(Workflow).filter(Workflow.id == instance.workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 构建实例数据
    instance_data = {
        "id": instance.id,
        "workflowId": instance.workflow_id,
        "workflowName": workflow.name,
        "status": instance.status,
        "startTime": instance.started_at,
        "endTime": instance.ended_at,
        "triggeredBy": instance.triggered_by,
        "params": json.loads(instance.params) if instance.params else None,
        "graph": json.loads(instance.graph) if instance.graph else None
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
    # 验证实例是否存在
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    # 获取节点执行记录
    node_executions = db.query(NodeExecution).filter(NodeExecution.instance_id == instance_id).all()
    
    # 构建响应数据
    nodes_data = []
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
            "output": node.output,
            "error": node.error
        }
        nodes_data.append(node_data)
    
    return {
        "code": 200,
        "message": "获取节点执行记录成功",
        "data": nodes_data
    }

# 获取节点执行日志
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
    # 验证节点执行记录是否存在
    node_execution = db.query(NodeExecution).filter(
        NodeExecution.instance_id == instance_id,
        NodeExecution.node_id == node_id
    ).first()
    
    if not node_execution:
        raise HTTPException(status_code=404, detail="节点执行记录不存在")
    
    # 实际应用中应从日志文件中读取
    # 这里返回模拟日志
    log_content = f"""
    === 节点执行日志 ===
    节点名称: {node_execution.node_name}
    节点类型: {node_execution.node_type}
    开始时间: {node_execution.started_at}
    结束时间: {node_execution.ended_at or '未结束'}
    状态: {node_execution.status}
    
    === 执行输出 ===
    {node_execution.output or '无输出内容'}
    
    === 错误信息 ===
    {node_execution.error or '无错误信息'}
    """
    
    return {
        "code": 200,
        "message": "获取节点日志成功",
        "data": log_content.strip()
    }

# 停止实例执行
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
    
    # 更新实例状态
    instance.status = InstanceStatus.STOPPED
    instance.ended_at = datetime.utcnow()
    
    # 更新未完成的节点状态
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
        "message": "实例已停止执行",
        "data": None
    }

# 重试失败的实例
@router.post("/instances/{instance_id}/retry", response_model=Dict[str, Any])
async def retry_instance(
    instance_id: str = Path(..., description="实例ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    重试失败的工作流实例
    """
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    if instance.status != InstanceStatus.FAILED:
        raise HTTPException(status_code=400, detail="只能重试失败的实例")
    
    # 更新实例状态
    instance.status = InstanceStatus.PENDING
    instance.ended_at = None
    
    # 更新失败的节点状态
    failed_nodes = db.query(NodeExecution).filter(
        NodeExecution.instance_id == instance_id,
        NodeExecution.status == InstanceStatus.FAILED
    ).all()
    
    for node in failed_nodes:
        node.status = InstanceStatus.PENDING
        node.ended_at = None
        node.retry_count += 1
        node.error = None
    
    db.commit()
    
    # 实际应用中，这里应启动异步任务重新执行工作流
    # 简化示例，直接修改状态为运行中
    instance.status = InstanceStatus.RUNNING
    db.commit()
    
    return {
        "code": 200,
        "message": "实例已重新提交执行",
        "data": None
    } 