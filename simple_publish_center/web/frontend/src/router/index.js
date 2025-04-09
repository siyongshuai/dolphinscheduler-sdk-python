import { createRouter, createWebHashHistory } from 'vue-router'
import { getToken } from '@/utils/auth'
import store from '@/store'

// 页面路由
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', isAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '控制台', icon: 'dashboard', affix: true }
      },
      {
        path: 'workflow',
        name: 'Workflow',
        component: () => import('@/views/workflow/index.vue'),
        meta: { title: '工作流管理', icon: 'workflow' }
      },
      {
        path: 'workflow/edit/:id?',
        name: 'WorkflowEdit',
        component: () => import('@/views/workflow/edit.vue'),
        meta: { title: '编辑工作流', activeMenu: '/workflow', hidden: true }
      },
      {
        path: 'template',
        name: 'Template',
        component: () => import('@/views/template/index.vue'),
        meta: { title: '模板管理', icon: 'template' }
      },
      {
        path: 'batch',
        name: 'Batch',
        component: () => import('@/views/batch/index.vue'),
        meta: { title: '批量部署', icon: 'batch' }
      },
      {
        path: 'script',
        name: 'Script',
        component: () => import('@/views/script/index.vue'),
        meta: { title: '脚本管理', icon: 'script' }
      },
      {
        path: 'instance',
        name: 'Instance',
        component: () => import('@/views/instance/index.vue'),
        meta: { title: '执行实例', icon: 'instance' }
      },
      {
        path: 'instance/:id',
        name: 'InstanceDetail',
        component: () => import('@/views/instance/detail.vue'),
        meta: { title: '实例详情', activeMenu: '/instance', hidden: true }
      }
    ]
  },
  {
    path: '/404',
    component: () => import('@/views/error/404.vue'),
    meta: { hidden: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: { hidden: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes
})

// 路由守卫，处理权限验证
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 工作流管理系统` : '工作流管理系统'
  
  const hasToken = getToken()
  
  // 不需要认证或已有Token，直接通过
  if (to.meta.isAuth === false || hasToken) {
    // 已登录状态下访问登录页，重定向到首页
    if (to.path === '/login' && hasToken) {
      next({ path: '/' })
    } else {
      // 检查用户信息是否已加载
      if (store.getters.userInfo) {
        next()
      } else {
        try {
          // 获取用户信息
          await store.dispatch('user/getUserInfo')
          next()
        } catch (error) {
          // 获取用户信息失败，重置Token并重定向到登录页
          await store.dispatch('user/resetToken')
          next({ path: '/login', query: { redirect: to.fullPath } })
        }
      }
    }
  } else {
    // 未登录，重定向到登录页
    next({ path: '/login', query: { redirect: to.fullPath } })
  }
})

export default router 