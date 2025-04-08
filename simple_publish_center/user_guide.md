# 用户指南

本文档提供了simple_publish_center工具的详细使用说明，帮助用户快速上手和使用。

## 概述

simple_publish_center是一个批量创建工作流的工具，基于YAML配置文件和模板，能够高效地创建多个结构相似但内容不同的工作流。每个工作流包含一个依赖(dependent)节点和一个shell节点，shell节点的命令内容会被提取并存储到publish_center目录中集中管理。

## 安装与配置

### 前置要求

- Python 3.9或更高版本
- 安装了PyDolphinScheduler库
- 运行中的DolphinScheduler服务器

### 安装步骤

1. 下载或克隆项目到本地
2. 安装依赖:

```bash
pip install apache-dolphinscheduler pyyaml
```

## 使用方法

### 基本用法

1. 查看和修改配置文件`workflow_configs.yaml`，添加你需要的工作流配置
2. 运行批量创建脚本:

```bash
python batch_create_workflows.py
```

3. 查看脚本输出日志，确认工作流创建成功
4. 在DolphinScheduler UI中查看创建的工作流

### 配置文件说明

配置文件`workflow_configs.yaml`包含多个工作流的配置信息，示例如下:

```yaml
workflows:
  - workflow_name: "data_process_region_a"  # 工作流名称
    workflow_description: "区域A数据处理工作流"  # 工作流描述
    task_id: "001"  # 任务ID
    dependent_project: "base_project"  # 依赖的项目
    dependent_workflow: "data_collect"  # 依赖的工作流
    dependent_task: "collect_complete"  # 依赖的任务
    shell_command: |  # Shell命令内容
      #!/bin/bash
      echo "开始处理区域A数据"
      date
      # 区域A特定处理逻辑
      echo "区域A数据处理完成"
```

### 配置参数说明

| 参数名 | 描述 | 是否必填 | 示例值 |
|-------|------|---------|-------|
| workflow_name | 工作流名称 | 是 | "data_process_region_a" |
| workflow_description | 工作流描述 | 否 | "区域A数据处理工作流" |
| task_id | 任务ID | 是 | "001" |
| dependent_project | 依赖的项目名称 | 是 | "base_project" |
| dependent_workflow | 依赖的工作流名称 | 是 | "data_collect" |
| dependent_task | 依赖的任务名称 | 是 | "collect_complete" |
| shell_command | Shell命令内容 | 是 | 详见示例 |

## 工作流模板说明

工作流模板文件`workflow_template.yaml`定义了工作流的基本结构:

```yaml
workflow:
  name: "${workflow_name}"
  description: "${workflow_description}"
  release_state: "online"
  
tasks:
  - name: "dependent_${task_id}"
    task_type: Dependent
    dependent_parameters:
      - project_name: "${dependent_project}"
        workflow_name: "${dependent_workflow}"
        dependent_mode: "task_dependent"
        dependent_task_name: "${dependent_task}"
        dependent_result: "success"
        
  - name: "shell_${task_id}"
    task_type: Shell
    deps: ["dependent_${task_id}"]
    command: "${shell_command}"
```

## 输出文件说明

执行脚本后，将生成以下输出:

1. **publish_center目录**：存放提取的shell脚本
   - 命名格式: `{workflow_name}_{task_id}.sh`
   - 例如: `data_process_region_a_001.sh`

2. **workflow_yamls目录**：存放生成的工作流YAML配置
   - 命名格式: `{workflow_name}.yaml`
   - 例如: `data_process_region_a.yaml`

## 高级用法

### 自定义配置文件路径

```bash
python batch_create_workflows.py --config path/to/your/config.yaml
```

### 仅生成配置不创建工作流

```bash
python batch_create_workflows.py --dry-run
```

### 添加更多工作流

编辑`workflow_configs.yaml`文件，在`workflows`列表中添加新的工作流配置。

## 故障排除

### 常见错误

1. **找不到配置文件**
   - 确保工作目录中存在`workflow_configs.yaml`文件
   - 检查文件权限

2. **工作流创建失败**
   - 检查DolphinScheduler服务是否正常运行
   - 检查配置中的项目、工作流和任务名称是否正确
   - 查看日志输出获取详细错误信息

3. **Shell脚本内容问题**
   - 确保shell脚本内容语法正确
   - 避免使用特殊字符导致YAML解析错误

## 最佳实践

1. **命名规范**
   - 工作流名称使用有意义的命名，表明其功能和范围
   - 使用一致的命名约定，如区域前缀或功能前缀

2. **脚本管理**
   - 将复杂的shell脚本逻辑移到单独的脚本文件
   - 在shell_command中调用这些脚本，而不是嵌入大量代码

3. **依赖管理**
   - 确保依赖的项目、工作流和任务已存在
   - 建立清晰的依赖关系链，避免循环依赖

4. **版本控制**
   - 将配置文件和模板文件纳入版本控制
   - 记录配置变更历史
   - 为不同环境维护不同的配置文件 