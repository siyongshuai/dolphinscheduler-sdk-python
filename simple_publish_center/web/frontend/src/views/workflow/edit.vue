<template>
  <div class="workflow-edit-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑工作流' : '创建工作流' }}</span>
          <div>
            <el-button type="primary" @click="handleSave">保存</el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>

      <el-form ref="formRef" :model="workflowForm" :rules="rules" label-width="120px">
        <el-form-item label="工作流名称" prop="name">
          <el-input v-model="workflowForm.name" placeholder="请输入工作流名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="workflowForm.description" type="textarea" placeholder="请输入工作流描述" />
        </el-form-item>
        
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="workflowForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或添加标签"
          >
            <el-option
              v-for="tag in tagOptions"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <div class="workflow-editor">
        <div class="editor-toolbar">
          <el-button-group>
            <el-button size="small" @click="handleAddNode">添加节点</el-button>
            <el-button size="small" @click="handleAddEdge">添加连线</el-button>
            <el-button size="small" @click="handleDelete">删除</el-button>
          </el-button-group>
        </div>
        
        <div class="editor-container" ref="graphContainer"></div>
      </div>
      
      <div class="node-config" v-if="currentNode">
        <h3>节点配置</h3>
        <el-form label-width="100px">
          <el-form-item label="节点名称">
            <el-input v-model="currentNode.data.name" @change="updateNodeName" />
          </el-form-item>
          
          <el-form-item label="节点类型">
            <el-select v-model="currentNode.data.type" @change="updateNodeType">
              <el-option label="Shell脚本" value="shell" />
              <el-option label="Python脚本" value="python" />
              <el-option label="条件判断" value="condition" />
              <el-option label="并行任务" value="parallel" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="脚本内容" v-if="currentNode.data.type === 'shell' || currentNode.data.type === 'python'">
            <div class="code-editor" ref="codeEditor"></div>
          </el-form-item>
          
          <el-form-item label="条件表达式" v-if="currentNode.data.type === 'condition'">
            <el-input v-model="currentNode.data.condition" placeholder="例如: ${status} == 'success'" />
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Graph } from '@antv/x6'
import * as monaco from 'monaco-editor'
import { createWorkflow, updateWorkflow, getWorkflowById } from '@/api/workflow'

