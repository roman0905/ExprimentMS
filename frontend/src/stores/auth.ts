import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)
  const username = ref('')

  // 简单的管理员登录验证
  const login = (user: string, password: string): boolean => {
    // 简单的硬编码验证，实际项目中应该调用API
    if (user === 'admin' && password === 'admin123') {
      isLoggedIn.value = true
      username.value = user
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('username', user)
      return true
    }
    return false
  }

  const logout = () => {
    isLoggedIn.value = false
    username.value = ''
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('username')
  }

  // 初始化时检查本地存储
  const initAuth = () => {
    const stored = localStorage.getItem('isLoggedIn')
    const storedUsername = localStorage.getItem('username')
    if (stored === 'true' && storedUsername) {
      isLoggedIn.value = true
      username.value = storedUsername
    }
  }

  return {
    isLoggedIn,
    username,
    login,
    logout,
    initAuth
  }
})