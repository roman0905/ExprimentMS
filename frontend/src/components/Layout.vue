<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <div class="logo">
          <el-icon v-if="isCollapse" size="24"><DataAnalysis /></el-icon>
          <span v-else>实验数据管理系统</span>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :unique-opened="true"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasPermission('batch_management')"
            index="/batches"
          >
            <el-icon><Collection /></el-icon>
            <template #title>批次管理</template>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasPermission('person_management')"
            index="/persons"
          >
            <el-icon><User /></el-icon>
            <template #title>人员管理</template>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasPermission('experiment_management')"
            index="/experiments"
          >
            <el-icon><DataAnalysis /></el-icon>
            <template #title>实验管理</template>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasPermission('competitor_data')"
            index="/competitorData"
          >
            <el-icon><Files /></el-icon>
            <template #title>竞品数据</template>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasPermission('finger_blood_data')"
            index="/fingerBloodData"
          >
            <el-icon><TrendCharts /></el-icon>
            <template #title>指尖血数据</template>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasPermission('sensor_data')"
            index="/sensors"
          >
            <el-icon><Monitor /></el-icon>
            <template #title>传感器管理</template>
          </el-menu-item>
          
          <el-menu-item 
            v-if="authStore.isAdmin"
            index="/users"
          >
            <el-icon><UserFilled /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header class="header">
          <div class="header-left">
            <el-button
              link
              size="large"
              @click="toggleCollapse"
            >
              <el-icon><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
            </el-button>
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><Avatar /></el-icon>
                {{ authStore.username }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 主内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  House,
  Collection,
  User,
  UserFilled,
  FolderOpened,
  Document,
  TrendCharts,
  Monitor,
  Expand,
  Fold,
  Avatar,
  ArrowDown,
  SwitchButton,
  DataAnalysis,
  Files
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)

const activeMenu = computed(() => {
  return route.path
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const hasPermission = (module: string) => {
  return authStore.isAdmin || authStore.hasAnyPermission(module)
}

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm(
        '确定要退出登录吗？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      await authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {
      // 用户取消
    }
  }
}

onMounted(async () => {
  await authStore.initAuth()
  authStore.setupApiInterceptors()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #434a50;
}

.header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}

.user-info:hover {
  color: #409EFF;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  min-height: calc(100vh - 60px);
  overflow-y: auto;
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
}

:deep(.el-sub-menu .el-menu-item) {
  height: 40px;
  line-height: 40px;
  padding-left: 50px !important;
}
</style>