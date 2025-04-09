<template>
  <section class="app-main">
    <router-view v-slot="{ Component }">
      <transition name="fade-transform" mode="out-in">
        <keep-alive :include="cachedViews">
          <component :is="Component" />
        </keep-alive>
      </transition>
    </router-view>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'

export default defineComponent({
  name: 'AppMain',
  setup() {
    const store = useStore()
    const cachedViews = computed(() => store.state.tagsView?.cachedViews || [])
    
    return {
      cachedViews
    }
  }
})
</script>

<style lang="less" scoped>
.app-main {
  padding: 15px;
  height: calc(100vh - 84px);
  overflow: auto;
  background-color: #f5f7f9;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style> 