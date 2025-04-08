# 基于YAML配置的批量工作流创建工具

本目录包含基于YAML配置的批量工作流创建工具，可用于PyDolphinScheduler项目中批量生成工作流。每个工作流包含一个依赖(dependent)节点和一个shell节点，shell节点的内容会被提取并存储到publish_center目录中。

## 目录文件说明

- **batch_create_workflows.py** - 批量创建工作流的Python脚本
- **workflow_template.yaml** - 工作流模板文件，定义工作流结构
- **workflow_configs.yaml** - 工作流配置文件，包含多个工作流的参数
- **yaml_batch_workflow.md** - 详细的方案说明文档

## 使用方法

1. 确保已安装PyDolphinScheduler
2. 修改workflow_configs.yaml添加需要的工作流配置
3. 运行批量创建脚本：

```bash
python batch_create_workflows.py
```

## 执行结果

- 创建publish_center目录存放shell脚本
- 创建workflow_yamls目录存放生成的工作流配置
- 在DolphinScheduler中创建工作流实例

## 适用场景

- 需要为多个业务区域/分支创建结构相同的工作流
- 工作流结构稳定，但shell命令内容各不相同
- 需要集中管理shell脚本内容 