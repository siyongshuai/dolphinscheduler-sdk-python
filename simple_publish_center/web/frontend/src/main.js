import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/index.less'

const app = createApp(App)

// 全局挂载Element Plus组件
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$msgbox = ElMessageBox
app.config.globalProperties.$loading = ElLoading.service

// 注册全局指令
import * as directives from './directives'
Object.keys(directives).forEach(key => {
  app.directive(key, directives[key])
})

// 错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('应用错误:', err, info)
}

app.use(store)
  .use(router)
  .mount('#app') 