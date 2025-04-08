<template>
  <div class="instance-detail-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>执行实例详情</span>
          <div>
            <el-button 
              type="danger" 
              @click="handleStop" 
              v-if="instanceDetail.status === 'RUNNING'"
            >
              停止执行
            </el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>
      
      <el-descriptions class="instance-info" :column="2" border>
        <el-descriptions-item label="实例ID">{{ instanceDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="工作流">{{ instanceDetail.workflowName }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ formatTime(instanceDetail.startTime) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ instanceDetail.endTime ? formatTime(instanceDetail.endTime) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(instanceDetail.status)">
            {{ formatStatus(instanceDetail.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行参数" :span="2" v-if="instanceDetail.params">
          <div class="params-block">
            <pre>{{ formatParams(instanceDetail.params) }}</pre>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      
      <div class="execution-graph">
        <h3>执行图形</h3>
        <div class="graph-container" ref="graphContainer"></div>
      </div>
      
      <div class="node-executions">
        <h3>节点执行情况</h3>
        <el-table :data="nodeExecutions" style="width: 100%" v-loading="loading">
          <el-table-column prop="nodeName" label="节点名称" />
          <el-table-column prop="nodeType" label="节点类型">
            <template #default="scope">
              {{ formatNodeType(scope.row.nodeType) }}
            </template>
          </el-table-column>
          <el-table-column prop="startTime" label="开始时间">
            <template #default="scope">
              {{ formatTime(scope.row.startTime) }}
            </template>
          </el-table-column>
          <el-table-column prop="endTime" label="结束时间">
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
                @click="viewNodeLogs(scope.row)"
              >
                查看日志
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <!-- 日志查看对话框 -->
    <el-dialog
      v-model="logDialogVisible"
      :title="`${currentNode.nodeName || '节点'} 执行日志`"
      width="70%"
      fullscreen
    >
      <div class="log-container">
        <div class="log-actions">
          <el-button type="primary" size="small" @click="refreshLogs">刷新</el-button>
          <el-button size="small" @click="downloadLogs">下载</el-button>
        </div>
        <div 
          class="log-content" 
          v-loading="logsLoading"
          element-loading-text="加载日志中..."
        >
          <pre>{{ logs }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Graph } from '@antv/x6'
import { 
  getInstanceById, 
  getNodeExecutions, 
  getNodeLogs,
  stopInstance 
} from '@/api/instance'
import { formatDateTime } from '@/utils/format'

export default defineComponent({
  name: 'InstanceDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const instanceId = computed(() => route.params.id)
    const graphContainer = ref(null)
    const graph = ref(null)
    
    const instanceDetail = ref({})
    const nodeExecutions = ref([])
    const loading = ref(false)
    const logsLoading = ref(false)
    const logs = ref('')
    const logDialogVisible = ref(false)
    const currentNode = reactive({
      nodeId: '',
      nodeName: ''
    })
    
    // 自动刷新相关变量
    const refreshTimer = ref(null)
    const autoRefresh = ref(true)
    
    onMounted(async () => {
      await loadInstanceDetail()
      loadNodeExecutions()
      
      // 如果实例状态是运行中，启动自动刷新
      if (instanceDetail.value.status === 'RUNNING') {
        startAutoRefresh()
      }
    })
    
    onUnmounted(() => {
      // 组件销毁时清除定时器
      stopAutoRefresh()
    })
    
    // 启动自动刷新
    const startAutoRefresh = () => {
      if (refreshTimer.value) return
      
      refreshTimer.value = setInterval(() => {
        if (autoRefresh.value) {
          loadInstanceDetail(false)
          loadNodeExecutions(false)
          
          // 如果实例已经不是运行中状态，停止自动刷新
          if (instanceDetail.value.status !== 'RUNNING') {
            stopAutoRefresh()
          }
        }
      }, 5000) // 每5秒刷新一次
    }
    
    // 停止自动刷新
    const stopAutoRefresh = () => {
      if (refreshTimer.value) {
        clearInterval(refreshTimer.value)
        refreshTimer.value = null
      }
    }
    
    // 加载实例详情
    const loadInstanceDetail = async (showLoading = true) => {
      if (showLoading) loading.value = true
      try {
        const response = await getInstanceById(instanceId.value)
        instanceDetail.value = response.data
        
        // 初始化工作流图形
        if (instanceDetail.value.graph) {
          initGraph(instanceDetail.value.graph)
        }
      } catch (error) {
        ElMessage.error('加载实例详情失败')
      } finally {
        if (showLoading) loading.value = false
      }
    }
    
    // 加载节点执行记录
    const loadNodeExecutions = async (showLoading = true) => {
      if (showLoading) loading.value = true
      try {
        const response = await getNodeExecutions(instanceId.value)
        nodeExecutions.value = response.data
        
        // 更新图形节点状态
        updateGraphNodesStatus()
      } catch (error) {
        ElMessage.error('加载节点执行记录失败')
      } finally {
        if (showLoading) loading.value = false
      }
    }
    
    // 初始化图形展示
    const initGraph = (graphData) => {
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
      
      graph.value.fromJSON(graphData)
      
      // 自动调整画布大小以适应所有节点
      graph.value.zoomToFit({ padding: 20 })
    }
    
    // 更新图形节点状态
    const updateGraphNodesStatus = () => {
      if (!graph.value) return
      
      nodeExecutions.value.forEach(nodeExec => {
        const cell = graph.value.getCellById(nodeExec.nodeId)
        if (cell) {
          let statusColor = '#808080' // 默认灰色
          
          switch (nodeExec.status) {
            case 'RUNNING':
              statusColor = '#409EFF' // 蓝色
              break
            case 'SUCCESS':
              statusColor = '#67C23A' // 绿色
              break
            case 'FAILED':
              statusColor = '#F56C6C' // 红色
              break
            case 'STOPPED':
              statusColor = '#E6A23C' // 橙色
              break
          }
          
          cell.attr('body/stroke', statusColor)
          cell.attr('label/style/color', statusColor)
        }
      })
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
    
    // 格式化参数
    const formatParams = (params) => {
      if (!params) return ''
      try {
        return typeof params === 'string' 
          ? JSON.stringify(JSON.parse(params), null, 2) 
          : JSON.stringify(params, null, 2)
      } catch (e) {
        return params
      }
    }
    
    // 查看节点日志
    const viewNodeLogs = async (node) => {
      currentNode.nodeId = node.nodeId
      currentNode.nodeName = node.nodeName
      logDialogVisible.value = true
      logs.value = ''
      
      await fetchNodeLogs()
    }
    
    // 获取节点日志
    const fetchNodeLogs = async () => {
      logsLoading.value = true
      try {
        const response = await getNodeLogs(instanceId.value, currentNode.nodeId)
        logs.value = response.data || '暂无日志'
      } catch (error) {
        ElMessage.error('获取日志失败')
        logs.value = '获取日志失败'
      } finally {
        logsLoading.value = false
      }
    }
    
    // 刷新日志
    const refreshLogs = () => {
      fetchNodeLogs()
    }
    
    // 下载日志
    const downloadLogs = () => {
      if (!logs.value) {
        ElMessage.warning('无日志内容可下载')
        return
      }
      
      const blob = new Blob([logs.value], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      
      a.href = url
      a.download = `${currentNode.nodeName || 'node'}_${instanceId.value}_logs.txt`
      document.body.appendChild(a)
      a.click()
      
      setTimeout(() => {
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }, 100)
    }
    
    // 停止实例
    const handleStop = async () => {
      try {
        await ElMessageBox.confirm('确定要停止当前执行实例吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await stopInstance(instanceId.value)
        ElMessage.success('已停止执行')
        
        // 重新加载实例详情
        loadInstanceDetail()
        loadNodeExecutions()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('停止执行失败')
        }
      }
    }
    
    // 返回列表
    const goBack = () => {
      router.go(-1)
    }
    
    return {
      instanceDetail,
      nodeExecutions,
      loading,
      logsLoading,
      logs,
      logDialogVisible,
      currentNode,
      graphContainer,
      formatTime,
      formatStatus,
      getStatusType,
      formatNodeType,
      formatParams,
      viewNodeLogs,
      refreshLogs,
      downloadLogs,
      handleStop,
      goBack
    }
  }
})
</script>

<style lang="less" scoped>
.instance-detail-container {
  .box-card {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .instance-info {
    margin-bottom: 20px;
  }
  
  .params-block {
    max-height: 150px;
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
  
  .execution-graph {
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
  
  .node-executions {
    margin: 20px 0;
    
    h3 {
      margin-bottom: 15px;
    }
  }
  
  .log-container {
    .log-actions {
      margin-bottom: 10px;
      text-align: right;
    }
    
    .log-content {
      height: calc(80vh - 100px);
      background-color: #1e1e1e;
      color: #e6e6e6;
      padding: 15px;
      overflow: auto;
      border-radius: 4px;
      
      pre {
        margin: 0;
        font-family: Consolas, Monaco, 'Andale Mono', monospace;
        white-space: pre-wrap;
        word-wrap: break-word;
      }
    }
  }
}
</style> 