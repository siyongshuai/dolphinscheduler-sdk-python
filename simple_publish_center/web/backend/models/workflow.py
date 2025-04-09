from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid

from core.database import Base

# 工作流状态枚举
class WorkflowStatus(str, enum.Enum):
    DRAFT = "DRAFT"  # 草稿
    DEPLOYED = "DEPLOYED"  # 已部署
    DEPRECATED = "DEPRECATED"  # 已弃用

# 工作流模型
class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String(36), nullable=False)
    definition = Column(Text, nullable=True)  # JSON格式的工作流定义
    status = Column(String(20), default=WorkflowStatus.DRAFT)
    tags = Column(String(255), nullable=True)  # 逗号分隔的标签
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    instances = relationship("WorkflowInstance", back_populates="workflow")

    def __repr__(self):
        return f"<Workflow {self.name}>"
    
    @property
    def tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",")]
    
    @tags_list.setter
    def tags_list(self, tags_list):
        if not tags_list:
            self.tags = None
        else:
            self.tags = ",".join(tags_list)

# 工作流实例状态枚举
class InstanceStatus(str, enum.Enum):
    PENDING = "PENDING"  # 等待中
    RUNNING = "RUNNING"  # 运行中
    SUCCESS = "SUCCESS"  # 成功
    FAILED = "FAILED"    # 失败
    STOPPED = "STOPPED"  # 已停止

# 工作流实例模型
class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    status = Column(String(20), default=InstanceStatus.PENDING)
    params = Column(Text, nullable=True)  # JSON格式的参数
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    triggered_by = Column(String(36), nullable=False)  # 触发用户ID
    graph = Column(Text, nullable=True)  # 执行图JSON
    
    # 关系
    workflow = relationship("Workflow", back_populates="instances")
    node_executions = relationship("NodeExecution", back_populates="instance")

    def __repr__(self):
        return f"<WorkflowInstance {self.id}>"

# 节点执行状态枚举
class NodeStatus(str, enum.Enum):
    PENDING = "PENDING"  # 等待中
    RUNNING = "RUNNING"  # 运行中
    SUCCESS = "SUCCESS"  # 成功
    FAILED = "FAILED"    # 失败
    SKIPPED = "SKIPPED"  # 已跳过

# 节点执行记录模型
class NodeExecution(Base):
    __tablename__ = "node_executions"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    instance_id = Column(String(36), ForeignKey("workflow_instances.id"), nullable=False)
    node_id = Column(String(36), nullable=False)  # 工作流定义中的节点ID
    node_name = Column(String(100), nullable=False)  # 节点名称
    node_type = Column(String(50), nullable=False)  # 节点类型
    status = Column(String(20), default=NodeStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)  # 重试次数
    output = Column(Text, nullable=True)  # 输出结果
    error = Column(Text, nullable=True)  # 错误信息
    
    # 关系
    instance = relationship("WorkflowInstance", back_populates="node_executions")

    def __repr__(self):
        return f"<NodeExecution {self.node_name}>" 