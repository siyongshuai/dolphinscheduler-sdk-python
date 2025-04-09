<template>
  <div class="navbar">
    <hamburger :is-active="!sidebarCollapsed" class="hamburger-container" @toggle-click="toggleSidebar" />
    
    <breadcrumb class="breadcrumb-container" />

    <div class="right-menu">
      <el-dropdown class="avatar-container" trigger="click">
        <div class="avatar-wrapper">
          <el-avatar :size="30" icon="el-icon-user-solid" />
          <span class="user-name">{{ username }}</span>
          <i class="el-icon-caret-bottom" />
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人中心</el-dropdown-item>
            <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessageBox } from 'element-plus'
import Hamburger from './Hamburger.vue'
import Breadcrumb from './Breadcrumb.vue'

export default defineComponent({
  name: 'Navbar',
  components: {
    Hamburger,
    Breadcrumb
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const sidebarCollapsed = computed(() => store.state.app?.sidebar?.collapsed || false)
    const username = computed(() => store.getters.username || '用户')
    
    const toggleSidebar = () => {
      store.dispatch('app/toggleSidebar')
    }
    
    const logout = () => {
      ElMessageBox.confirm('确定要退出登录吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        store.dispatch('user/logout').then(() => {
          router.push('/login')
        })
      }).catch(() => {})
    }
    
    return {
      sidebarCollapsed,
      username,
      toggleSidebar,
      logout
    }
  }
})
</script>

<style lang="less" scoped>
.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  
  .hamburger-container {
    line-height: 46px;
    height: 100%;
    float: left;
    cursor: pointer;
    transition: background 0.3s;
    margin-left: 10px;
    
    &:hover {
      background: rgba(0, 0, 0, 0.025);
    }
  }
  
  .breadcrumb-container {
    float: left;
    margin-left: 20px;
  }
  
  .right-menu {
    float: right;
    height: 100%;
    margin-right: 20px;
    display: flex;
    align-items: center;
    
    .avatar-container {
      cursor: pointer;
      
      .avatar-wrapper {
        display: flex;
        align-items: center;
        
        .user-name {
          margin: 0 5px;
        }
      }
    }
  }
}
</style> 