# Web界面设计与实现方案

## 设计目标

为simple_publish_center项目开发一个轻量级、前后端分离的Web界面，实现工作流的可视化管理，同时保持代码结构清晰简洁。

## 技术选型

### 后端框架
- **FastAPI**: 高性能、轻量级的Python Web框架
  - 自动生成API文档
  - 基于Python类型注解的数据验证
  - 异步支持，高性能处理请求
  - 易于扩展和集成

### 前端框架
- **Vue.js 3**: 渐进式JavaScript框架
  - 组合式API提供更灵活的组件逻辑组织
  - 轻量化设计，按需引入功能
  - 使用TypeScript增强类型安全
- **Tailwind CSS**: 实用优先的CSS框架
  - 无需编写自定义CSS，加速开发
  - 高度可定制，保持轻量
- **Axios**: 基于Promise的HTTP客户端

## 系统架构

```
                  ┌─────────────────┐
                  │   Web Browser   │
                  └────────┬────────┘
                           │
                           ▼
┌─────────────────────────────────────────────┐
│            Frontend (Vue.js + Axios)         │
└────────────────────────┬────────────────────┘
                         │ HTTP API
                         ▼
┌─────────────────────────────────────────────┐
│             Backend (FastAPI)               │
└────────────────┬────────────────┬───────────┘
                 │                │
     ┌───────────▼─────┐  ┌───────▼────────┐
     │ File Operations │  │ DolphinScheduler│
     │  (YAML/Scripts) │  │      API        │
     └─────────────────┘  └─────────────────┘
```

## API设计

### 后端API端点

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/api/workflows` | GET | 获取所有工作流配置 | - |
| `/api/workflows/{name}` | GET | 获取特定工作流配置 | `name`: 工作流名称 |
| `/api/workflows` | POST | 创建新工作流配置 | 工作流配置JSON |
| `/api/workflows/{name}` | PUT | 更新工作流配置 | `name`: 工作流名称 |
| `/api/workflows/{name}` | DELETE | 删除工作流配置 | `name`: 工作流名称 |
| `/api/template` | GET | 获取工作流模板 | - |
| `/api/template` | PUT | 更新工作流模板 | 模板内容 |
| `/api/scripts` | GET | 获取所有脚本列表 | - |
| `/api/scripts/{name}` | GET | 获取特定脚本内容 | `name`: 脚本名称 |
| `/api/deploy` | POST | 部署所有工作流 | `dry_run`: 是否仅生成配置不部署 |
| `/api/deploy/{name}` | POST | 部署单个工作流 | `name`: 工作流名称 |

### 数据模型

**工作流配置:**
```typescript
interface WorkflowConfig {
  workflow_name: string;
  workflow_description: string;
  task_id: string;
  dependent_project: string;
  dependent_workflow: string;
  dependent_task: string;
  shell_command: string;
}
```

**部署响应:**
```typescript
interface DeployResponse {
  status: "success" | "error";
  message: string;
  workflows: {
    name: string;
    status: "created" | "updated" | "failed";
    error?: string;
  }[];
}
```

## 前端页面设计

### 主要页面

1. **工作流列表页面**:
   - 表格展示所有配置的工作流
   - 过滤和搜索功能
   - 操作按钮：编辑、删除、部署单个工作流

2. **工作流编辑页面**:
   - 表单编辑工作流配置
   - Shell命令编辑器（带语法高亮）
   - 配置校验

3. **模板管理页面**:
   - 编辑工作流模板
   - 预览模板效果

4. **批量部署页面**:
   - 选择要部署的工作流
   - 部署选项配置
   - 部署结果显示

5. **脚本管理页面**:
   - 查看和编辑已生成的脚本
   - 脚本验证功能

### 组件设计

1. **工作流表格组件**:
   - 可排序列
   - 状态指示器
   - 内联操作按钮

2. **工作流表单组件**:
   - 响应式布局
   - 动态表单验证
   - 高级/基础模式切换

3. **代码编辑器组件**:
   - 语法高亮
   - 行号显示
   - 代码提示

4. **部署状态组件**:
   - 实时状态更新
   - 错误详情展示

## 实现计划

### 后端实现

1. 创建`web`目录和基本结构:
```
simple_publish_center/web/
├── backend/
│   ├── main.py        # FastAPI应用入口
│   ├── api/           # API路由
│   ├── models/        # 数据模型
│   ├── services/      # 业务逻辑
│   └── utils/         # 工具函数
└── frontend/          # 前端代码
```

2. 实现核心API逻辑:

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Workflow Manager UI")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 引入路由
from api.workflows import router as workflow_router
from api.template import router as template_router
from api.scripts import router as scripts_router
from api.deploy import router as deploy_router

app.include_router(workflow_router, prefix="/api")
app.include_router(template_router, prefix="/api")
app.include_router(scripts_router, prefix="/api")
app.include_router(deploy_router, prefix="/api")
```

### 前端实现

1. 使用Vue CLI创建项目:
```bash
npm create vue@latest simple_publish_center-ui
cd simple_publish_center-ui
npm install axios tailwindcss
```

2. 配置Vue Router并创建主要视图:
```
src/
├── assets/         # 静态资源 
├── components/     # 可复用组件
├── views/          # 页面组件
├── services/       # API调用服务
├── router/         # 路由配置
└── store/          # 状态管理
```

## 部署方案

### 开发环境

1. 后端启动:
```bash
cd simple_publish_center/web/backend
uvicorn main:app --reload
```

2. 前端启动:
```bash
cd simple_publish_center/web/frontend
npm run dev
```

### 生产环境

1. 前端构建:
```bash
cd simple_publish_center/web/frontend
npm run build
```

2. 后端部署:
   - 使用Gunicorn作为WSGI服务器
   - 使用Nginx作为反向代理
   - 可选择Docker容器化部署

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## 安全考虑

1. 实现基本身份验证
2. API请求限流
3. 定义角色和权限
4. Shell脚本内容验证和过滤
5. 生产环境下的HTTPS配置
6. 跨站请求伪造(CSRF)保护

## 后续迭代计划

1. 添加用户管理功能
2. 工作流历史版本控制
3. 环境变量管理
4. 工作流模板库
5. 定时任务和批量操作
6. 工作流执行状态监控

## 与现有模块的集成

Web界面将直接复用现有的批量创建脚本核心逻辑，确保功能一致性：

```python
# services/workflow_service.py
from pathlib import Path
import sys
import os

# 添加父级目录到Python路径以导入现有模块
sys.path.append(str(Path(__file__).parents[2]))

from batch_create_workflows import (
    render_template,
    generate_workflow_yaml,
    save_shell_script,
    batch_create_workflows
)

class WorkflowService:
    """复用现有批量创建逻辑的服务类"""
    
    @staticmethod
    def get_all_workflows():
        """获取所有工作流配置"""
        # 实现读取workflow_configs.yaml的逻辑
        
    @staticmethod
    def deploy_workflows(workflows, dry_run=False):
        """部署工作流"""
        return batch_create_workflows(workflows, "workflow_template.yaml", dry_run)
```

## 结论

这个Web界面设计充分考虑了前后端分离、轻量化和功能完整性的需求，通过FastAPI和Vue.js的组合，可以实现高效、易用的工作流管理系统，同时保持代码结构的清晰和简洁。 