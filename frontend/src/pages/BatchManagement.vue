<template>
  <div class="batch-management">
    <div class="page-header">
      <h2>批次管理</h2>
      <p>管理实验批次信息</p>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchText"
          placeholder="搜索批次号"
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
        <el-button 
          :disabled="!authStore.hasModulePermission('batch_management', 'read')"
          @click="handleExport"
        >
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button 
          :disabled="!authStore.hasModulePermission('batch_management', 'write')"
          type="primary" 
          @click="handleAdd"
        >
          <el-icon><Plus /></el-icon>
          新建批次
        </el-button>
      </div>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table
        :data="paginatedBatches"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="batch_id" label="批次ID" width="100" />
        <el-table-column prop="batch_number" label="批次号" min-width="150">
          <template #default="{ row }">
            <el-tag type="primary" size="small">
              {{ row.batch_number }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" min-width="180" />
        <el-table-column prop="end_time" label="结束时间" min-width="180">
          <template #default="{ row }">
            {{ row.end_time || getBatchStatus(row).label }}
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getBatchStatus(row).type">
              {{ getBatchStatus(row).label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              :disabled="!authStore.hasModulePermission('batch_management', 'write')"
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              :disabled="!authStore.hasModulePermission('batch_management', 'delete')"
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页组件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="pageSizes"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑批次' : '新建批次'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="批次号" prop="batch_number">
          <el-input
            v-model="form.batch_number"
            placeholder="请输入批次号"
          />
        </el-form-item>
        
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            placeholder="选择结束时间（可选）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
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
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search, Plus, Download } from '@element-plus/icons-vue'
import { usePagination } from '../composables/usePagination'
import { useSearch } from '../composables/useFilter'
import { exportToExcel } from '../utils/excel'
import { useDataStore, type Batch } from '../stores/data'
import { ApiService } from '../services/api'
import { useAuthStore } from '../stores/auth'

const dataStore = useDataStore()
const authStore = useAuthStore()

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    const batchesData = await ApiService.getBatches()
    dataStore.batches = batchesData
  } catch (error) {
    console.error('Failed to load batches:', error)
    ElMessage.error('加载批次数据失败')
  } finally {
    loading.value = false
  }
})

const loading = ref(false)
const { searchKeyword: searchText } = useSearch()
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  batch_id: 0,
  batch_number: '',
  start_time: '',
  end_time: ''
})

const rules = {
  batch_number: [
    { required: true, message: '请输入批次号', trigger: 'blur' },
    { min: 3, max: 50, message: '批次号长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ]
}

// 获取批次状态
const getBatchStatus = (batch: Batch) => {
  const now = new Date().getTime()
  const startTime = new Date(batch.start_time).getTime()
  const endTime = batch.end_time ? new Date(batch.end_time).getTime() : null
  
  if (now < startTime) {
    return { type: 'warning', label: '未开始' }
  } else if (endTime && now > endTime) {
    return { type: 'info', label: '已结束' }
  } else {
    return { type: 'success', label: '进行中' }
  }
}

// 过滤后的批次列表
const filteredBatches = computed(() => {
  let result = dataStore.batches
  
  if (searchText.value) {
    result = result.filter(batch => 
      batch.batch_number.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }
  
  // 按批次ID倒序排列，最新创建的在前面
  return result.sort((a, b) => b.batch_id - a.batch_id)
})

// 分页逻辑
const {
  currentPage,
  pageSize,
  pageSizes,
  total,
  handleSizeChange,
  handleCurrentChange,
  resetPagination
} = usePagination()

// 分页数据计算
const paginatedBatches = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBatches.value.slice(start, end)
})

// 监听过滤结果变化，更新总数
watch(filteredBatches, (newVal) => {
  total.value = newVal.length
}, { immediate: true })

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
  resetPagination()
}

// 导出数据
const handleExport = () => {
  try {
    // 准备导出数据
    const exportData = filteredBatches.value.map(batch => ({
      '批次ID': batch.batch_id,
      '批次号': batch.batch_number,
      '开始时间': batch.start_time,
      '结束时间': batch.end_time || '进行中',
      '状态': getBatchStatus(batch).label
    }))
    
    const success = exportToExcel(exportData, '批次数据导出', '批次数据')
    if (success) {
      ElMessage.success('导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 新建批次
const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
  resetForm()
}

// 编辑批次
const handleEdit = (row: Batch) => {
  isEdit.value = true
  dialogVisible.value = true
  Object.assign(form, row)
}

// 删除批次
const handleDelete = async (row: Batch) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除批次 "${row.batch_number}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await dataStore.deleteBatch(row.batch_id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          // 编辑
          await dataStore.updateBatch(form.batch_id, {
            batch_number: form.batch_number,
            start_time: form.start_time,
            end_time: form.end_time || undefined
          })
          ElMessage.success('更新成功')
        } else {
          // 新建
          await dataStore.addBatch({
            batch_number: form.batch_number,
            start_time: form.start_time,
            end_time: form.end_time || undefined
          })
          ElMessage.success('创建成功')
        }
        
        dialogVisible.value = false
        resetForm()
      } catch (error) {
        console.error('Submit failed:', error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    batch_id: 0,
    batch_number: '',
    start_time: '',
    end_time: ''
  })
}
</script>

<style scoped>
.batch-management {
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

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
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
</style>