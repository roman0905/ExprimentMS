import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'

export interface UserPermission {
  permission_id: number
  user_id: number
  module: string
  can_read: boolean
  can_write: boolean
  can_delete: boolean
}

export interface UserInfo {
  user_id: number
  username: string
  role: 'Admin' | 'User'
  created_at: string
  permissions: UserPermission[]
}

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)
  const token = ref('')
  const userInfo = ref<UserInfo | null>(null)
  const loading = ref(false)

  // 计算属性
  const isAdmin = computed(() => userInfo.value?.role === 'Admin')
  const username = computed(() => userInfo.value?.username || '')

  // 登录
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      loading.value = true
      const response = await api.post('/api/auth/login', {
        username,
        password
      })
      
      if (response.data.access_token) {
        token.value = response.data.access_token
        isLoggedIn.value = true
        
        // 保存到本地存储
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('isLoggedIn', 'true')
        
        // 获取用户详细信息
        await getCurrentUser()
        
        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取当前用户信息
  const getCurrentUser = async () => {
    try {
      if (!token.value) return
      
      const response = await api.get('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })
      
      userInfo.value = response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取用户信息失败，可能是token过期，执行登出
      logout()
    }
  }

  // 登出
  const logout = async () => {
    try {
      if (token.value) {
        await api.post('/api/auth/logout', {}, {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        })
      }
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 清除状态
      isLoggedIn.value = false
      token.value = ''
      userInfo.value = null
      
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('isLoggedIn')
    }
  }

  // 检查模块权限
  const hasModulePermission = (module: string, permissionType: 'read' | 'write' | 'delete' = 'read'): boolean => {
    // 管理员拥有所有权限
    if (isAdmin.value) {
      return true
    }
    
    if (!userInfo.value?.permissions) {
      return false
    }
    
    const permission = userInfo.value.permissions.find(p => p.module === module)
    if (!permission) {
      return false
    }
    
    switch (permissionType) {
      case 'read':
        return permission.can_read
      case 'write':
        return permission.can_write
      case 'delete':
        return permission.can_delete
      default:
        return false
    }
  }

  // 检查是否有任何模块的权限
  const hasAnyPermission = (module: string): boolean => {
    return hasModulePermission(module, 'read') || 
           hasModulePermission(module, 'write') || 
           hasModulePermission(module, 'delete')
  }

  // 初始化认证状态
  const initAuth = async () => {
    const storedToken = localStorage.getItem('token')
    const storedIsLoggedIn = localStorage.getItem('isLoggedIn')
    
    if (storedToken && storedIsLoggedIn === 'true') {
      token.value = storedToken
      isLoggedIn.value = true
      
      // 尝试获取用户信息验证token有效性
      await getCurrentUser()
    }
  }

  // 设置请求拦截器
  const setupApiInterceptors = () => {
    // 请求拦截器 - 自动添加token
    api.interceptors.request.use(
      (config) => {
        if (token.value) {
          config.headers.Authorization = `Bearer ${token.value}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器 - 处理401错误
    api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // token过期或无效，执行登出
          logout()
        }
        return Promise.reject(error)
      }
    )
  }

  return {
    // 状态
    isLoggedIn,
    token,
    userInfo,
    loading,
    
    // 计算属性
    isAdmin,
    username,
    
    // 方法
    login,
    logout,
    getCurrentUser,
    hasModulePermission,
    hasAnyPermission,
    initAuth,
    setupApiInterceptors
  }
})