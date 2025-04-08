# API实现指南

## 目录

- [API实现指南](#api实现指南)
  - [目录](#目录)
  - [概述](#概述)
  - [技术选型](#技术选型)
  - [项目结构](#项目结构)
  - [核心模块实现](#核心模块实现)
    - [用户认证](#用户认证)
    - [工作流管理](#工作流管理)
    - [脚本管理](#脚本管理)
    - [执行实例管理](#执行实例管理)
  - [数据模型](#数据模型)
  - [错误处理](#错误处理)
  - [安全考虑](#安全考虑)
  - [部署指南](#部署指南)

## 概述

本文档提供了API实现的详细指南，包括技术选型、项目结构、核心模块实现和部署说明。该API服务是工作流管理系统的后端核心，负责处理前端界面的请求并提供数据处理功能。

## 技术选型

后端API服务采用以下技术栈：

1. **FastAPI**：高性能、易用的Python Web框架
   - 自动生成API文档
   - 内置数据验证
   - 支持异步处理
   - 类型提示支持

2. **SQLAlchemy**：SQL工具包和ORM框架
   - 数据库模型定义
   - 数据查询和操作
   - 事务管理

3. **Pydantic**：数据验证和设置管理
   - 请求和响应模型定义
   - 数据验证和转换

4. **PyJWT**：JWT令牌处理
   - 生成和验证JWT令牌
   - 处理令牌过期和刷新

5. **Redis**：缓存和会话管理
   - 缓存频繁访问的数据
   - 存储用户会话信息
   - 实现API限流

## 项目结构

API服务的项目结构如下：

```
api/
│
├── main.py                 # 应用入口
├── config.py               # 配置管理
├── dependencies.py         # 依赖注入
│
├── routers/                # API路由
│   ├── auth.py             # 认证相关路由
│   ├── workflows.py        # 工作流相关路由
│   ├── scripts.py          # 脚本相关路由
│   ├── instances.py        # 执行实例相关路由
│   └── system.py           # 系统相关路由
│
├── models/                 # 数据库模型
│   ├── user.py             # 用户模型
│   ├── workflow.py         # 工作流模型
│   ├── script.py           # 脚本模型
│   └── instance.py         # 执行实例模型
│
├── schemas/                # 请求和响应模型
│   ├── auth.py             # 认证相关模型
│   ├── workflow.py         # 工作流相关模型
│   ├── script.py           # 脚本相关模型
│   ├── instance.py         # 执行实例相关模型
│   └── system.py           # 系统相关模型
│
├── services/               # 业务逻辑
│   ├── auth.py             # 认证服务
│   ├── workflow.py         # 工作流服务
│   ├── script.py           # 脚本服务
│   ├── instance.py         # 执行实例服务
│   └── system.py           # 系统服务
│
├── core/                   # 核心功能
│   ├── security.py         # 安全相关功能
│   ├── errors.py           # 错误处理
│   └── utils.py            # 工具函数
│
└── tests/                  # 测试代码
    ├── test_auth.py        # 认证测试
    ├── test_workflow.py    # 工作流测试
    ├── test_script.py      # 脚本测试
    └── test_instance.py    # 执行实例测试
```

## 核心模块实现

### 用户认证

用户认证模块实现JWT令牌认证机制。

**1. 登录API实现**

```python
# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.security import create_access_token, create_refresh_token
from ..services.auth import authenticate_user
from ..schemas.auth import Token, RefreshToken
from ..dependencies import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": 7200,
            "userId": user.id,
            "username": user.username,
            "role": user.role
        }
    }
```

**2. 令牌刷新API实现**

```python
# routers/auth.py
@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: RefreshToken,
    db: Session = Depends(get_db)
):
    try:
        username = verify_refresh_token(refresh_token.refreshToken)
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        access_token = create_access_token(data={"sub": username})
        
        return {
            "code": 200,
            "message": "令牌刷新成功",
            "data": {
                "accessToken": access_token,
                "expiresIn": 7200
            }
        }
    except:
        raise HTTPException(
            status_code=401,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 工作流管理

工作流管理模块处理工作流的创建、查询、更新和删除操作。

**1. 获取工作流列表API实现**

```python
# routers/workflows.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ..dependencies import get_db, get_current_user
from ..services.workflow import get_workflows
from ..schemas.workflow import WorkflowList

router = APIRouter(prefix="/api/v1/workflows", tags=["工作流"])

@router.get("", response_model=WorkflowList)
async def list_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    tag: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "createdAt",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    workflows, total = get_workflows(
        db,
        page=page,
        page_size=page_size,
        name=name,
        tag=tag,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
        user_id=current_user.id
    )
    
    return {
        "code": 200,
        "message": "成功",
        "data": {
            "total": total,
            "pages": (total + page_size - 1) // page_size,
            "current": page,
            "records": workflows
        }
    }
```

**2. 创建工作流API实现**

```python
# routers/workflows.py
from ..schemas.workflow import WorkflowCreate, WorkflowResponse

@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_workflow = create_workflow_service(
        db=db,
        workflow_data=workflow,
        user_id=current_user.id
    )
    
    return {
        "code": 200,
        "message": "工作流创建成功",
        "data": {
            "workflowId": new_workflow.id,
            "name": new_workflow.name,
            "createdAt": new_workflow.created_at
        }
    }
```

### 脚本管理

脚本管理模块处理脚本的上传、查询、更新和删除操作。

**1. 上传脚本API实现**

```python
# routers/scripts.py
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from ..dependencies import get_db, get_current_user
from ..services.script import create_script
from ..schemas.script import ScriptResponse

router = APIRouter(prefix="/api/v1/scripts", tags=["脚本"])

@router.post("", response_model=ScriptResponse)
async def upload_script(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    type: str = Form(...),
    tags: str = Form("[]"),
    file: UploadFile = File(...),
    parameters: str = Form("[]"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 处理表单数据
    tags_list = json.loads(tags)
    params_list = json.loads(parameters)
    
    # 读取文件内容
    content = await file.read()
    
    new_script = create_script(
        db=db,
        name=name,
        description=description,
        type=type,
        content=content.decode(),
        tags=tags_list,
        parameters=params_list,
        user_id=current_user.id
    )
    
    return {
        "code": 200,
        "message": "脚本上传成功",
        "data": {
            "scriptId": new_script.id,
            "name": new_script.name,
            "type": new_script.type,
            "createdAt": new_script.created_at
        }
    }
```

### 执行实例管理

执行实例管理模块处理工作流执行实例的创建、查询和控制操作。

**1. 运行工作流API实现**

```python
# routers/workflows.py
from ..schemas.workflow import RunWorkflowRequest, RunWorkflowResponse

@router.post("/{workflow_id}/run", response_model=RunWorkflowResponse)
async def run_workflow(
    workflow_id: str,
    run_request: RunWorkflowRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 检查工作流是否存在
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 创建执行实例
    instance = create_workflow_instance(
        db=db,
        workflow_id=workflow_id,
        parameters=run_request.parameters,
        run_mode=run_request.runMode,
        user_id=current_user.id
    )
    
    # 启动工作流执行
    if run_request.runMode == "ASYNC":
        # 异步执行
        background_tasks.add_task(
            execute_workflow_async, 
            instance_id=instance.id
        )
    else:
        # 同步执行
        execute_workflow_sync(instance.id)
    
    return {
        "code": 200,
        "message": "工作流运行已提交",
        "data": {
            "instanceId": instance.id,
            "workflowId": workflow_id,
            "status": "RUNNING",
            "startTime": instance.start_time
        }
    }
```

## 数据模型

系统使用SQLAlchemy ORM定义数据模型，以下是核心数据模型的实现。

**1. 用户模型**

```python
# models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
```

**2. 工作流模型**

```python
# models/workflow.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    definition = Column(Text)  # JSON格式的工作流定义
    status = Column(String)
    creator_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_run_at = Column(DateTime, nullable=True)
    
    creator = relationship("User")
    instances = relationship("WorkflowInstance", back_populates="workflow")
```

## 错误处理

系统使用统一的错误处理机制，以确保所有API返回一致的错误响应格式。

```python
# core/errors.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

class APIException(Exception):
    def __init__(self, code: int, message: str, data=None, status_code: int = 400):
        self.code = code
        self.message = message
        self.data = data
        self.status_code = status_code

def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": exc.data
        }
    )

def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": str(exc.detail),
            "data": None
        }
    )

def register_exception_handlers(app):
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
```

## 安全考虑

API实现中的安全措施包括：

1. **认证与授权**
   - 使用JWT令牌进行用户认证
   - 基于角色的访问控制
   - 令牌自动过期和刷新机制

2. **请求验证**
   - 使用Pydantic模型进行请求数据验证
   - 参数类型和格式检查
   - 业务规则验证

3. **防护措施**
   - CORS配置，限制跨域请求
   - 请求限流，防止DDoS攻击
   - 参数转义，防止SQL注入
   - 请求日志记录，便于审计

## 部署指南

API服务支持多种部署方式，以下是推荐的部署步骤：

1. **Docker部署**

```bash
# 构建Docker镜像
docker build -t workflow-api .

# 运行容器
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@db:5432/workflow" \
  -e SECRET_KEY="your-secret-key" \
  -e REDIS_URL="redis://redis:6379/0" \
  --name workflow-api \
  workflow-api
```

2. **Kubernetes部署**

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-api
  template:
    metadata:
      labels:
        app: workflow-api
    spec:
      containers:
      - name: workflow-api
        image: workflow-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: secret-key
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "0.5"
            memory: "256Mi"
```

3. **配置Nginx作为反向代理**

```nginx
# nginx.conf
server {
    listen 80;
    server_name api.workflow.example.com;

    location / {
        proxy_pass http://workflow-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
``` 