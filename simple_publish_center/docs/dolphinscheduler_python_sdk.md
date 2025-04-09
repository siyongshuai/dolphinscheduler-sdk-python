# DolphinScheduler Python SDK 功能概述

## 简介

Apache DolphinScheduler Python SDK (pydolphinscheduler) 是 Apache DolphinScheduler 的 Python API，允许用户通过 Python 代码定义工作流，实现"工作流即代码"(workflow-as-code)的开发模式。

## 核心功能

### 1. 工作流定义

通过 Python 类定义工作流，包括：
- 工作流基本属性（名称、描述、调度策略等）
- 任务定义与依赖关系
- 资源引用
- 参数传递

### 2. 任务类型支持

SDK 支持多种任务类型，包括但不限于：
- Shell
- Python
- SQL
- Spark
- Flink
- DataX
- Http
- Dependent（依赖任务）
- Switch（条件分支）
- SubProcess（子流程）
- SubWorkflow（子工作流）
- MapReduce
- 机器学习相关（PyTorch、MLflow、SageMaker等）

### 3. 工作流控制

支持工作流的各种控制功能：
- 创建和提交工作流
- 运行工作流
- 工作流调度设置
- 超时控制
- 失败策略
- 并行/串行执行控制

### 4. YAML 工作流支持

除了直接使用 Python API，还支持通过 YAML 文件定义工作流：
- 使用 `YamlWorkflow` 类加载和创建 YAML 工作流
- 支持模板变量替换，便于批量创建工作流

### 5. 资源管理

支持资源文件管理：
- 上传和引用资源文件
- 资源插件支持

### 6. 批量操作

支持批量创建工作流：
- 基于模板批量创建
- 通过配置文件管理多个工作流

## 使用示例

### 基本工作流创建

```python
from pydolphinscheduler.core.workflow import Workflow
from pydolphinscheduler.tasks.shell import Shell

with Workflow(name="simple_workflow") as workflow:
    task = Shell(name="shell_task", command="echo hello world")
    workflow.submit()
```

### 任务依赖关系

```python
# 设置任务依赖关系的方法
task_parent = Shell(name="parent", command="echo parent")
task_child = Shell(name="child", command="echo child")

# 方法一：使用 set_downstream
task_parent.set_downstream(task_child)

# 方法二：使用运算符
task_parent >> task_child

# 多任务依赖
task_group = [task_child1, task_child2]
task_parent >> task_group
```

### 使用YAML创建工作流

```python
from pydolphinscheduler.core.yaml_workflow import YamlWorkflow

# 加载YAML文件创建工作流
YamlWorkflow("workflow.yaml").create_workflow()
```

## 环境要求

- Python 3.6+（Windows环境下不支持Python 3.10+）
- 需要连接到已运行的DolphinScheduler服务

## 配置

主要配置项包括：
- Java Gateway配置（连接到DolphinScheduler服务）
- 默认用户和项目设置
- 任务执行相关配置
- 资源目录配置

## 后续开发方向

- 增强批量工作流管理功能
- 完善与其他系统的集成能力
- 提供更丰富的监控和管理API 