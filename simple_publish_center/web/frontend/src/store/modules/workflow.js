import { getWorkflows, getWorkflowDetail, createWorkflow, updateWorkflow, runWorkflow } from '@/api/workflow'

const state = {
  list: [],
  total: 0,
  query: {
    page: 1,
    pageSize: 10,
    name: '',
    status: '',
    sortBy: 'createdAt',
    sortOrder: 'desc'
  },
  current: null
}

const mutations = {
  SET_LIST: (state, { list, total }) => {
    state.list = list
    state.total = total
  },
  UPDATE_QUERY: (state, query) => {
    state.query = { ...state.query, ...query }
  },
  SET_CURRENT: (state, workflow) => {
    state.current = workflow
  },
  CLEAR_CURRENT: (state) => {
    state.current = null
  }
}

const actions = {
  // 获取工作流列表
  getList({ commit, state }) {
    return new Promise((resolve, reject) => {
      getWorkflows(state.query).then(response => {
        const { data, total } = response.data
        commit('SET_LIST', { list: data, total: total })
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },
  
  // 更新查询条件
  updateQuery({ commit, dispatch }, query) {
    commit('UPDATE_QUERY', query)
    return dispatch('getList')
  },

  // 获取工作流详情
  getDetail({ commit }, id) {
    return new Promise((resolve, reject) => {
      getWorkflowDetail(id)
        .then(response => {
          const { data } = response
          commit('SET_CURRENT', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 创建工作流
  create({ dispatch }, workflowData) {
    return new Promise((resolve, reject) => {
      createWorkflow(workflowData)
        .then(response => {
          dispatch('getList')
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 更新工作流
  update({ dispatch }, { id, workflowData }) {
    return new Promise((resolve, reject) => {
      updateWorkflow(id, workflowData)
        .then(response => {
          dispatch('getList')
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 运行工作流
  run({ commit }, { id, params }) {
    return new Promise((resolve, reject) => {
      runWorkflow(id, params)
        .then(response => {
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 清除当前工作流
  clearCurrent({ commit }) {
    commit('CLEAR_CURRENT')
  }
}

const getters = {
  workflows: state => state.list,
  workflowTotal: state => state.total
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 