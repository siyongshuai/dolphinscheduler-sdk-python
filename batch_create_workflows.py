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
    # 从配置文件加载工作流配置
    config_path = "workflow_configs.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        workflow_configs = config_data.get("workflows", [])
        
        if not workflow_configs:
            logger.warning(f"配置文件 {config_path} 中未找到工作流配置")
            return
        
        template_path = "workflow_template.yaml"
        if not os.path.exists(template_path):
            logger.error(f"工作流模板文件 {template_path} 不存在")
            return
        
        logger.info(f"开始批量创建工作流，共 {len(workflow_configs)} 个工作流")
        batch_create_workflows(workflow_configs, template_path)
        logger.info("批量创建工作流完成")
        
    except FileNotFoundError:
        logger.error(f"找不到配置文件: {config_path}")
    except yaml.YAMLError as e:
        logger.error(f"解析YAML配置文件出错: {str(e)}")
    except Exception as e:
        logger.error(f"创建工作流过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 