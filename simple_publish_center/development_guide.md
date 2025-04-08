# 开发指南

本文档提供了对simple_publish_center项目进行开发和扩展的指导。

## 环境设置

### 前置条件

1. Python 3.9或更高版本
2. 已安装PyDolphinScheduler
3. 运行中的DolphinScheduler服务器

### 开发环境搭建

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 安装依赖
pip install apache-dolphinscheduler pyyaml
```

## 代码结构

```
simple_publish_center/
├── batch_create_workflows.py  # 核心处理脚本
├── workflow_template.yaml     # 工作流模板
├── workflow_configs.yaml      # 工作流配置
├── README.md                  # 使用说明
└── ...                        # 其他文档
```

## 核心模块解析

### 1. 配置解析模块

负责读取YAML配置文件，将配置信息转换为Python对象。

关键函数:
- `main()`: 读取配置文件并启动处理
- `batch_create_workflows()`: 批量处理工作流配置

### 2. 模板渲染模块

负责使用配置数据渲染工作流模板。

关键函数:
- `render_template()`: 使用string.Template渲染模板
- `generate_workflow_yaml()`: 生成工作流YAML文件

### 3. 脚本管理模块

负责提取和保存shell脚本。

关键函数:
- `save_shell_script()`: 将shell命令保存为脚本文件

### 4. 工作流创建模块

使用PyDolphinScheduler API创建工作流实例。

关键代码:
```python
YamlWorkflow(yaml_path).create_workflow()
```

## 扩展指南

### 添加新的节点类型

1. 修改`workflow_template.yaml`添加新节点定义:

```yaml
- name: "new_node_${task_id}"
  task_type: NewNodeType
  deps: ["dependent_${task_id}"]
  custom_parameter: "${custom_value}"
```

2. 在`workflow_configs.yaml`中添加对应参数:

```yaml
- workflow_name: "example_workflow"
  # ... 其他参数
  custom_value: "示例值"
```

### 支持复杂依赖关系

修改脚本中的`batch_create_workflows`函数，添加对复杂依赖关系的处理逻辑。

### 添加脚本检查功能

在`save_shell_script`函数中添加脚本检查逻辑:

```python
def validate_shell_script(content):
    # 添加检查逻辑
    if "rm -rf /" in content:
        raise ValueError("危险命令: rm -rf /")
    return True

# 在save_shell_script中调用
validate_shell_script(script_content)
```

## 测试指南

### 单元测试

创建`tests`目录，添加单元测试:

```python
# test_batch_create.py
import unittest
from batch_create_workflows import render_template

class TestBatchCreate(unittest.TestCase):
    def test_render_template(self):
        template = "Hello ${name}"
        params = {"name": "World"}
        result = render_template(template, params)
        self.assertEqual(result, "Hello World")
```

### 集成测试

创建测试配置，运行完整流程并验证结果:

```bash
# 创建测试配置
cp workflow_configs.yaml workflow_configs_test.yaml
# 修改测试配置...

# 运行测试
python batch_create_workflows.py --config workflow_configs_test.yaml
```

## 编码规范

1. 遵循PEP 8编码规范
2. 使用类型注解增强代码可读性
3. 编写清晰的函数文档字符串
4. 使用有意义的变量名和函数名
5. 添加适当的日志信息

## 贡献流程

1. Fork项目仓库
2. 创建特性分支
3. 提交更改并添加测试
4. 确保所有测试通过
5. 提交Pull Request

## 发布流程

1. 更新版本号
2. 更新changelog.md
3. 创建新的release标签
4. 发布release说明 