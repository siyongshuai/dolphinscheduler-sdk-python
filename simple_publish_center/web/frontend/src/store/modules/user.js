import { login, getUserInfo } from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'

const state = {
  token: getToken(),
  userInfo: null
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_USER_INFO: (state, userInfo) => {
    state.userInfo = userInfo
  },
  CLEAR_USER: (state) => {
    state.token = ''
    state.userInfo = null
  }
}

const actions = {
  // 用户登录
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password })
        .then(response => {
          const { data } = response
          commit('SET_TOKEN', data.accessToken)
          setToken(data.accessToken)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取用户信息
  getUserInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      if (!state.token) {
        reject('未登录')
        return
      }
      
      getUserInfo()
        .then(response => {
          const { data } = response
          if (!data) {
            reject('验证失败，请重新登录')
            return
          }
          
          commit('SET_USER_INFO', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 登出
  logout({ commit }) {
    return new Promise((resolve) => {
      commit('CLEAR_USER')
      removeToken()
      resolve()
    })
  },

  // 重置Token
  resetToken({ commit }) {
    return new Promise((resolve) => {
      commit('CLEAR_USER')
      removeToken()
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 