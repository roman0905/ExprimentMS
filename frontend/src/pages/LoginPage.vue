<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>实验数据管理系统</h2>
        <div class="mode-switch">
          <el-button
            :type="isLoginMode ? 'primary' : 'default'"
            size="small"
            @click="switchToLogin"
          >
            登录
          </el-button>
          <el-button
            :type="!isLoginMode ? 'primary' : 'default'"
            size="small"
            @click="switchToRegister"
          >
            注册账号
          </el-button>
        </div>
      </div>
      
      <!-- 登录表单 -->
      <el-form
        v-if="isLoginMode"
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 注册表单 -->
      <el-form
        v-else
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="login-form"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- <div class="login-tips">
        <p>默认账号：admin</p>
        <p>默认密码：admin123</p>
      </div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { userApi } from '@/services/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)
const isLoginMode = ref(true)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const switchToLogin = () => {
  isLoginMode.value = true
  // 清空表单
  loginForm.username = ''
  loginForm.password = ''
}

const switchToRegister = () => {
  isLoginMode.value = false
  // 清空表单
  registerForm.username = ''
  registerForm.password = ''
  registerForm.confirmPassword = ''
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const success = await authStore.login(loginForm.username, loginForm.password)
        
        if (success) {
          ElMessage.success('登录成功')
          
          // 检查是否有重定向参数
          const redirect = route.query.redirect as string
          if (redirect && redirect !== '/login') {
            router.push(redirect)
          } else {
            router.push('/dashboard')
          }
        } else {
          ElMessage.error('用户名或密码错误')
        }
      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error('登录失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const response = await userApi.register({
          username: registerForm.username,
          password: registerForm.password
        })
        
        if (response.data) {
          // 注册成功，自动登录
          const { access_token, user_info } = response.data
          
          // 保存token和用户信息
          localStorage.setItem('token', access_token)
          authStore.setUser(user_info)
          authStore.setToken(access_token)
          
          ElMessage.success('注册成功，已自动登录')
          
          // 检查是否有重定向参数
          const redirect = route.query.redirect as string
          if (redirect && redirect !== '/login') {
            router.push(redirect)
          } else {
            router.push('/dashboard')
          }
        }
      } catch (error: any) {
        console.error('注册错误:', error)
        const errorMessage = error.response?.data?.detail || '注册失败，请稍后重试'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #303133;
  margin: 0 0 16px 0;
  font-size: 24px;
  font-weight: 600;
}

.login-header p {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

.mode-switch {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 8px;
}

.mode-switch .el-button {
  flex: 1;
  max-width: 80px;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.login-tips {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.login-tips p {
  margin: 4px 0;
  color: #606266;
  font-size: 13px;
}
</style>