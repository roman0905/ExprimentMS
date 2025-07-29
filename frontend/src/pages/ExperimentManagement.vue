<template>
  <div class="experiment-management">
    <div class="page-header">
      <h2>实验管理</h2>
      <p>管理实验记录和关联信息</p>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="filterBatchId"
          placeholder="筛选批次"
          clearable
          style="width: 200px; margin-right: 12px"
          @change="handleFilter"
        >
          <el-option
            v-for="batch in availableBatchesForFilter"
            :key="batch.batch_id"
            :label="batch.batch_number"
            :value="batch.batch_id"
          />
        </el-select>
        
        <el-select
          v-model="filterPersonId"
          placeholder="筛选人员"
          clearable
          style="width: 200px"
          @change="handleFilter"
        >
          <el-option
            v-for="person in filteredPersonsForFilter"
            :key="person.person_id"
            :label="`${person.person_name} (ID: ${person.person_id})`"
            :value="person.person_id"
          />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button 
          :disabled="!authStore.hasModulePermission('experiment_management', 'read')"
          @click="handleExport"
        >
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button 
          :disabled="!authStore.hasModulePermission('experiment_management', 'write')"
          type="primary" 
          @click="handleAdd"
        >
          <el-icon><Plus /></el-icon>
          新建实验
        </el-button>
      </div>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table
        :data="paginatedExperiments"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="experiment_id" label="实验ID" width="100" />
        <el-table-column label="批次号" width="150">
          <template #default="{ row }">
            <el-tag type="primary">
              {{ getBatchNumber(row.batch_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="实验成员" min-width="300">
          <template #default="{ row }">
            <div class="members-cell">
              <div v-if="row.members && row.members.length > 0" class="members-group">
                <div class="members-header">
                  <el-icon class="group-icon"><User /></el-icon>
                  <span class="member-count">{{ row.members.length }}人小组</span>
                </div>
                <div class="members-list">
                  <div 
                    v-for="(member, index) in row.members" 
                    :key="member.id"
                    class="member-item"
                  >
                    <div class="member-avatar">
                      {{ member.person_name.charAt(0) }}
                    </div>
                    <div class="member-info">
                      <span class="member-name">{{ member.person_name }}</span>
                      <span class="member-id">ID: {{ member.person_id }}</span>
                    </div>
                    <el-tag 
                      type="info" 
                      size="small"
                      class="member-role"
                    >
                      成员
                    </el-tag>
                  </div>
                </div>
              </div>
              <div v-else class="no-members">
                <el-icon><UserFilled /></el-icon>
                <span>暂无成员</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="experiment_content" label="实验内容" min-width="200">
          <template #default="{ row }">
            <div class="content-cell">
              {{ row.experiment_content || '暂无描述' }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              :disabled="!authStore.hasModulePermission('experiment_management', 'write')"
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              :disabled="!authStore.hasModulePermission('experiment_management', 'delete')"
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
      :title="isEdit ? '编辑实验' : '新建实验'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="关联批次" prop="batch_id">
          <el-select
            v-model="form.batch_id"
            placeholder="请选择批次"
            style="width: 100%"
          >
            <el-option
              v-for="batch in dataStore.batches"
              :key="batch.batch_id"
              :label="`${batch.batch_number} (${batch.start_time})`"
              :value="batch.batch_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="实验成员" prop="member_ids">
          <el-select
            v-model="form.member_ids"
            placeholder="请选择实验成员"
            multiple
            style="width: 100%"
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option
              v-for="person in filteredPersons"
              :key="person.person_id"
              :label="`${person.person_name} (ID: ${person.person_id})`"
              :value="person.person_id"
            />
          </el-select>
          <div class="form-tip">
            {{ form.batch_id ? '显示该批次下的人员' : '请先选择批次' }}
          </div>
        </el-form-item>
        
        <el-form-item label="实验内容" prop="experiment_content">
          <el-input
            v-model="form.experiment_content"
            type="textarea"
            :rows="4"
            placeholder="请输入实验内容描述"
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
import { Search, Plus, Download, User, UserFilled } from '@element-plus/icons-vue'
import { useDataStore, type Experiment } from '../stores/data'
import { ApiService } from '../services/api'
import { useAuthStore } from '../stores/auth'
import { usePagination } from '@/composables/usePagination'

import { getBatchNumber, getPersonName, formatDateTime } from '@/utils/formatters'
import { exportToExcel } from '@/utils/excel'

const dataStore = useDataStore()
const authStore = useAuthStore()

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    const [experimentsData, batchesData, personsData] = await Promise.all([
      ApiService.getExperiments(),
      ApiService.getBatches(),
      ApiService.getPersons()
    ])
    dataStore.experiments = experimentsData
    dataStore.batches = batchesData
    dataStore.persons = personsData
  } catch (error) {
    console.error('Failed to load data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
})

const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

// 分页相关
const { currentPage, pageSize, pageSizes, handleSizeChange, handleCurrentChange, resetPagination } = usePagination()

// 筛选相关
const filterBatchId = ref<number | undefined>()
const filterPersonId = ref<number | undefined>()

// 根据实验数据中实际存在的批次进行筛选
const availableBatchesForFilter = computed(() => {
  const batchIds = [...new Set(dataStore.experiments.map(exp => exp.batch_id))]
  return dataStore.batches.filter(batch => batchIds.includes(batch.batch_id))
})

// 根据实验数据中实际存在的人员进行筛选
const availablePersonsForFilter = computed(() => {
  const personIds = new Set<number>()
  dataStore.experiments.forEach(exp => {
    if (exp.members) {
      exp.members.forEach(member => personIds.add(member.person_id))
    }
  })
  return dataStore.persons.filter(person => personIds.has(person.person_id))
})

// 根据选择的批次过滤人员
const filteredPersonsForFilter = computed(() => {
  if (!filterBatchId.value) {
    return availablePersonsForFilter.value
  }
  return availablePersonsForFilter.value.filter(person => person.batch_id === filterBatchId.value)
})

// 监听批次选择变化，清空人员过滤
watch(() => filterBatchId.value, (newBatchId, oldBatchId) => {
  if (newBatchId !== oldBatchId) {
    filterPersonId.value = undefined
    resetPagination()
  }
})

const form = reactive({
  experiment_id: 0,
  batch_id: undefined as number | undefined,
  member_ids: [] as number[],
  experiment_content: ''
})

const rules = {
  batch_id: [
    { required: true, message: '请选择关联批次', trigger: 'change' }
  ],
  member_ids: [
    { required: true, message: '请至少选择一个实验成员', trigger: 'change' },
    { type: 'array', min: 1, message: '请至少选择一个实验成员', trigger: 'change' }
  ],
  experiment_content: [
    { max: 500, message: '实验内容长度不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 过滤后的实验列表
const filteredExperiments = computed(() => {
  let result = dataStore.experiments
  
  if (filterBatchId.value) {
    result = result.filter(exp => exp.batch_id === filterBatchId.value)
  }
  
  if (filterPersonId.value) {
    result = result.filter(exp => 
      exp.members && exp.members.some(member => member.person_id === filterPersonId.value)
    )
  }
  
  // 按实验ID倒序排列，最新创建的在前面
  return result.sort((a, b) => b.experiment_id - a.experiment_id)
})

// 当前页数据
const paginatedExperiments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredExperiments.value.slice(start, end)
})

// 总数据量
const total = computed(() => filteredExperiments.value.length)

// 根据选择的批次过滤人员
const filteredPersons = computed(() => {
  if (!form.batch_id) {
    return []
  }
  return dataStore.persons.filter(person => person.batch_id === form.batch_id)
})

// 监听批次选择变化，清空人员选择
watch(() => form.batch_id, (newBatchId, oldBatchId) => {
  if (newBatchId !== oldBatchId) {
    form.member_ids = []
  }
})







// 筛选处理
const handleFilter = () => {
  // 筛选逻辑已在computed中处理
  resetPagination()
}

// 导出数据
const handleExport = () => {
  try {
    // 准备导出数据
    const exportData = filteredExperiments.value.map(experiment => ({
      '实验ID': experiment.experiment_id,
      '批次号': getBatchNumber(experiment.batch_id),
      '实验成员': experiment.members?.map(m => m.person_name).join(', ') || '暂无成员',
      '成员数量': experiment.members?.length || 0,
      '实验内容': experiment.experiment_content || '暂无描述',
      '创建时间': formatDateTime(experiment.created_time)
    }))
    
    exportToExcel(exportData, '实验数据')
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败，请重试')
  }
}

// 新建实验
const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
  resetForm()
}

// 编辑实验
const handleEdit = (row: Experiment) => {
  isEdit.value = true
  dialogVisible.value = true
  
  // 正确处理表单数据，特别是member_ids字段
  Object.assign(form, {
    experiment_id: row.experiment_id,
    batch_id: row.batch_id,
    experiment_content: row.experiment_content || '',
    // 从members数组中提取person_id作为member_ids
    member_ids: row.members ? row.members.map(member => member.person_id) : (row.member_ids || [])
  })
}

// 删除实验
const handleDelete = async (row: Experiment) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除实验记录 "${row.experiment_id}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await ApiService.deleteExperiment(row.experiment_id)
    
    // 重新加载数据
    const experimentsData = await ApiService.getExperiments()
    dataStore.experiments = experimentsData
    
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
      ElMessage.error('删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        
        if (isEdit.value) {
          // 编辑
          await ApiService.updateExperiment(form.experiment_id, {
            batch_id: form.batch_id!,
            member_ids: form.member_ids,
            experiment_content: form.experiment_content
          })
          ElMessage.success('更新成功')
        } else {
          // 新建
          await ApiService.createExperiment({
            batch_id: form.batch_id!,
            member_ids: form.member_ids,
            experiment_content: form.experiment_content
          })
          ElMessage.success('创建成功')
        }
        
        // 重新加载数据
        const experimentsData = await ApiService.getExperiments()
        dataStore.experiments = experimentsData
        
        dialogVisible.value = false
        resetForm()
      } catch (error) {
        console.error('Submit failed:', error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        loading.value = false
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
    experiment_id: 0,
    batch_id: undefined,
    member_ids: [],
    experiment_content: ''
  })
}
</script>

<style scoped>
.experiment-management {
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

.content-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

:deep(.el-select) {
  width: 100%;
}

.members-cell {
  padding: 8px 0;
}

.members-group {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e4e7ed;
}

.members-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e4e7ed;
}

.group-icon {
  color: #409eff;
  margin-right: 6px;
  font-size: 16px;
}

.member-count {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-item {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  transition: all 0.2s ease;
}

.member-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
}

.member-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-right: 10px;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.member-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  line-height: 1.2;
}

.member-id {
  font-size: 11px;
  color: #909399;
  line-height: 1.2;
  margin-top: 2px;
}

.member-role {
  margin-left: 8px;
  flex-shrink: 0;
}

.no-members {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #c0c4cc;
  font-size: 13px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px dashed #e4e7ed;
}

.no-members .el-icon {
  margin-right: 6px;
  font-size: 16px;
}

.form-tip {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
  line-height: 1.4;
}
</style>