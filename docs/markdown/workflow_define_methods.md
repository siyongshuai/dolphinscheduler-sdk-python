# PyDolphinScheduler定义工作流的方法

PyDolphinScheduler提供了多种方式来定义工作流，满足不同用户的使用习惯和场景需求。以下是主要的几种定义工作流的方法：

## 1. 使用上下文管理器(with语句)

这是最常用、最直观的方式，通过Python的上下文管理器(with语句)来定义工作流和任务。

```python
from pydolphinscheduler.core.workflow import Workflow
from pydolphinscheduler.tasks.shell import Shell

with Workflow(name="workflow_name", schedule="0 0 0 * * ? *") as workflow:
    task_1 = Shell(name="task_1", command="echo hello")
    task_2 = Shell(name="task_2", command="echo world")
    
    # 定义任务依赖关系
    task_1 >> task_2
    
    # 提交或运行工作流
    workflow.run()  # 或 workflow.submit()
```

此方法利用Python的`with`语句上下文管理器，使得代码结构清晰，任务之间的关系直观可见。当`with`块退出时，会自动清理工作流上下文。

## 2. 使用装饰器方式(@task)

通过`@task`装饰器，可以将普通Python函数转化为工作流任务，尤其适合Python开发者。

```python
from pydolphinscheduler.core.workflow import Workflow
from pydolphinscheduler.tasks.func_wrap import task

@task
def task_1():
    print("This is task 1")

@task
def task_2():
    print("This is task 2")

with Workflow(name="workflow_with_decorator") as workflow:
    t1 = task_1()
    t2 = task_2()
    
    t1 >> t2
    
    workflow.submit()
```

这种方式允许开发者利用普通的Python函数定义任务，装饰器会自动将函数转换为PyDolphinScheduler任务。

## 3. YAML配置文件定义

使用YAML配置文件可以无需编写Python代码，直接通过配置文件定义工作流，适合非开发人员或希望配置与代码分离的场景。

```yaml
# example.yaml
workflow:
  name: "workflow_from_yaml"
  
tasks:
  - name: task_1
    task_type: Shell
    command: echo "Hello from task 1"
    
  - name: task_2
    task_type: Shell
    command: echo "Hello from task 2"
    deps: [task_1]  # 依赖task_1
```

可以通过以下方式加载和创建工作流：

```python
from pydolphinscheduler.core.yaml_workflow import YamlWorkflow

# 方式1
YamlWorkflow("example.yaml").create_workflow()

# 方式2 
parser = YamlWorkflow("example.yaml")
parser.create_workflow()
```

## 4. 批量创建工作流

对于需要批量生成相似工作流的场景，可以使用循环方式批量创建：

```python
from pydolphinscheduler.core.workflow import Workflow
from pydolphinscheduler.tasks.shell import Shell

# 创建10个工作流
for wf_num in range(10):
    workflow_name = f"workflow_{wf_num}"
    
    with Workflow(name=workflow_name) as workflow:
        # 每个工作流创建5个任务
        for task_num in range(5):
            task_name = f"task_{task_num}_{workflow_name}"
            command = f"echo This is {task_name}"
            task = Shell(name=task_name, command=command)
            
            # 建立任务依赖
            if task_num > 0:
                pre_task_name = f"task_{task_num-1}_{workflow_name}"
                workflow.get_one_task_by_name(pre_task_name) >> task
        
        workflow.submit()
```

这种方式适合需要生成大量相似结构工作流的场景，如数据处理管道的复制或测试环境的搭建。

## 5. 子工作流方式

通过子工作流方式，可以将一个工作流嵌入到另一个工作流中，实现工作流的模块化和复用：

```python
from pydolphinscheduler.core.workflow import Workflow
from pydolphinscheduler.tasks.shell import Shell
from pydolphinscheduler.tasks.sub_workflow import SubWorkflow

# 先定义一个子工作流
with Workflow(name="sub_workflow") as sub_wf:
    task_a = Shell(name="task_a", command="echo task A")
    task_b = Shell(name="task_b", command="echo task B")
    task_a >> task_b
    sub_wf.submit()

# 在主工作流中使用子工作流
with Workflow(name="main_workflow") as main_wf:
    task_1 = Shell(name="task_1", command="echo task 1")
    sub_wf_task = SubWorkflow(name="sub_workflow_task", workflow_name="sub_workflow")
    task_2 = Shell(name="task_2", command="echo task 2")
    
    task_1 >> sub_wf_task >> task_2
    
    main_wf.submit()
```

这种方式允许将复杂的工作流拆分为小型、可管理的部分，有助于工作流的维护和复用。

## 总结

PyDolphinScheduler提供了多种定义工作流的方式，用户可以根据自己的需求和偏好选择合适的方式：

1. **上下文管理器(with语句)**：最直观和常用的方式
2. **装饰器方式(@task)**：适合Python开发者，可以将普通函数转为任务
3. **YAML配置文件**：适合非开发人员或配置与代码分离的场景
4. **批量创建**：适合需要创建大量相似工作流的场景
5. **子工作流**：适合模块化和复用工作流的场景

不同的定义方式可以相互结合使用，以满足复杂的工作流场景需求。 