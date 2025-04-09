<template>
  <div class="login-container">
    <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" autocomplete="on" label-position="left">
      <div class="title-container">
        <h3 class="title">工作流管理系统</h3>
      </div>

      <el-form-item prop="username">
        <el-input
          ref="username"
          v-model="loginForm.username"
          placeholder="用户名"
          name="username"
          type="text"
          tabindex="1"
          autocomplete="on"
          prefix-icon="el-icon-user"
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          ref="password"
          v-model="loginForm.password"
          :type="passwordVisible ? 'text' : 'password'"
          placeholder="密码"
          name="password"
          tabindex="2"
          autocomplete="on"
          prefix-icon="el-icon-lock"
          @keyup.enter="handleLogin"
        >
          <template #suffix>
            <el-icon class="show-pwd" @click="passwordVisible = !passwordVisible">
              <svg-icon :icon-class="passwordVisible ? 'eye' : 'eye-close'" />
            </el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-button :loading="loading" type="primary" style="width:100%;margin-bottom:30px;" @click.prevent="handleLogin">登录</el-button>
    </el-form>
  </div>
</template>

<script>
import { defineComponent, reactive, ref, toRefs } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'Login',
  setup() {
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const loginRules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
    }
    
    const loginFormRef = ref(null)
    const loading = ref(false)
    const passwordVisible = ref(false)
    
    const router = useRouter()
    const route = useRoute()
    const store = useStore()
    
    const handleLogin = () => {
      loginFormRef.value.validate(valid => {
        if (valid) {
          loading.value = true
          store.dispatch('user/login', loginForm)
            .then(() => {
              // 登录成功，跳转到首页或之前访问的页面
              const redirect = route.query.redirect || '/'
              router.push({ path: redirect })
              ElMessage({
                message: '登录成功',
                type: 'success'
              })
            })
            .catch(() => {
              loading.value = false
            })
        } else {
          ElMessage({
            message: '请输入正确的用户名和密码',
            type: 'error'
          })
          return false
        }
      })
    }
    
    return {
      loginForm,
      loginRules,
      loginFormRef,
      loading,
      passwordVisible,
      handleLogin
    }
  }
})
</script>

<style lang="less" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  background-color: #f5f7f9;
  overflow: hidden;
  
  .login-form {
    width: 400px;
    max-width: 100%;
    padding: 35px 35px 15px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .title-container {
      position: relative;
      
      .title {
        font-size: 26px;
        color: #333;
        margin: 0 auto 30px;
        text-align: center;
        font-weight: 700;
      }
    }
    
    .show-pwd {
      cursor: pointer;
    }
  }
}
</style> 