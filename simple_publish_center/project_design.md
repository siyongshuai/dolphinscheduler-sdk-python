# 模板化工作流批量创建项目设计

## 项目概述

simple_publish_center是一个基于YAML配置的工作流批量创建工具，旨在解决大规模相似工作流创建和shell脚本统一管理的问题。项目利用PyDolphinScheduler提供的YAML配置功能和Python API，实现工作流的模板化定义和批量创建。

## 设计目标

1. **模板化定义**：通过统一模板定义工作流结构，便于维护
2. **配置驱动**：通过配置文件定义多个工作流，无需编写代码
3. **脚本集中化**：将shell脚本内容集中存储，便于版本控制和审计
4. **批量处理**：高效创建大量相似结构的工作流

## 系统架构

### 组件关系

```
workflow_template.yaml <-- batch_create_workflows.py --> workflow_configs.yaml
                             |
                             v
                       publish_center/
                             |
                             v
                       workflow_yamls/
                             |
                             v
                     DolphinScheduler API
```

### 核心流程

1. 读取工作流模板文件和配置文件
2. 解析工作流配置，提取shell命令
3. 将shell命令保存到publish_center目录
4. 生成工作流YAML配置文件
5. 调用PyDolphinScheduler API创建工作流实例

## 文件结构

- **batch_create_workflows.py**: 核心处理脚本
- **workflow_template.yaml**: 工作流模板文件
- **workflow_configs.yaml**: 工作流配置文件
- **yaml_batch_workflow.md**: 详细说明文档
- **README.md**: 使用说明文件
- **元文件**: 
  - prop_process.md: 提示词记录
  - changelog.md: 变更日志
  - issue.md: 问题记录
  - bugfix.md: Bug修复记录
  - project_design.md: 项目设计文档

## 数据流向

1. 配置数据流: workflow_configs.yaml -> batch_create_workflows.py
2. 模板数据流: workflow_template.yaml -> batch_create_workflows.py
3. 脚本输出流: batch_create_workflows.py -> publish_center/*.sh
4. 工作流输出流: batch_create_workflows.py -> workflow_yamls/*.yaml
5. API调用流: batch_create_workflows.py -> PyDolphinScheduler API

## 设计决策

### 为什么选择YAML配置方式?
- 降低使用门槛，非开发人员也能创建工作流
- 配置与代码分离，便于版本控制和审计
- 适合运维和自动化场景

### 为什么需要集中存储shell脚本?
- 便于统一管理和版本控制
- 提高安全性，可以集中审计敏感操作
- 减少重复代码，提高维护效率

### 为什么使用模板化方式?
- 确保所有工作流结构一致
- 降低创建工作流的复杂度
- 便于统一修改所有工作流结构

## 扩展计划

1. 支持多种节点类型和复杂依赖关系
2. 添加工作流更新和删除功能
3. 实现版本控制和回滚机制
4. 添加脚本内容检查和安全审计功能
5. 开发Web界面进行可视化管理

## 部署建议

- 建议将本工具集成到CI/CD流程中
- 推荐使用Git管理配置文件和脚本
- 建议为不同环境(开发/测试/生产)创建不同的配置文件 