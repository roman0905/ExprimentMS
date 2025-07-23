<template>
  <div class="person-management">
    <div class="page-header">
      <h2>人员管理</h2>
      <p>管理受试人员信息</p>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchText"
          placeholder="搜索人员姓名"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="toolbar-right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新建人员
        </el-button>
      </div>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table
        :data="filteredPersons"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="person_id" label="人员ID" width="100" />
        <el-table-column prop="person_name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag
              :type="row.gender === 'Male' ? 'primary' : row.gender === 'Female' ? 'danger' : 'info'"
              size="small"
            >
              {{ genderMap[row.gender] || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80">
          <template #default="{ row }">
            {{ row.age || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="height_cm" label="身高(cm)" width="100">
          <template #default="{ row }">
            {{ row.height_cm || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="weight_kg" label="体重(kg)" width="100">
          <template #default="{ row }">
            {{ row.weight_kg || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="BMI" width="80">
          <template #default="{ row }">
            {{ calculateBMI(row.height_cm, row.weight_kg) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑人员' : '新建人员'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="姓名" prop="person_name">
          <el-input
            v-model="form.person_name"
            placeholder="请输入姓名"
          />
        </el-form-item>
        
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio value="Male">男</el-radio>
            <el-radio value="Female">女</el-radio>
            <el-radio value="Other">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="年龄" prop="age">
          <el-input-number
            v-model="form.age"
            :min="1"
            :max="120"
            placeholder="请输入年龄"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="身高(cm)" prop="height_cm">
          <el-input-number
            v-model="form.height_cm"
            :min="50"
            :max="250"
            :precision="1"
            placeholder="请输入身高"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="体重(kg)" prop="weight_kg">
          <el-input-number
            v-model="form.weight_kg"
            :min="10"
            :max="300"
            :precision="1"
            placeholder="请输入体重"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { useDataStore, type Person } from '../stores/data'
import { ApiService } from '../services/api'

const dataStore = useDataStore()

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    const personsData = await ApiService.getPersons()
    dataStore.persons = personsData
  } catch (error) {
    console.error('Failed to load persons:', error)
    ElMessage.error('加载人员数据失败')
  } finally {
    loading.value = false
  }
})

const loading = ref(false)
const searchText = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  person_id: 0,
  person_name: '',
  gender: 'Male' as 'Male' | 'Female' | 'Other',
  age: undefined as number | undefined,
  height_cm: undefined as number | undefined,
  weight_kg: undefined as number | undefined
})

const genderMap = {
  Male: '男',
  Female: '女',
  Other: '其他'
}

const rules = {
  person_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ]
}

// 过滤后的人员列表
const filteredPersons = computed(() => {
  if (!searchText.value) {
    return dataStore.persons
  }
  return dataStore.persons.filter(person => 
    person.person_name.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 计算BMI
const calculateBMI = (height?: number, weight?: number): string => {
  if (!height || !weight) return '-'
  const heightInM = height / 100
  const bmi = weight / (heightInM * heightInM)
  return bmi.toFixed(1)
}

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

// 新建人员
const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
  resetForm()
}

// 编辑人员
const handleEdit = (row: Person) => {
  isEdit.value = true
  dialogVisible.value = true
  Object.assign(form, row)
}

// 删除人员
const handleDelete = async (row: Person) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除人员 "${row.person_name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    dataStore.deletePerson(row.person_id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消删除
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      if (isEdit.value) {
        // 编辑
        dataStore.updatePerson(form.person_id, {
          person_name: form.person_name,
          gender: form.gender,
          age: form.age,
          height_cm: form.height_cm,
          weight_kg: form.weight_kg
        })
        ElMessage.success('更新成功')
      } else {
        // 新建
        dataStore.addPerson({
          person_name: form.person_name,
          gender: form.gender,
          age: form.age,
          height_cm: form.height_cm,
          weight_kg: form.weight_kg
        })
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      resetForm()
    }
  })
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    person_id: 0,
    person_name: '',
    gender: 'Male' as 'Male' | 'Female' | 'Other',
    age: undefined,
    height_cm: undefined,
    weight_kg: undefined
  })
}
</script>

<style scoped>
.person-management {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 16px;
}
</style>