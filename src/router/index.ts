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
          icon: 'Collection'
        }
      },
      {
        path: 'persons',
        name: 'PersonManagement',
        component: PersonManagement,
        meta: {
          title: '人员管理',
          icon: 'User'
        }
      },
      {
        path: 'experiments',
        name: 'ExperimentManagement',
        component: ExperimentManagement,
        meta: {
          title: '实验管理',
          icon: 'DataAnalysis'
        }
      },
      {
        path: 'competitor-data',
        name: 'CompetitorData',
        component: CompetitorData,
        meta: {
          title: '竞品数据',
          icon: 'Files'
        }
      },
      {
        path: 'finger-blood-data',
        name: 'FingerBloodData',
        component: FingerBloodData,
        meta: {
          title: '指尖血数据',
          icon: 'TrendCharts'
        }
      },
      {
        path: 'sensors',
        name: 'SensorManagement',
        component: SensorManagement,
        meta: {
          title: '传感器管理',
          icon: 'Monitor'
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
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 实验数据管理系统`
  } else {
    document.title = '实验数据管理系统'
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    if (!authStore.isLoggedIn) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  } else {
    // 如果已登录且访问登录页，重定向到首页
    if (authStore.isLoggedIn && to.path === '/login') {
      next('/dashboard')
      return
    }
  }
  
  next()
})

export default router