# 提示词记录

## 2025-04-09
- 以yaml配置为基础，结合批量创建的方式，每个工作流都有一个dependent节点和一个shell节点，shell节点中的内容是模板化的，实现编码，编码内容放入publish_center
- 创建目录simple_publish_center，将生成的四个文件移入其中
- 为simple_publish_center子项目建立独立的元文件 