export default defineComponent({
  name: 'WorkflowEdit',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    
    const workflowId = computed(() => route.params.id)
    const isEdit = computed(() => !!workflowId.value)
    
    const formRef = ref(null)
    const graphContainer = ref(null)
    const codeEditor = ref(null)
    
    const graph = ref(null)
    const editor = ref(null)
    const currentNode = ref(null)
    
    // 工作流表单
    const workflowForm = reactive({
      name: '',
      description: '',
      tags: [],
      definition: JSON.stringify({
        nodes: [],
        edges: []
      })
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入工作流名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      description: [
        { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
      ]
    }
    
    // 标签选项
    const tagOptions = ref(['开发', '测试', '生产', '数据处理', '周期任务'])
    
    onMounted(async () => {
      initGraph()
      
      if (isEdit.value) {
        await loadWorkflow()
      }
    })
    
    // 初始化图形编辑器
    const initGraph = () => {
      graph.value = new Graph({
        container: graphContainer.value,
        grid: true,
        mousewheel: {
          enabled: true,
          zoomAtMousePosition: true,
          modifiers: 'ctrl'
        },
        connecting: {
          snap: true,
          allowBlank: false,
          allowLoop: false,
          router: {
            name: 'manhattan'
          },
          connector: {
            name: 'rounded'
          }
        }
      })
      
      // 添加节点选中事件
      graph.value.on('node:click', ({ node }) => {
        currentNode.value = node
        
        // 初始化代码编辑器
        if ((node.data.type === 'shell' || node.data.type === 'python') && codeEditor.value) {
          nextTick(() => {
            if (editor.value) {
              editor.value.dispose()
            }
            
            editor.value = monaco.editor.create(codeEditor.value, {
              value: node.data.script || '',
              language: node.data.type === 'shell' ? 'shell' : 'python',
              minimap: { enabled: false },
              theme: 'vs-dark',
              automaticLayout: true,
              scrollBeyondLastLine: false,
              lineNumbers: 'on',
              glyphMargin: false,
              folding: true,
              lineDecorationsWidth: 10,
              lineNumbersMinChars: 3
            })
            
            editor.value.onDidChangeModelContent(() => {
              node.data.script = editor.value.getValue()
            })
          })
        }
      })
    }
    
    // 加载工作流数据
    const loadWorkflow = async () => {
      try {
        const response = await getWorkflowById(workflowId.value)
        const workflow = response.data
        
        // 填充表单
        workflowForm.name = workflow.name
        workflowForm.description = workflow.description
        workflowForm.tags = workflow.tags || []
        
        // 加载工作流图形
        if (workflow.definition) {
          let definition
          try {
            definition = typeof workflow.definition === 'string' 
              ? JSON.parse(workflow.definition) 
              : workflow.definition
          } catch (e) {
            definition = { nodes: [], edges: [] }
          }
          
          // 加载节点和边
          if (definition.nodes && definition.edges) {
            graph.value.fromJSON(definition)
          }
        }
      } catch (error) {
        ElMessage.error('加载工作流失败')
      }
    }
    
    // 添加节点
    const handleAddNode = () => {
      const node = graph.value.addNode({
        shape: 'rect',
        width: 120,
        height: 60,
        attrs: {
          body: {
            fill: '#f5f5f5',
            stroke: '#d9d9d9',
            strokeWidth: 1,
            rx: 4,
            ry: 4
          },
          label: {
            text: '新节点',
            fill: '#333',
            fontSize: 14
          }
        },
        position: {
          x: 100,
          y: 100
        },
        data: {
          name: '新节点',
          type: 'shell',
          script: ''
        }
      })
      
      currentNode.value = node
    }
    
    // 添加连线
    const handleAddEdge = () => {
      ElMessage.info('请在节点之间拖拽创建连线')
    }
    
    // 删除选中元素
    const handleDelete = () => {
      const cells = graph.value.getSelectedCells()
      if (cells.length === 0) {
        ElMessage.warning('请先选择要删除的元素')
        return
      }
      
      graph.value.removeCells(cells)
      if (currentNode.value && cells.includes(currentNode.value)) {
        currentNode.value = null
      }
    }
    
    // 更新节点名称
    const updateNodeName = () => {
      if (!currentNode.value) return
      
      currentNode.value.attr('label/text', currentNode.value.data.name)
    }
    
    // 更新节点类型
    const updateNodeType = () => {
      if (!currentNode.value) return
      
      const type = currentNode.value.data.type
      
      // 根据类型更新节点样式
      let fillColor = '#f5f5f5'
      
      switch (type) {
        case 'shell':
          fillColor = '#e6f7ff'
          break
        case 'python':
          fillColor = '#f6ffed'
          break
        case 'condition':
          fillColor = '#fff7e6'
          break
        case 'parallel':
          fillColor = '#f9f0ff'
          break
      }
      
      currentNode.value.attr('body/fill', fillColor)
    }
    
    // 保存工作流
    const handleSave = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            // 保存图形数据
            const graphData = graph.value.toJSON()
            workflowForm.definition = JSON.stringify(graphData)
            
            if (isEdit.value) {
              await updateWorkflow(workflowId.value, workflowForm)
              ElMessage.success('更新成功')
            } else {
              await createWorkflow(workflowForm)
              ElMessage.success('创建成功')
            }
            
            router.push('/workflow')
          } catch (error) {
            ElMessage.error('保存失败')
          }
        }
      })
    }
    
    // 返回列表
    const goBack = () => {
      router.push('/workflow')
    }
    
    return {
      workflowForm,
      rules,
      formRef,
      graphContainer,
      codeEditor,
      currentNode,
      tagOptions,
      isEdit,
      handleAddNode,
      handleAddEdge,
      handleDelete,
      updateNodeName,
      updateNodeType,
      handleSave,
      goBack
    }
  }
})
</script>

<style lang="less" scoped>
.workflow-edit-container {
  .box-card {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .workflow-editor {
    margin-top: 20px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    
    .editor-toolbar {
      padding: 8px;
      border-bottom: 1px solid #dcdfe6;
    }
    
    .editor-container {
      height: 400px;
    }
  }
  
  .node-config {
    margin-top: 20px;
    padding: 15px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    
    h3 {
      margin-top: 0;
      margin-bottom: 15px;
    }
    
    .code-editor {
      height: 200px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
    }
  }
}
</style> 