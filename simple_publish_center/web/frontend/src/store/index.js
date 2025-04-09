import { createStore } from 'vuex'
import user from './modules/user'
import workflow from './modules/workflow'
import script from './modules/script'
import instance from './modules/instance'
import getters from './getters'

export default createStore({
  modules: {
    user,
    workflow,
    script,
    instance
  },
  getters
}) 