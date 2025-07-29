<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-table :data="users" v-loading="loading" stripe>
      <el-table-column prop="user_id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色">
        <template #default="{ row }">
          <el-tag :type="row.role === 'Admin' ? 'danger' : 'primary'">
            {{ row.role === 'Admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="createTime" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="updateTime" label="更新时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.updateTime) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="editUser(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="managePermissions(row)">权限</el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="deleteUser(row)"
            :disabled="row.user_id === authStore.userInfo?.user_id"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog 
      :title="editingUser ? '编辑用户' : '新增用户'"
      v-model="showCreateDialog"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="password" v-if="editingUser">
          <el-input v-model="userForm.password" type="password" placeholder="留空则不修改密码" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select 
            v-model="userForm.role" 
            placeholder="请选择角色"
            :disabled="editingUser && editingUser.user_id === authStore.userInfo?.user_id && editingUser.role === 'Admin'"
          >
            <el-option label="管理员" value="Admin" />
            <el-option label="普通用户" value="User" />
          </el-select>
        </el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 权限管理对话框 -->
    <el-dialog title="权限管理" v-model="showPermissionDialog" width="600px">
      <div class="permission-header">
        <h4>为用户 "{{ selectedUser?.username }}" 分配权限</h4>
        <div v-if="selectedUser?.role === 'Admin'" class="admin-notice">
          <el-alert
            title="管理员拥有所有模块的完整权限"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      <el-table :data="permissionList" border>
        <el-table-column prop="module" label="模块" width="150">
          <template #default="{ row }">
            {{ getModuleName(row.module) }}
          </template>
        </el-table-column>
        <el-table-column label="读取" width="100" align="center">
          <template #header>
            <div class="column-header">
              <span class="column-title">读取</span>
              <div class="column-actions" v-if="selectedUser?.role !== 'Admin'">
                <el-button size="small" @click="selectAllColumn('can_read')" title="全选读取权限">全选</el-button>
                <el-button size="small" @click="clearAllColumn('can_read')" title="清空读取权限">清空</el-button>
              </div>
            </div>
          </template>
          <template #default="{ row }">
            <el-checkbox 
              v-model="row.can_read" 
              :disabled="selectedUser?.role === 'Admin'"
            />
          </template>
        </el-table-column>
        <el-table-column label="写入" width="100" align="center">
          <template #header>
            <div class="column-header">
              <span class="column-title">写入</span>
              <div class="column-actions" v-if="selectedUser?.role !== 'Admin'">
                <el-button size="small" @click="selectAllColumn('can_write')" title="全选写入权限">全选</el-button>
                <el-button size="small" @click="clearAllColumn('can_write')" title="清空写入权限">清空</el-button>
              </div>
            </div>
          </template>
          <template #default="{ row }">
            <el-checkbox 
              v-model="row.can_write" 
              :disabled="selectedUser?.role === 'Admin'"
            />
          </template>
        </el-table-column>
        <el-table-column label="删除" width="100" align="center">
          <template #header>
            <div class="column-header">
              <span class="column-title">删除</span>
              <div class="column-actions" v-if="selectedUser?.role !== 'Admin'">
                <el-button size="small" @click="selectAllColumn('can_delete')" title="全选删除权限">全选</el-button>
                <el-button size="small" @click="clearAllColumn('can_delete')" title="清空删除权限">清空</el-button>
              </div>
            </div>
          </template>
          <template #default="{ row }">
            <el-checkbox 
              v-model="row.can_delete" 
              :disabled="selectedUser?.role === 'Admin'"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" v-if="selectedUser?.role !== 'Admin'">
          <template #default="{ row }">
            <div class="row-actions">
              <el-button size="small" @click="selectAllPermissions(row)">全选</el-button>
              <el-button size="small" @click="clearAllPermissions(row)">清空</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showPermissionDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="savePermissions" 
          :loading="saving"
          v-if="selectedUser?.role !== 'Admin'"
        >
          保存权限
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

interface User {
  user_id: number
  username: string
  role: 'Admin' | 'User'
  createTime: string
  updateTime: string
}

interface Permission {
  module: string
  can_read: boolean
  can_write: boolean
  can_delete: boolean
}

const authStore = useAuthStore()

const users = ref<User[]>([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showPermissionDialog = ref(false)
const editingUser = ref<User | null>(null)
const selectedUser = ref<User | null>(null)
const userFormRef = ref<FormInstance>()

const userForm = reactive({
  username: '',
  password: '',
  role: 'User' as 'Admin' | 'User'
})

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const permissionList = ref<Permission[]>([])

const moduleNames = {
  'batch_management': '批次管理',
  'person_management': '人员管理',
  'experiment_management': '实验管理',
  'competitor_data': '竞品数据',
  'finger_blood_data': '指尖血数据',
  'sensor_data': '传感器数据'
}

const getModuleName = (module: string) => {
  return moduleNames[module as keyof typeof moduleNames] || module
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const fetchUsers = async () => {
  try {
    loading.value = true
    const response = await api.get('/api/auth/users')
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const resetUserForm = () => {
  userForm.username = ''
  userForm.password = ''
  userForm.role = 'User'
  editingUser.value = null
}

const editUser = (user: User) => {
  editingUser.value = user
  userForm.username = user.username
  userForm.password = ''
  userForm.role = user.role
  showCreateDialog.value = true
}

const saveUser = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        saving.value = true
        
        if (editingUser.value) {
          // 更新用户
          const updateData: any = {
            username: userForm.username,
            role: userForm.role
          }
          
          if (userForm.password) {
            updateData.password = userForm.password
          }
          
          await api.put(`/api/auth/users/${editingUser.value.user_id}`, updateData)
          ElMessage.success('用户更新成功')
        } else {
          // 创建用户
          await api.post('/api/auth/users', userForm)
          ElMessage.success('用户创建成功')
        }
        
        showCreateDialog.value = false
        resetUserForm()
        await fetchUsers()
      } catch (error: any) {
        console.error('保存用户失败:', error)
        const message = error.response?.data?.detail || '保存用户失败'
        ElMessage.error(message)
      } finally {
        saving.value = false
      }
    }
  })
}

const deleteUser = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/api/auth/users/${user.user_id}`)
    ElMessage.success('用户删除成功')
    await fetchUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      const message = error.response?.data?.detail || '删除用户失败'
      ElMessage.error(message)
    }
  }
}

const managePermissions = async (user: User) => {
  selectedUser.value = user
  
  try {
    if (user.role === 'Admin') {
      // 管理员显示所有权限为true
      permissionList.value = Object.keys(moduleNames).map(module => ({
        module,
        can_read: true,
        can_write: true,
        can_delete: true
      }))
    } else {
      // 普通用户获取实际权限
      const response = await api.get(`/api/auth/users/${user.user_id}/permissions`)
      const userPermissions = response.data
      
      // 初始化所有模块权限
      permissionList.value = Object.keys(moduleNames).map(module => {
        const existingPermission = userPermissions.find((p: any) => p.module === module)
        return {
          module,
          can_read: existingPermission?.can_read || false,
          can_write: existingPermission?.can_write || false,
          can_delete: existingPermission?.can_delete || false
        }
      })
    }
    
    showPermissionDialog.value = true
  } catch (error) {
    console.error('获取用户权限失败:', error)
    ElMessage.error('获取用户权限失败')
  }
}

const selectAllPermissions = (permission: Permission) => {
  permission.can_read = true
  permission.can_write = true
  permission.can_delete = true
}

const clearAllPermissions = (permission: Permission) => {
  permission.can_read = false
  permission.can_write = false
  permission.can_delete = false
}

// 列全选功能
const selectAllColumn = (columnType: 'can_read' | 'can_write' | 'can_delete') => {
  permissionList.value.forEach(permission => {
    permission[columnType] = true
  })
}

// 列清空功能
const clearAllColumn = (columnType: 'can_read' | 'can_write' | 'can_delete') => {
  permissionList.value.forEach(permission => {
    permission[columnType] = false
  })
}

const savePermissions = async () => {
  if (!selectedUser.value) return
  
  try {
    saving.value = true
    
    // 只发送有权限的模块
    const permissions = permissionList.value.filter(p => 
      p.can_read || p.can_write || p.can_delete
    )
    
    await api.post('/api/auth/assign-permissions', {
      user_id: selectedUser.value.user_id,
      permissions
    })
    
    ElMessage.success('权限保存成功')
    showPermissionDialog.value = false
  } catch (error: any) {
    console.error('保存权限失败:', error)
    const message = error.response?.data?.detail || '保存权限失败'
    ElMessage.error(message)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.permission-header {
  margin-bottom: 20px;
}

.permission-header h4 {
  margin: 0;
  color: #606266;
}

.admin-notice {
  margin-top: 15px;
}

.column-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.column-header .column-title {
  margin-bottom: 2px;
}

.column-title {
  font-weight: 600;
  color: #303133;
}

.column-actions {
  display: flex;
  flex-direction: row;
  gap: 4px;
  justify-content: center;
}

.column-actions .el-button {
  padding: 2px 6px;
  font-size: 11px;
  height: 22px;
  min-height: 22px;
  border-radius: 4px;
}

.row-actions {
  display: flex;
  gap: 4px;
  justify-content: center;
  align-items: center;
}

.row-actions .el-button {
  margin: 0;
}
</style>