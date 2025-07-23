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
            v-for="batch in dataStore.batches"
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
            v-for="person in dataStore.persons"
            :key="person.person_id"
            :label="person.person_name"
            :value="person.person_id"
          />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button type="primary" @click="handleAdd">
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
        <el-table-column label="人员姓名" width="120">
          <template #default="{ row }">
            <el-tag type="success">
              {{ getPersonName(row.person_id) }}
            </el-tag>
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
        
        <el-form-item label="关联人员" prop="person_id">
          <el-select
            v-model="form.person_id"
            placeholder="请选择人员"
            style="width: 100%"
          >
            <el-option
              v-for="person in dataStore.persons"
              :key="person.person_id"
              :label="`${person.person_name} (ID: ${person.person_id})`"
              :value="person.person_id"
            />
          </el-select>
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
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search, Plus, Download } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { useDataStore, type Experiment } from '../stores/data'
import { ApiService } from '../services/api'

const dataStore = useDataStore()

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    const experimentsData = await ApiService.getExperiments()
    dataStore.experiments = experimentsData
  } catch (error) {
    console.error('Failed to load experiments:', error)
    ElMessage.error('加载实验数据失败')
  } finally {
    loading.value = false
  }
})

const loading = ref(false)
const filterBatchId = ref<number | undefined>()
const filterPersonId = ref<number | undefined>()
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizes = [10, 20, 50, 100]

const form = reactive({
  experiment_id: 0,
  batch_id: undefined as number | undefined,
  person_id: undefined as number | undefined,
  experiment_content: ''
})

const rules = {
  batch_id: [
    { required: true, message: '请选择关联批次', trigger: 'change' }
  ],
  person_id: [
    { required: true, message: '请选择关联人员', trigger: 'change' }
  ],
  experiment_content: [
    { required: true, message: '请输入实验内容', trigger: 'blur' },
    { min: 5, max: 500, message: '实验内容长度在 5 到 500 个字符', trigger: 'blur' }
  ]
}

// 过滤后的实验列表
const filteredExperiments = computed(() => {
  let result = dataStore.experiments
  
  if (filterBatchId.value) {
    result = result.filter(exp => exp.batch_id === filterBatchId.value)
  }
  
  if (filterPersonId.value) {
    result = result.filter(exp => exp.person_id === filterPersonId.value)
  }
  
  return result
})

// 当前页数据
const paginatedExperiments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredExperiments.value.slice(start, end)
})

// 总数据量
const total = computed(() => filteredExperiments.value.length)

// 获取批次号
const getBatchNumber = (batchId: number): string => {
  const batch = dataStore.batches.find(b => b.batch_id === batchId)
  return batch?.batch_number || '未知批次'
}

// 获取人员姓名
const getPersonName = (personId: number): string => {
  const person = dataStore.persons.find(p => p.person_id === personId)
  return person?.person_name || '未知人员'
}

// 分页事件处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

// 重置分页到第一页
const resetPagination = () => {
  currentPage.value = 1
}

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
      '人员姓名': getPersonName(experiment.person_id),
      '实验内容': experiment.experiment_content || '暂无描述'
    }))
    
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(exportData)
    
    // 设置列宽
    const colWidths = [
      { wch: 10 }, // 实验ID
      { wch: 15 }, // 批次号
      { wch: 15 }, // 人员姓名
      { wch: 50 }  // 实验内容
    ]
    ws['!cols'] = colWidths
    
    XLSX.utils.book_append_sheet(wb, ws, '实验数据')
    
    // 生成文件名
    const now = new Date()
    const timestamp = now.toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_')
    const filename = `实验数据_${timestamp}.xlsx`
    
    // 导出文件
    XLSX.writeFile(wb, filename)
    
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
  Object.assign(form, row)
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
    
    dataStore.deleteExperiment(row.experiment_id)
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
        dataStore.updateExperiment(form.experiment_id, {
          batch_id: form.batch_id!,
          person_id: form.person_id!,
          experiment_content: form.experiment_content
        })
        ElMessage.success('更新成功')
      } else {
        // 新建
        dataStore.addExperiment({
          batch_id: form.batch_id!,
          person_id: form.person_id!,
          experiment_content: form.experiment_content
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
    experiment_id: 0,
    batch_id: undefined,
    person_id: undefined,
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
</style>