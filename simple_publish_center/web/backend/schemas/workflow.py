from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from models.workflow import WorkflowStatus, InstanceStatus, NodeStatus

# 工作流基础模型
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="工作流名称")
    description: Optional[str] = Field(None, max_length=500, description="工作流描述")
    tags: Optional[List[str]] = Field(None, description="标签列表")

# 创建工作流的请求体
class WorkflowCreate(WorkflowBase):
    definition: Optional[Dict[str, Any]] = Field(None, description="工作流定义")

    @validator('definition', pre=True)
    def validate_definition(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                raise ValueError("工作流定义必须是有效的JSON")
        return v

# 更新工作流的请求体
class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="工作流名称")
    description: Optional[str] = Field(None, max_length=500, description="工作流描述")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    definition: Optional[Dict[str, Any]] = Field(None, description="工作流定义")
    status: Optional[str] = Field(None, description="工作流状态")
    
    @validator('definition', pre=True)
    def validate_definition(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                raise ValueError("工作流定义必须是有效的JSON")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in WorkflowStatus]:
            raise ValueError(f"状态必须是以下之一: {[status.value for status in WorkflowStatus]}")
        return v

# 工作流的响应模型
class WorkflowResponse(WorkflowBase):
    id: str
    creator: str
    status: str
    created_at: datetime
    updated_at: datetime
    definition: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

# 工作流列表查询参数
class WorkflowQuery(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    tag: Optional[str] = None
    page: int = 1
    page_size: int = 10
    sort_by: str = "created_at"
    sort_order: str = "desc"

# 工作流运行请求体
class WorkflowRunRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = Field(None, description="运行参数")
    
    @validator('parameters', pre=True)
    def validate_parameters(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                raise ValueError("参数必须是有效的JSON")
        return v

# 工作流实例响应模型
class WorkflowInstanceResponse(BaseModel):
    id: str
    workflow_id: str
    workflow_name: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    triggered_by: str
    params: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

# 节点执行响应模型
class NodeExecutionResponse(BaseModel):
    id: str
    node_id: str
    node_name: str
    node_type: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None

    class Config:
        orm_mode = True

# 工作流实例详情响应模型
class WorkflowInstanceDetailResponse(WorkflowInstanceResponse):
    node_executions: List[NodeExecutionResponse]
    graph: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

# 工作流列表分页响应
class WorkflowListResponse(BaseModel):
    records: List[WorkflowResponse]
    total: int
    page: int
    page_size: int

# 工作流实例列表分页响应
class WorkflowInstanceListResponse(BaseModel):
    records: List[WorkflowInstanceResponse]
    total: int
    page: int
    page_size: int 