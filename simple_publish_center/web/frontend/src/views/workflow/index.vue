<template>
  <div class="workflow-container">
    <div class="filter-container">
      <el-input
        v-model="query.name"
        placeholder="工作流名称"
        class="filter-item"
        clearable
        @keyup.enter="handleFilter"
      />
      
      <el-select
        v-model="query.status"
        placeholder="状态"
        clearable
        class="filter-item"
      >
        <el-option label="已部署" value="DEPLOYED" />
        <el-option label="草稿" value="DRAFT" />
      </el-select>
      
      <el-button type="primary" class="filter-item" @click="handleFilter">搜索</el-button>
      <el-button type="primary" class="filter-item" @click="handleCreate">新建工作流</el-button>
      <el-button type="primary" class="filter-item" @click="handleImport">导入</el-button>
      
      <el-dropdown class="filter-item" trigger="click" @command="handleBatchCommand">
        <el-button type="primary">
          批量操作 <i class="el-icon-arrow-down el-icon--right"></i>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="deploy">批量部署</el-dropdown-item>
            <el-dropdown-item command="export">批量导出</el-dropdown-item>
            <el-dropdown-item command="delete">批量删除</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    
    <el-table
      v-loading="loading"
      :data="workflowList"
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column prop="name" label="工作流名称" min-width="150" />
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column prop="updatedAt" label="最后修改时间" width="180" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'DEPLOYED' ? 'success' : 'info'">
            {{ row.status === 'DEPLOYED' ? '已部署' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center">
        <template #default="{ row }">
          <el-button type="text" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-dropdown trigger="click" @command="(command) => handleCommand(command, row)">
            <el-button type="text" size="small">
              更多<i class="el-icon-arrow-down el-icon--right"></i>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="run">运行</el-dropdown-item>
                <el-dropdown-item command="deploy">部署</el-dropdown-item>
                <el-dropdown-item command="export">导出</el-dropdown-item>
                <el-dropdown-item command="delete">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-container">
      <el-pagination
        :current-page="query.page"
        :page-sizes="[10, 20, 30, 50]"
        :page-size="query.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 运行工作流对话框 -->
    <el-dialog title="运行工作流" v-model="runDialogVisible" width="500px">
      <el-form ref="runForm" :model="runForm" label-width="80px">
        <el-form-item label="参数">
          <el-input
            v-model="runForm.parameters"
            type="textarea"
            rows="10"
            placeholder="请输入JSON格式的参数"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="runDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRun">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, reactive, toRefs, computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteWorkflow, exportWorkflow, runWorkflow } from '@/api/workflow'

export default defineComponent({
  name: 'WorkflowList',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const state = reactive({
      loading: false,
      query: {
        page: 1,
        pageSize: 10,
        name: '',
        status: '',
        sortBy: 'createdAt',
        sortOrder: 'desc'
      },
      runDialogVisible: false,
      runForm: {
        workflowId: '',
        parameters: '{}'
      },
      selectedWorkflows: []
    })
    
    const workflowList = computed(() => store.getters.workflows)
    const total = computed(() => store.getters.workflowTotal)
    
    // 获取工作流列表
    const getList = async () => {
      state.loading = true
      try {
        await store.dispatch('workflow/getList')
      } finally {
        state.loading = false
      }
    }
    
    // 初始化
    onMounted(() => {
      getList()
    })
    
    // 搜索
    const handleFilter = () => {
      state.query.page = 1
      store.dispatch('workflow/updateQuery', state.query)
    }
    
    // 新建工作流
    const handleCreate = () => {
      router.push('/workflow/edit')
    }
    
    // 编辑工作流
    const handleEdit = (row) => {
      router.push(`/workflow/edit/${row.id}`)
    }
    
    // 导入工作流
    const handleImport = () => {
      // 调用导入功能
    }
    
    // 单个工作流操作
    const handleCommand = (command, row) => {
      switch (command) {
        case 'run':
          handleRun(row)
          break
        case 'deploy':
          handleDeploy(row)
          break
        case 'export':
          handleExport(row)
          break
        case 'delete':
          handleDelete(row)
          break
      }
    }
    
    // 批量操作
    const handleBatchCommand = (command) => {
      if (state.selectedWorkflows.length === 0) {
        ElMessage.warning('请选择工作流')
        return
      }
      
      switch (command) {
        case 'deploy':
          handleBatchDeploy()
          break
        case 'export':
          handleBatchExport()
          break
        case 'delete':
          handleBatchDelete()
          break
      }
    }
    
    // 表格选择变化
    const handleSelectionChange = (selection) => {
      state.selectedWorkflows = selection
    }
    
    // 分页大小变化
    const handleSizeChange = (size) => {
      state.query.pageSize = size
      store.dispatch('workflow/updateQuery', state.query)
    }
    
    // 页码变化
    const handleCurrentChange = (page) => {
      state.query.page = page
      store.dispatch('workflow/updateQuery', state.query)
    }
    
    // 运行工作流
    const handleRun = (row) => {
      state.runForm.workflowId = row.id
      state.runForm.parameters = '{}'
      state.runDialogVisible = true
    }
    
    // 确认运行
    const confirmRun = () => {
      try {
        const params = JSON.parse(state.runForm.parameters)
        runWorkflow(state.runForm.workflowId, {
          parameters: params,
          runMode: 'ASYNC'
        }).then(response => {
          ElMessage.success('工作流已提交运行')
          state.runDialogVisible = false
        }).catch(() => {})
      } catch (error) {
        ElMessage.error('参数格式错误，请输入有效的JSON')
      }
    }
    
    // 部署工作流
    const handleDeploy = (row) => {
      // 调用部署API
    }
    
    // 导出工作流
    const handleExport = (row) => {
      exportWorkflow(row.id).then(response => {
        // 处理文件下载
      })
    }
    
    // 删除工作流
    const handleDelete = (row) => {
      ElMessageBox.confirm('确定要删除该工作流吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteWorkflow(row.id).then(() => {
          ElMessage.success('删除成功')
          getList()
        })
      }).catch(() => {})
    }
    
    // 批量部署
    const handleBatchDeploy = () => {
      // 实现批量部署逻辑
    }
    
    // 批量导出
    const handleBatchExport = () => {
      // 实现批量导出逻辑
    }
    
    // 批量删除
    const handleBatchDelete = () => {
      ElMessageBox.confirm(`确定要删除选中的${state.selectedWorkflows.length}个工作流吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        // 实现批量删除逻辑
      }).catch(() => {})
    }
    
    return {
      ...toRefs(state),
      workflowList,
      total,
      handleFilter,
      handleCreate,
      handleEdit,
      handleImport,
      handleCommand,
      handleBatchCommand,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      confirmRun
    }
  }
})
</script>

<style lang="less" scoped>
.workflow-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  
  .filter-container {
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap;
    
    .filter-item {
      margin-right: 10px;
      margin-bottom: 10px;
      width: 200px;
      
      &:last-child {
        margin-right: 0;
      }
    }
    
    .el-button {
      width: auto;
    }
  }
  
  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
}
</style> 