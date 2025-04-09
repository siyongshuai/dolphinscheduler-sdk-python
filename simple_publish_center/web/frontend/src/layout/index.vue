<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <sidebar class="sidebar-container" />
    
    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 头部 -->
      <navbar />
      
      <!-- 标签 -->
      <tags-view />
      
      <!-- 内容 -->
      <app-main />
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import Sidebar from './components/Sidebar/index.vue'
import Navbar from './components/Navbar.vue'
import TagsView from './components/TagsView.vue'
import AppMain from './components/AppMain.vue'

export default defineComponent({
  name: 'Layout',
  components: {
    Sidebar,
    Navbar,
    TagsView,
    AppMain
  }
})
</script>

<style lang="less" scoped>
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
  
  .sidebar-container {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    width: 200px;
    overflow: hidden;
    z-index: 1001;
    transition: width 0.28s;
  }
  
  .main-container {
    min-height: 100%;
    margin-left: 200px;
    position: relative;
    transition: margin-left 0.28s;
  }
}
</style> 