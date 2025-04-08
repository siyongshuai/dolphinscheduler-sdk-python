# API设计文档

## 目录
- [简介](#简介)
- [API概览](#api概览)
- [认证与授权](#认证与授权)
- [RESTful API规范](#restful-api规范)
- [API端点详细说明](#api端点详细说明)
  - [用户相关](#用户相关)
  - [工作流相关](#工作流相关)
  - [脚本相关](#脚本相关)
  - [执行实例相关](#执行实例相关)
  - [系统相关](#系统相关)
- [响应格式](#响应格式)
- [错误处理](#错误处理)
- [版本控制](#版本控制)
- [限流策略](#限流策略)
- [API文档](#api文档)

## 简介

本文档描述了工作流管理系统的API设计，包括所有可用的API端点、请求/响应格式、认证机制以及错误处理策略。这些API使客户端应用能够与工作流管理系统进行交互，执行工作流的创建、修改、执行和监控等操作。

## API概览

系统API主要分为以下几个模块：

1. **用户管理API**：处理用户注册、登录、权限管理等操作
2. **工作流管理API**：处理工作流的创建、修改、查询、删除等操作
3. **脚本管理API**：处理脚本的上传、修改、查询、删除等操作
4. **执行实例API**：处理工作流执行实例的创建、查询、停止等操作
5. **系统管理API**：处理系统配置、监控、日志等操作

## 认证与授权

### 认证机制

系统使用基于JWT（JSON Web Token）的认证机制：

1. 用户通过登录API获取访问令牌（access token）和刷新令牌（refresh token）
2. 客户端在后续请求中将访问令牌添加到Authorization请求头中
3. 访问令牌有效期为2小时，刷新令牌有效期为30天
4. 当访问令牌过期时，客户端可使用刷新令牌获取新的访问令牌

```
Authorization: Bearer <access_token>
```

### 权限控制

系统采用基于角色的访问控制（RBAC）模型：

1. **管理员（Admin）**：拥有所有操作权限
2. **开发者（Developer）**：可以创建和管理工作流、脚本，执行工作流
3. **操作员（Operator）**：只能执行和监控工作流
4. **访客（Guest）**：只能查看工作流和执行结果

## RESTful API规范

API设计遵循RESTful原则：

1. **资源命名**：使用名词复数形式（如 `/workflows`、`/scripts`）
2. **HTTP方法**：
   - GET：获取资源
   - POST：创建资源
   - PUT：更新资源（全量更新）
   - PATCH：部分更新资源
   - DELETE：删除资源
3. **查询参数**：用于过滤、排序和分页
4. **状态码**：使用标准HTTP状态码表示操作结果

## API端点详细说明

### 用户相关

#### 用户注册
- **端点**：`POST /api/v1/users`
- **请求体**：
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "fullName": "string"
}
```
- **响应**：
```json
{
  "code": 200,
  "message": "用户创建成功",
  "data": {
    "userId": "string",
    "username": "string",
    "email": "string",
    "fullName": "string",
    "role": "string",
    "createdAt": "timestamp"
  }
}
```

#### 用户登录
- **端点**：`POST /api/v1/auth/login`
- **请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```
- **响应**：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "accessToken": "string",
    "refreshToken": "string",
    "expiresIn": 7200,
    "userId": "string",
    "username": "string",
    "role": "string"
  }
}
```

#### 刷新令牌
- **端点**：`POST /api/v1/auth/refresh`
- **请求体**：
```json
{
  "refreshToken": "string"
}
```
- **响应**：
```json
{
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "accessToken": "string",
    "expiresIn": 7200
  }
}
```

#### 获取用户信息
- **端点**：`GET /api/v1/users/{userId}`
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "userId": "string",
    "username": "string",
    "email": "string",
    "fullName": "string",
    "role": "string",
    "createdAt": "timestamp",
    "lastLoginAt": "timestamp"
  }
}
```

### 工作流相关

#### 创建工作流
- **端点**：`POST /api/v1/workflows`
- **请求体**：
```json
{
  "name": "string",
  "description": "string",
  "tags": ["string"],
  "nodes": [
    {
      "id": "string",
      "name": "string",
      "type": "string",
      "config": {
        "scriptId": "string",
        "parameters": {}
      },
      "position": {
        "x": 0,
        "y": 0
      },
      "dependencies": ["string"]
    }
  ],
  "schedule": {
    "enabled": false,
    "cron": "string",
    "startTime": "timestamp",
    "endTime": "timestamp"
  }
}
```
- **响应**：
```json
{
  "code": 200,
  "message": "工作流创建成功",
  "data": {
    "workflowId": "string",
    "name": "string",
    "createdAt": "timestamp"
  }
}
```

#### 获取工作流列表
- **端点**：`GET /api/v1/workflows`
- **查询参数**：
  - `page`: 页码（默认1）
  - `pageSize`: 每页数量（默认10）
  - `name`: 工作流名称（可选，模糊匹配）
  - `tag`: 标签（可选）
  - `status`: 状态（可选）
  - `sortBy`: 排序字段（默认createdAt）
  - `sortOrder`: 排序方向（asc/desc，默认desc）
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 0,
    "pages": 0,
    "current": 0,
    "records": [
      {
        "workflowId": "string",
        "name": "string",
        "description": "string",
        "tags": ["string"],
        "status": "string",
        "createdBy": "string",
        "createdAt": "timestamp",
        "updatedAt": "timestamp",
        "lastRunAt": "timestamp"
      }
    ]
  }
}
```

#### 获取工作流详情
- **端点**：`GET /api/v1/workflows/{workflowId}`
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "workflowId": "string",
    "name": "string",
    "description": "string",
    "tags": ["string"],
    "nodes": [
      {
        "id": "string",
        "name": "string",
        "type": "string",
        "config": {
          "scriptId": "string",
          "parameters": {}
        },
        "position": {
          "x": 0,
          "y": 0
        },
        "dependencies": ["string"]
      }
    ],
    "schedule": {
      "enabled": false,
      "cron": "string",
      "startTime": "timestamp",
      "endTime": "timestamp"
    },
    "status": "string",
    "createdBy": "string",
    "createdAt": "timestamp",
    "updatedAt": "timestamp",
    "lastRunAt": "timestamp"
  }
}
```

#### 更新工作流
- **端点**：`PUT /api/v1/workflows/{workflowId}`
- **请求体**：与创建工作流相同
- **响应**：
```json
{
  "code": 200,
  "message": "工作流更新成功",
  "data": {
    "workflowId": "string",
    "updatedAt": "timestamp"
  }
}
```

#### 删除工作流
- **端点**：`DELETE /api/v1/workflows/{workflowId}`
- **响应**：
```json
{
  "code": 200,
  "message": "工作流删除成功",
  "data": null
}
```

#### 运行工作流
- **端点**：`POST /api/v1/workflows/{workflowId}/run`
- **请求体**：
```json
{
  "parameters": {
    "key1": "value1",
    "key2": "value2"
  },
  "runMode": "ASYNC"
}
```
- **响应**：
```json
{
  "code": 200,
  "message": "工作流运行已提交",
  "data": {
    "instanceId": "string",
    "workflowId": "string",
    "status": "RUNNING",
    "startTime": "timestamp"
  }
}
```

### 脚本相关

#### 上传脚本
- **端点**：`POST /api/v1/scripts`
- **请求体**（multipart/form-data）：
  - `name`: 脚本名称
  - `description`: 脚本描述
  - `type`: 脚本类型（PYTHON/SHELL/SQL等）
  - `tags`: 标签（JSON数组）
  - `file`: 脚本文件
  - `parameters`: 参数定义（JSON格式）
- **响应**：
```json
{
  "code": 200,
  "message": "脚本上传成功",
  "data": {
    "scriptId": "string",
    "name": "string",
    "type": "string",
    "createdAt": "timestamp"
  }
}
```

#### 获取脚本列表
- **端点**：`GET /api/v1/scripts`
- **查询参数**：
  - `page`: 页码（默认1）
  - `pageSize`: 每页数量（默认10）
  - `name`: 脚本名称（可选，模糊匹配）
  - `type`: 脚本类型（可选）
  - `tag`: 标签（可选）
  - `sortBy`: 排序字段（默认createdAt）
  - `sortOrder`: 排序方向（asc/desc，默认desc）
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 0,
    "pages": 0,
    "current": 0,
    "records": [
      {
        "scriptId": "string",
        "name": "string",
        "description": "string",
        "type": "string",
        "tags": ["string"],
        "createdBy": "string",
        "createdAt": "timestamp",
        "updatedAt": "timestamp"
      }
    ]
  }
}
```

#### 获取脚本详情
- **端点**：`GET /api/v1/scripts/{scriptId}`
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "scriptId": "string",
    "name": "string",
    "description": "string",
    "type": "string",
    "content": "string",
    "parameters": [
      {
        "name": "string",
        "type": "string",
        "required": true,
        "defaultValue": "string",
        "description": "string"
      }
    ],
    "tags": ["string"],
    "createdBy": "string",
    "createdAt": "timestamp",
    "updatedAt": "timestamp"
  }
}
```

#### 更新脚本
- **端点**：`PUT /api/v1/scripts/{scriptId}`
- **请求体**（multipart/form-data）：与上传脚本相同
- **响应**：
```json
{
  "code": 200,
  "message": "脚本更新成功",
  "data": {
    "scriptId": "string",
    "updatedAt": "timestamp"
  }
}
```

#### 删除脚本
- **端点**：`DELETE /api/v1/scripts/{scriptId}`
- **响应**：
```json
{
  "code": 200,
  "message": "脚本删除成功",
  "data": null
}
```

### 执行实例相关

#### 获取执行实例列表
- **端点**：`GET /api/v1/instances`
- **查询参数**：
  - `page`: 页码（默认1）
  - `pageSize`: 每页数量（默认10）
  - `workflowId`: 工作流ID（可选）
  - `status`: 状态（可选，可多选，逗号分隔）
  - `startTimeFrom`: 开始时间范围（开始）
  - `startTimeTo`: 开始时间范围（结束）
  - `sortBy`: 排序字段（默认startTime）
  - `sortOrder`: 排序方向（asc/desc，默认desc）
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 0,
    "pages": 0,
    "current": 0,
    "records": [
      {
        "instanceId": "string",
        "workflowId": "string",
        "workflowName": "string",
        "status": "string",
        "startTime": "timestamp",
        "endTime": "timestamp",
        "duration": 0,
        "triggeredBy": "string",
        "triggerType": "string"
      }
    ]
  }
}
```

#### 获取执行实例详情
- **端点**：`GET /api/v1/instances/{instanceId}`
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "instanceId": "string",
    "workflowId": "string",
    "workflowName": "string",
    "status": "string",
    "startTime": "timestamp",
    "endTime": "timestamp",
    "duration": 0,
    "parameters": {},
    "triggeredBy": "string",
    "triggerType": "string",
    "nodes": [
      {
        "nodeId": "string",
        "nodeName": "string",
        "status": "string",
        "startTime": "timestamp",
        "endTime": "timestamp",
        "duration": 0,
        "retries": 0,
        "error": "string"
      }
    ]
  }
}
```

#### 获取节点执行详情
- **端点**：`GET /api/v1/instances/{instanceId}/nodes/{nodeId}`
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "nodeId": "string",
    "instanceId": "string",
    "nodeName": "string",
    "nodeType": "string",
    "status": "string",
    "startTime": "timestamp",
    "endTime": "timestamp",
    "duration": 0,
    "parameters": {},
    "result": {},
    "retries": 0,
    "logs": "string",
    "error": "string"
  }
}
```

#### 停止执行实例
- **端点**：`POST /api/v1/instances/{instanceId}/stop`
- **响应**：
```json
{
  "code": 200,
  "message": "执行实例已停止",
  "data": {
    "instanceId": "string",
    "status": "STOPPED"
  }
}
```

#### 重试执行实例
- **端点**：`POST /api/v1/instances/{instanceId}/retry`
- **请求体**：
```json
{
  "fromNodeId": "string" // 可选，从特定节点开始重试
}
```
- **响应**：
```json
{
  "code": 200,
  "message": "执行实例重试已提交",
  "data": {
    "instanceId": "string",
    "status": "RUNNING"
  }
}
```

### 系统相关

#### 获取系统状态
- **端点**：`GET /api/v1/system/status`
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "version": "string",
    "uptime": 0,
    "workflowCount": 0,
    "runningInstanceCount": 0,
    "queuedInstanceCount": 0,
    "systemLoad": {
      "cpu": 0,
      "memory": 0,
      "disk": 0
    }
  }
}
```

#### 获取系统配置
- **端点**：`GET /api/v1/system/config`
- **响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "maxConcurrentInstances": 0,
    "defaultExecutionTimeout": 0,
    "allowedScriptTypes": ["string"],
    "logRetentionDays": 0
  }
}
```

## 响应格式

所有API响应采用统一的JSON格式：

```json
{
  "code": 0,      // 状态码，200表示成功，其他表示错误
  "message": "",  // 响应消息，成功或错误描述
  "data": {}      // 响应数据，可能是对象、数组或null
}
```

## 错误处理

### 错误响应格式

```json
{
  "code": 0,      // 错误状态码
  "message": "",  // 错误消息
  "data": null,   // 通常为null
  "errors": [     // 详细错误信息（可选）
    {
      "field": "string",  // 出错的字段
      "message": "string" // 针对该字段的错误消息
    }
  ]
}
```

### 常见状态码

- **200** - 成功
- **400** - 请求无效（客户端错误）
- **401** - 未授权（缺少或无效的认证凭据）
- **403** - 禁止访问（权限不足）
- **404** - 资源不存在
- **409** - 冲突（例如资源已存在）
- **422** - 请求实体无法处理（例如验证失败）
- **429** - 请求过多（限流）
- **500** - 服务器内部错误

## 版本控制

API版本通过URL路径前缀控制：

- `/api/v1/` - 当前稳定版本
- `/api/v2/` - 新版本（当有重大变更时）

## 限流策略

为防止API滥用，系统实施了限流策略：

- 基本限制：每个IP每分钟最多100个请求
- 认证用户：根据用户角色，每分钟允许的请求数不同
  - 管理员：500请求/分钟
  - 开发者：300请求/分钟
  - 操作员：200请求/分钟
  - 访客：100请求/分钟

当超过限制时，API将返回429状态码，并在响应头中包含以下信息：

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1620000000
```

## API文档

完整的API文档通过Swagger UI提供，可在以下地址访问：

```
https://{base_url}/swagger-ui/index.html
```

开发环境中的API文档地址：

```
http://localhost:8080/swagger-ui/index.html
``` 