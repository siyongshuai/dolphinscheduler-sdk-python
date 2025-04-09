<template>
  <div class="workflow-detail-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>工作流详情</span>
          <div>
            <el-button type="primary" @click="handleEdit">编辑</el-button>
            <el-button type="success" @click="handleRun">执行</el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>
      
      <el-descriptions class="workflow-info" :column="2" border>
        <el-descriptions-item label="工作流名称">{{ workflowDetail.name }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ workflowDetail.creator }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(workflowDetail.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(workflowDetail.updateTime) }}</el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">
          <el-tag v-for="tag in workflowDetail.tags" :key="tag" style="margin-right: 5px">{{ tag }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ workflowDetail.description }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="workflow-graph">
        <h3>工作流图形</h3>
        <div class="graph-container" ref="graphContainer"></div>
      </div>
      
      <el-tabs v-model="activeTab" class="workflow-tabs">
        <el-tab-pane label="执行记录" name="instances">
          <el-table :data="instanceList" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="实例ID" width="180" />
            <el-table-column prop="startTime" label="开始时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.startTime) }}
              </template>
            </el-table-column>
            <el-table-column prop="endTime" label="结束时间" width="180">
              <template #default="scope">
                {{ scope.row.endTime ? formatTime(scope.row.endTime) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ formatStatus(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button 
                  size="small" 
                  @click="viewInstanceDetail(scope.row.id)"
                >
                  查看
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="stopInstance(scope.row.id)"
                  v-if="scope.row.status === 'RUNNING'"
                >
                  停止
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              v-model:currentPage="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="节点信息" name="nodes">
          <el-collapse v-if="workflowDetail.definition">
            <el-collapse-item 
              v-for="(node, index) in nodeList" 
              :key="index" 
              :title="node.name || '未命名节点'"
            >
              <el-descriptions :column="1" border>
                <el-descriptions-item label="节点类型">{{ formatNodeType(node.type) }}</el-descriptions-item>
                <el-descriptions-item label="代码内容" v-if="node.type === 'shell' || node.type === 'python'">
                  <div class="code-block">
                    <pre><code>{{ node.script || '无代码内容' }}</code></pre>
                  </div>
                </el-descriptions-item>
                <el-descriptions-item label="条件表达式" v-if="node.type === 'condition'">
                  {{ node.condition || '无条件表达式' }}
                </el-descriptions-item>
              </el-descriptions>
            </el-collapse-item>
          </el-collapse>
          <el-empty v-else description="暂无节点信息"></el-empty>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 运行对话框 -->
    <el-dialog
      v-model="runDialogVisible"
      title="执行工作流"
      width="500px"
    >
      <el-form :model="runForm" label-width="100px">
        <el-form-item label="执行参数">
          <el-input
            v-model="runForm.params"
            type="textarea"
            placeholder="请输入JSON格式的执行参数（可选）"
            rows="5"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="runDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRun">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Graph } from '@antv/x6'
import { getWorkflowById, runWorkflow, stopWorkflowInstance } from '@/api/workflow'
import { getWorkflowInstances } from '@/api/instance'
import { formatDateTime } from '@/utils/format'

export default defineComponent({
  name: 'WorkflowDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const workflowId = computed(() => route.params.id)
    const graphContainer = ref(null)
    const graph = ref(null)
    
    const workflowDetail = ref({})
    const nodeList = ref([])
    const instanceList = ref([])
    const loading = ref(false)
    const activeTab = ref('instances')
    
    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    
    // 运行对话框
    const runDialogVisible = ref(false)
    const runForm = reactive({
      params: ''
    })
    
    onMounted(async () => {
      await loadWorkflowDetail()
      loadInstanceList()
    })
    
    // 加载工作流详情
    const loadWorkflowDetail = async () => {
      try {
        const response = await getWorkflowById(workflowId.value)
        workflowDetail.value = response.data
        
        // 解析定义并初始化图形
        if (workflowDetail.value.definition) {
          let definition
          try {
            definition = typeof workflowDetail.value.definition === 'string' 
              ? JSON.parse(workflowDetail.value.definition) 
              : workflowDetail.value.definition
          } catch (e) {
            definition = { nodes: [], edges: [] }
          }
          
          if (definition.nodes) {
            nodeList.value = definition.nodes.map(node => node.data || {})
          }
          
          initGraph(definition)
        }
      } catch (error) {
        ElMessage.error('加载工作流详情失败')
      }
    }
    
    // 初始化图形展示
    const initGraph = (definition) => {
      if (!graphContainer.value) return
      
      graph.value = new Graph({
        container: graphContainer.value,
        grid: true,
        mousewheel: {
          enabled: true,
          zoomAtMousePosition: true,
          modifiers: 'ctrl'
        },
        interacting: {
          nodeMovable: false,
          edgeMovable: false,
          magnetConnectable: false,
          vertexMovable: false,
          vertexAddable: false,
          vertexDeletable: false
        }
      })
      
      graph.value.fromJSON(definition)
      
      // 自动调整画布大小以适应所有节点
      graph.value.zoomToFit({ padding: 20 })
    }
    
    // 加载实例列表
    const loadInstanceList = async () => {
      loading.value = true
      try {
        const params = {
          workflowId: workflowId.value,
          page: currentPage.value,
          size: pageSize.value
        }
        
        const response = await getWorkflowInstances(params)
        instanceList.value = response.data.records
        total.value = response.data.total
      } catch (error) {
        ElMessage.error('加载执行记录失败')
      } finally {
        loading.value = false
      }
    }
    
    // 格式化时间
    const formatTime = (time) => {
      if (!time) return '-'
      return formatDateTime(time)
    }
    
    // 格式化状态
    const formatStatus = (status) => {
      const statusMap = {
        'RUNNING': '运行中',
        'SUCCESS': '成功',
        'FAILED': '失败',
        'STOPPED': '已停止',
        'PENDING': '等待中'
      }
      return statusMap[status] || status
    }
    
    // 获取状态标签类型
    const getStatusType = (status) => {
      const typeMap = {
        'RUNNING': 'primary',
        'SUCCESS': 'success',
        'FAILED': 'danger',
        'STOPPED': 'info',
        'PENDING': 'warning'
      }
      return typeMap[status] || ''
    }
    
    // 格式化节点类型
    const formatNodeType = (type) => {
      const typeMap = {
        'shell': 'Shell脚本',
        'python': 'Python脚本',
        'condition': '条件判断',
        'parallel': '并行任务'
      }
      return typeMap[type] || type
    }
    
    // 编辑工作流
    const handleEdit = () => {
      router.push(`/workflow/edit/${workflowId.value}`)
    }
    
    // 显示运行对话框
    const handleRun = () => {
      runDialogVisible.value = true
      runForm.params = ''
    }
    
    // 确认运行
    const confirmRun = async () => {
      try {
        let params = {}
        if (runForm.params) {
          try {
            params = JSON.parse(runForm.params)
          } catch (error) {
            ElMessage.error('参数格式错误，请输入有效的JSON格式')
            return
          }
        }
        
        await runWorkflow(workflowId.value, params)
        ElMessage.success('工作流已启动')
        runDialogVisible.value = false
        
        // 刷新实例列表
        loadInstanceList()
      } catch (error) {
        ElMessage.error('启动工作流失败')
      }
    }
    
    // 查看实例详情
    const viewInstanceDetail = (instanceId) => {
      router.push(`/instance/detail/${instanceId}`)
    }
    
    // 停止实例
    const stopInstance = async (instanceId) => {
      try {
        await ElMessageBox.confirm('确定要停止该执行实例吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await stopWorkflowInstance(instanceId)
        ElMessage.success('已停止执行')
        
        // 刷新实例列表
        loadInstanceList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('停止执行失败')
        }
      }
    }
    
    // 分页大小改变
    const handleSizeChange = (size) => {
      pageSize.value = size
      loadInstanceList()
    }
    
    // 页码改变
    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadInstanceList()
    }
    
    // 返回列表
    const goBack = () => {
      router.push('/workflow')
    }
    
    return {
      workflowDetail,
      nodeList,
      instanceList,
      loading,
      activeTab,
      currentPage,
      pageSize,
      total,
      graphContainer,
      runDialogVisible,
      runForm,
      formatTime,
      formatStatus,
      getStatusType,
      formatNodeType,
      handleEdit,
      handleRun,
      confirmRun,
      viewInstanceDetail,
      stopInstance,
      handleSizeChange,
      handleCurrentChange,
      goBack
    }
  }
})
</script>

<style lang="less" scoped>
.workflow-detail-container {
  .box-card {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .workflow-info {
    margin-bottom: 20px;
  }
  
  .workflow-graph {
    margin: 20px 0;
    
    h3 {
      margin-bottom: 15px;
    }
    
    .graph-container {
      height: 400px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
    }
  }
  
  .workflow-tabs {
    margin-top: 20px;
  }
  
  .code-block {
    max-height: 200px;
    overflow: auto;
    background-color: #f5f7fa;
    border-radius: 4px;
    padding: 10px;
    
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }
  
  .pagination {
    margin-top: 20px;
    text-align: right;
  }
}
</style> 