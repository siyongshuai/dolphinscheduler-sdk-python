# 基于YAML配置的批量工作流创建方案

## 方案概述

本方案结合YAML配置文件与批量创建方式的优点，实现模板化工作流创建。每个工作流包含：
- 一个依赖(dependent)节点
- 一个模板化的shell节点
- shell节点内容放入publish_center

## 实现步骤

1. 创建YAML模板文件
2. 开发Python批量生成脚本
3. 创建模板渲染工具函数
4. 实现工作流生成与发布逻辑

## 代码实现

### 1. 基础YAML模板文件

首先创建一个工作流模板文件 `workflow_template.yaml`：

```yaml
# 工作流模板 - 将被批量替换参数生成多个工作流
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

### 2. 批量生成脚本

创建Python脚本 `batch_create_workflows.py` 实现批量工作流生成：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于YAML模板批量创建工作流，并将Shell节点内容发布到publish_center
"""

import os
import yaml
import string
from pathlib import Path
import logging
from typing import Dict, List, Any

from pydolphinscheduler.core.yaml_workflow import YamlWorkflow

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 发布中心目录
PUBLISH_CENTER = "publish_center"

def ensure_dir_exists(directory: str) -> None:
    """确保目录存在，不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"创建目录: {directory}")

def render_template(template: str, params: Dict[str, Any]) -> str:
    """渲染包含变量的字符串模板"""
    return string.Template(template).safe_substitute(params)

def generate_workflow_yaml(template_path: str, output_path: str, params: Dict[str, Any]) -> str:
    """根据模板和参数生成工作流YAML文件"""
    # 读取模板文件
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 渲染模板
    rendered_content = render_template(template_content, params)
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    
    logger.info(f"生成工作流配置: {output_path}")
    return output_path

def save_shell_script(script_content: str, workflow_name: str, task_id: str) -> str:
    """保存Shell脚本到发布中心"""
    # 确保发布中心目录存在
    ensure_dir_exists(PUBLISH_CENTER)
    
    # 创建脚本文件路径
    script_filename = f"{workflow_name}_{task_id}.sh"
    script_path = os.path.join(PUBLISH_CENTER, script_filename)
    
    # 写入脚本内容
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    logger.info(f"保存Shell脚本: {script_path}")
    return script_path

def batch_create_workflows(workflow_configs: List[Dict[str, Any]], template_path: str) -> None:
    """批量创建工作流"""
    # 创建输出目录
    output_dir = "workflow_yamls"
    ensure_dir_exists(output_dir)
    
    for config in workflow_configs:
        # 提取并处理shell命令
        shell_command = config.get("shell_command", "echo 'Default command'")
        workflow_name = config.get("workflow_name", "default_workflow")
        task_id = config.get("task_id", "001")
        
        # 将shell命令保存到发布中心
        script_path = save_shell_script(shell_command, workflow_name, task_id)
        
        # 更新配置中的shell命令为引用脚本文件
        config["shell_command"] = f"sh {script_path}"
        
        # 生成工作流YAML文件
        output_path = os.path.join(output_dir, f"{workflow_name}.yaml")
        yaml_path = generate_workflow_yaml(template_path, output_path, config)
        
        # 创建工作流
        try:
            YamlWorkflow(yaml_path).create_workflow()
            logger.info(f"成功创建工作流: {workflow_name}")
        except Exception as e:
            logger.error(f"创建工作流失败 {workflow_name}: {str(e)}")

def main():
    """主函数"""
    # 示例工作流配置
    workflow_configs = [
        {
            "workflow_name": "data_process_region_a",
            "workflow_description": "区域A数据处理工作流",
            "task_id": "001",
            "dependent_project": "base_project",
            "dependent_workflow": "data_collect",
            "dependent_task": "collect_complete",
            "shell_command": """#!/bin/bash
echo "开始处理区域A数据"
date
# 区域A特定处理逻辑
echo "区域A数据处理完成"
"""
        },
        {
            "workflow_name": "data_process_region_b",
            "workflow_description": "区域B数据处理工作流",
            "task_id": "001",
            "dependent_project": "base_project",
            "dependent_workflow": "data_collect",
            "dependent_task": "collect_complete",
            "shell_command": """#!/bin/bash
echo "开始处理区域B数据"
date
# 区域B特定处理逻辑
echo "区域B数据处理完成"
"""
        },
        # 可以添加更多工作流配置...
    ]
    
    template_path = "workflow_template.yaml"
    batch_create_workflows(workflow_configs, template_path)

if __name__ == "__main__":
    main()
```

### 3. 扩展：配置文件驱动

为提高灵活性，我们可以通过外部配置文件驱动批量创建过程，创建 `workflow_configs.yaml`：

```yaml
# 工作流配置列表
workflows:
  - workflow_name: "data_process_region_a"
    workflow_description: "区域A数据处理工作流"
    task_id: "001"
    dependent_project: "base_project"
    dependent_workflow: "data_collect"
    dependent_task: "collect_complete"
    shell_command: |
      #!/bin/bash
      echo "开始处理区域A数据"
      date
      # 区域A特定处理逻辑
      echo "区域A数据处理完成"
  
  - workflow_name: "data_process_region_b"
    workflow_description: "区域B数据处理工作流"
    task_id: "001"
    dependent_project: "base_project"
    dependent_workflow: "data_collect"
    dependent_task: "collect_complete"
    shell_command: |
      #!/bin/bash
      echo "开始处理区域B数据"
      date
      # 区域B特定处理逻辑
      echo "区域B数据处理完成"

  # 可以添加更多工作流配置...
```

然后修改批量创建脚本以使用配置文件：

```python
def main():
    """主函数"""
    # 从配置文件加载工作流配置
    config_path = "workflow_configs.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    workflow_configs = config_data.get("workflows", [])
    template_path = "workflow_template.yaml"
    batch_create_workflows(workflow_configs, template_path)
```

## 使用方法

1. 准备YAML模板文件 `workflow_template.yaml`
2. 创建工作流配置文件 `workflow_configs.yaml`
3. 运行批量创建脚本：
```bash
python batch_create_workflows.py
```

## 优势分析

1. **配置与代码分离**：工作流结构在YAML模板定义，配置参数在单独文件
2. **批量高效创建**：一次性创建多个相似结构的工作流
3. **脚本集中管理**：所有Shell脚本内容存储在publish_center目录
4. **易于维护**：模板化设计使得修改工作流结构只需更新模板
5. **可扩展性**：可以轻松添加更多工作流配置

## 示例运行结果

执行批量创建脚本后，将创建以下文件：

1. **工作流YAML配置文件**：
   - `workflow_yamls/data_process_region_a.yaml`
   - `workflow_yamls/data_process_region_b.yaml`
   - ...

2. **Shell脚本文件**：
   - `publish_center/data_process_region_a_001.sh`
   - `publish_center/data_process_region_b_001.sh`
   - ...

3. **在DolphinScheduler中创建工作流**：
   - `data_process_region_a`（包含dependent_001和shell_001节点）
   - `data_process_region_b`（包含dependent_001和shell_001节点）
   - ...

## 实际应用场景

本方案特别适合以下场景：
- 需要为多个业务区域或分支创建结构相同的数据处理工作流
- 工作流的基本结构稳定，但Shell命令内容各不相同
- 需要集中管理和版本控制Shell脚本内容
- 运维人员希望通过配置文件方式管理工作流 