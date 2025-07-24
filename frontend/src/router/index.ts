import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 导入页面组件
import LoginPage from '../pages/LoginPage.vue'
import Layout from '../components/Layout.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import BatchManagement from '../pages/BatchManagement.vue'
import PersonManagement from '../pages/PersonManagement.vue'
import ExperimentManagement from '../pages/ExperimentManagement.vue'
import CompetitorData from '../pages/CompetitorData.vue'
import FingerBloodData from '../pages/FingerBloodData.vue'
import SensorManagement from '../pages/SensorManagement.vue'
import UserManagement from '../pages/UserManagement.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: {
      requiresAuth: false,
      title: '登录'
    }
  },
  {
    path: '/',
    component: Layout,
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardPage,
        meta: {
          title: '首页',
          icon: 'House'
        }
      },
      {
        path: 'batches',
        name: 'BatchManagement',
        component: BatchManagement,
        meta: {
          title: '批次管理',
          icon: 'Collection',
          module: 'batch_management'
        }
      },
      {
        path: 'persons',
        name: 'PersonManagement',
        component: PersonManagement,
        meta: {
          title: '人员管理',
          icon: 'User',
          module: 'person_management'
        }
      },
      {
        path: 'experiments',
        name: 'ExperimentManagement',
        component: ExperimentManagement,
        meta: {
          title: '实验管理',
          icon: 'DataAnalysis',
          module: 'experiment_management'
        }
      },
      {
        path: 'competitorData',
        name: 'CompetitorData',
        component: CompetitorData,
        meta: {
          title: '竞品数据',
          icon: 'Files',
          module: 'competitor_data'
        }
      },
      {
        path: 'fingerBloodData',
        name: 'FingerBloodData',
        component: FingerBloodData,
        meta: {
          title: '指尖血数据',
          icon: 'TrendCharts',
          module: 'finger_blood_data'
        }
      },
      {
        path: 'sensors',
        name: 'SensorManagement',
        component: SensorManagement,
        meta: {
          title: '传感器管理',
          icon: 'Monitor',
          module: 'sensor_data'
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: UserManagement,
        meta: {
          title: '用户管理',
          icon: 'UserFilled',
          module: 'user_management',
          adminOnly: true
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 实验数据管理系统`
  } else {
    document.title = '实验数据管理系统'
  }
  
  // 如果是登录页面，直接放行
  if (to.path === '/login') {
    // 如果已登录且访问登录页，重定向到首页
    if (authStore.isLoggedIn) {
      next('/dashboard')
      return
    }
    next()
    return
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    // 检查是否需要初始化认证状态
    const storedToken = localStorage.getItem('token')
    const storedIsLoggedIn = localStorage.getItem('isLoggedIn')
    
    // 如果有存储的认证信息但当前状态未初始化，需要先初始化
    if (storedToken && storedIsLoggedIn === 'true' && !authStore.isLoggedIn) {
      try {
        // 等待认证状态初始化完成
        await authStore.initAuth()
        
        // 初始化成功后，继续检查认证状态
        if (!authStore.isLoggedIn) {
          // 初始化后仍未登录，重定向到登录页
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
      } catch (error) {
        console.error('认证状态初始化失败:', error)
        // 初始化失败，重定向到登录页
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
        return
      }
    } else if (!authStore.isLoggedIn) {
      // 没有存储的认证信息或认证状态为未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 检查权限
    if (to.meta.module) {
      // 检查管理员权限
      if (to.meta.adminOnly && !authStore.isAdmin) {
        next('/dashboard')
        return
      }
      
      // 检查模块权限（非管理员需要检查）
      if (!authStore.isAdmin && !authStore.hasAnyPermission(to.meta.module as string)) {
        next('/dashboard')
        return
      }
    }
  }
  
  next()
})

export default router