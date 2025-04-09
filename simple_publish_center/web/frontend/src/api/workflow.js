import request from '@/utils/request'

/**
 * 获取工作流列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getWorkflows(params) {
  return request({
    url: '/api/workflows',
    method: 'get',
    params
  })
}

/**
 * 获取单个工作流详情
 * @param {String} id - 工作流ID
 * @returns {Promise}
 */
export function getWorkflowById(id) {
  return request({
    url: `/api/workflows/${id}`,
    method: 'get'
  })
}

/**
 * 创建工作流
 * @param {Object} data - 工作流数据
 * @returns {Promise}
 */
export function createWorkflow(data) {
  return request({
    url: '/api/workflows',
    method: 'post',
    data
  })
}

/**
 * 更新工作流
 * @param {String} id - 工作流ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateWorkflow(id, data) {
  return request({
    url: `/api/workflows/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除工作流
 * @param {String} id - 工作流ID
 * @returns {Promise}
 */
export function deleteWorkflow(id) {
  return request({
    url: `/api/workflows/${id}`,
    method: 'delete'
  })
}

/**
 * 运行工作流
 * @param {String} id - 工作流ID
 * @param {Object} params - 运行参数
 * @returns {Promise}
 */
export function runWorkflow(id, params) {
  return request({
    url: `/api/workflows/${id}/run`,
    method: 'post',
    data: params
  })
}

/**
 * 部署工作流
 * @param {String} id - 工作流ID
 * @returns {Promise}
 */
export function deployWorkflow(id) {
  return request({
    url: `/api/workflows/${id}/deploy`,
    method: 'post'
  })
}

/**
 * 导出工作流
 * @param {String} id - 工作流ID
 * @returns {Promise}
 */
export function exportWorkflow(id) {
  return request({
    url: `/api/workflows/${id}/export`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 导入工作流
 * @param {FormData} formData - 包含工作流文件的表单数据
 * @returns {Promise}
 */
export function importWorkflow(formData) {
  return request({
    url: '/api/workflows/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 