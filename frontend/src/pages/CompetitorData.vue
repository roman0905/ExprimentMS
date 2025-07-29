<template>
  <div class="competitor-data">
    <div class="page-header">
      <h2>竞品数据管理</h2>
      <p>管理竞品文件的上传、下载和关联信息</p>
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
          @click="handleExport" 
          :loading="exporting"
          :disabled="!authStore.hasModulePermission('competitor_data', 'read')"
        >
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button 
          type="primary" 
          @click="handleUpload"
          :disabled="!authStore.hasModulePermission('competitor_data', 'write')"
        >
          <el-icon><Upload /></el-icon>
          上传文件
        </el-button>
      </div>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table
        :data="paginatedFiles"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="competitor_file_id" label="文件ID" width="100" />
        <el-table-column prop="file_path" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon class="file-icon"><Document /></el-icon>
              {{ getFileName(row) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="关联批次" width="150">
          <template #default="{ row }">
            <el-tag type="primary">
              {{ getBatchNumber(row.batch_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联人员" width="120">
          <template #default="{ row }">
            <el-tag type="success">
              {{ getPersonName(row.person_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件大小" width="100">
          <template #default="{ row }">
            {{ getFileSize(row) }}
          </template>
        </el-table-column>
        <el-table-column label="上传时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleDownload(row)"
              :disabled="!authStore.hasModulePermission('competitor_data', 'read')"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleRename(row)"
              :disabled="!authStore.hasModulePermission('competitor_data', 'write')"
            >
              <el-icon><Edit /></el-icon>
              重命名
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              :disabled="!authStore.hasModulePermission('competitor_data', 'delete')"
            >
              <el-icon><Delete /></el-icon>
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
    
    <!-- 上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传竞品文件"
      width="600px"
      @close="resetUploadForm"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="关联批次" prop="batch_id">
          <el-select
            v-model="uploadForm.batch_id"
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
            v-model="uploadForm.person_id"
            placeholder="请选择人员"
            style="width: 100%"
          >
            <el-option
              v-for="person in filteredPersonsForUpload"
              :key="person.person_id"
              :label="`${person.person_name} (ID: ${person.person_id})`"
              :value="person.person_id"
            />
          </el-select>
          <div class="form-tip">
            {{ uploadForm.batch_id ? '显示该批次下的人员' : '请先选择批次' }}
          </div>
        </el-form-item>
        
        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".xlsx,.xls,.csv,.txt,.pdf"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 xlsx/xls/csv/txt/pdf 格式文件，文件大小不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitUpload" :loading="uploading">
            确定上传
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重命名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="重命名文件"
      width="500px"
      @close="resetRenameForm"
    >
      <el-form
        ref="renameFormRef"
        :model="renameForm"
        :rules="renameRules"
        label-width="80px"
      >
        <el-form-item label="当前文件名">
          <el-input
            :value="currentFileName"
            readonly
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="新文件名" prop="newFileName">
          <el-input
            v-model="renameForm.newFileName"
            placeholder="请输入新的文件名"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitRename" :loading="renaming">
            确定重命名
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type UploadFile } from 'element-plus'
import {
  Upload,
  Download,
  Delete,
  Document,
  UploadFilled,
  Edit
} from '@element-plus/icons-vue'
import { useDataStore, type CompetitorFile } from '../stores/data'
import { useAuthStore } from '../stores/auth'
import { ApiService } from '../services/api'
import { usePagination } from '../composables/usePagination'

import { getBatchNumber, getPersonName, formatFileSize, formatDateTime } from '../utils/formatters'
import { exportToExcel } from '../utils/excel'

const dataStore = useDataStore()
const authStore = useAuthStore()

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    // 并行加载所有必要的数据
    const [competitorFilesData, batchesData, personsData] = await Promise.all([
      ApiService.getCompetitorFiles(),
      ApiService.getBatches(),
      ApiService.getPersons()
    ])
    
    dataStore.competitorFiles = competitorFilesData
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
const uploading = ref(false)
const exporting = ref(false)
const renaming = ref(false)
const uploadDialogVisible = ref(false)
const renameDialogVisible = ref(false)
const uploadFormRef = ref<FormInstance>()
const renameFormRef = ref<FormInstance>()
const uploadRef = ref()
const fileList = ref<UploadFile[]>()
const currentFileName = ref('')
const currentFileId = ref<number | null>(null)

// 筛选相关
const filterBatchId = ref<number | undefined>()
const filterPersonId = ref<number | undefined>()

// 根据竞品文件数据中实际存在的批次进行筛选
const availableBatchesForFilter = computed(() => {
  const batchIds = [...new Set(dataStore.competitorFiles.map(file => file.batch_id))]
  return dataStore.batches.filter(batch => batchIds.includes(batch.batch_id))
})

// 根据竞品文件数据中实际存在的人员进行筛选
const availablePersonsForFilter = computed(() => {
  const personIds = [...new Set(dataStore.competitorFiles.map(file => file.person_id))]
  return dataStore.persons.filter(person => personIds.includes(person.person_id))
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

const uploadForm = reactive({
  batch_id: undefined as number | undefined,
  person_id: undefined as number | undefined,
  file: null as File | null
})

const renameForm = reactive({
  newFileName: ''
})

const uploadRules = {
  batch_id: [
    { required: true, message: '请选择关联批次', trigger: 'change' }
  ],
  person_id: [
    { required: true, message: '请选择关联人员', trigger: 'change' }
  ],
  file: [
    { required: true, message: '请选择要上传的文件', trigger: 'change' }
  ]
}

const renameRules = {
  newFileName: [
    { required: true, message: '请输入新的文件名', trigger: 'blur' },
    { min: 1, max: 255, message: '文件名长度应在1-255个字符之间', trigger: 'blur' },
    {
      pattern: /^[^<>:"/\\|?*]+$/,
      message: '文件名不能包含以下字符: < > : " / \\ | ? *',
      trigger: 'blur'
    }
  ]
}

// 根据选择的批次过滤人员（上传表单）
const filteredPersonsForUpload = computed(() => {
  if (!uploadForm.batch_id) {
    return []
  }
  return dataStore.persons.filter(person => person.batch_id === uploadForm.batch_id)
})

// 监听批次选择变化，清空人员选择（上传表单）
watch(() => uploadForm.batch_id, (newBatchId, oldBatchId) => {
  if (newBatchId !== oldBatchId) {
    uploadForm.person_id = undefined
  }
})



// 过滤后的文件列表
const filteredFiles = computed(() => {
  let result = dataStore.competitorFiles
  
  if (filterBatchId.value) {
    result = result.filter(file => file.batch_id === filterBatchId.value)
  }
  
  if (filterPersonId.value) {
    result = result.filter(file => file.person_id === filterPersonId.value)
  }
  
  // 按竞品文件ID倒序排列，最新创建的在前面
  return result.sort((a, b) => b.competitor_file_id - a.competitor_file_id)
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
const paginatedFiles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFiles.value.slice(start, end)
})

// 监听过滤结果变化，更新总数
watch(filteredFiles, (newVal) => {
  total.value = newVal.length
}, { immediate: true })



// 获取文件名（优先使用后端返回的filename字段）
const getFileName = (row: CompetitorFile): string => {
  if (row.filename) return row.filename
  if (!row.file_path) return '未知文件'
  const parts = row.file_path.split(/[\/\\]/)
  return parts[parts.length - 1] || '未知文件'
}

// 获取文件大小
const getFileSize = (row: CompetitorFile): string => {
  return formatFileSize(row.file_size)
}



// 筛选处理
const handleFilter = () => {
  // 筛选逻辑已在computed中处理
  resetPagination()
}

// 上传文件
const handleUpload = () => {
  uploadDialogVisible.value = true
  resetUploadForm()
}

// 文件选择处理
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    // 检查文件大小（10MB限制）
    if (file.raw.size > 10 * 1024 * 1024) {
      ElMessage.error('文件大小不能超过 10MB')
      fileList.value = []
      uploadForm.file = null
      return
    }
    
    uploadForm.file = file.raw
    fileList.value = [file]
  }
}

// 提交上传
const handleSubmitUpload = async () => {
  if (!uploadFormRef.value) return
  
  await uploadFormRef.value.validate(async (valid) => {
    if (valid && uploadForm.file) {
      uploading.value = true
      
      try {
        // 创建FormData对象
        const formData = new FormData()
        formData.append('batch_id', uploadForm.batch_id!.toString())
        formData.append('person_id', uploadForm.person_id!.toString())
        formData.append('file', uploadForm.file!)
        
        // 调用API上传文件
        const result = await ApiService.uploadCompetitorFile(formData)
        
        // 更新本地数据 - 检查是否已存在相同记录
        const existingIndex = dataStore.competitorFiles.findIndex(
          file => file.competitor_file_id === result.competitor_file_id
        )
        
        if (existingIndex !== -1) {
          // 如果已存在，更新现有记录
          dataStore.competitorFiles[existingIndex] = result
        } else {
          // 如果不存在，添加新记录
          dataStore.competitorFiles.push(result)
        }
        
        ElMessage.success('文件上传成功')
        uploadDialogVisible.value = false
        resetUploadForm()
      } catch (error) {
        console.error('文件上传失败:', error)
        ElMessage.error('文件上传失败，请重试')
      } finally {
        uploading.value = false
      }
    }
  })
}

// 下载文件
const handleDownload = async (row: CompetitorFile) => {
  try {
    // 检查用户权限
    if (!authStore.hasModulePermission('competitor_data', 'read')) {
      ElMessage.error('无下载权限')
      return
    }
    
    const fileName = getFileName(row)
    ElMessage.info(`正在下载文件: ${fileName}`)
    
    // 调用API下载文件
    const blob = await ApiService.downloadCompetitorFile(row.competitor_file_id)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('文件下载完成')
  } catch (error) {
    console.error('文件下载失败:', error)
    // 检查是否是权限错误
    if (error.response && error.response.status === 403) {
      ElMessage.error('无下载权限')
    } else {
      ElMessage.error('文件下载失败，请重试')
    }
  }
}

// 重命名文件
const handleRename = (row: CompetitorFile) => {
  currentFileId.value = row.competitor_file_id
  currentFileName.value = getFileName(row)
  renameForm.newFileName = currentFileName.value
  renameDialogVisible.value = true
}

// 提交重命名
const handleSubmitRename = async () => {
  if (!renameFormRef.value) return
  
  await renameFormRef.value.validate(async (valid) => {
    if (valid && currentFileId.value) {
      renaming.value = true
      
      try {
        // 调用API重命名文件
        const result = await ApiService.renameCompetitorFile(currentFileId.value, renameForm.newFileName)
        
        // 更新本地数据
        const fileIndex = dataStore.competitorFiles.findIndex(f => f.competitor_file_id === currentFileId.value)
        if (fileIndex !== -1) {
          dataStore.competitorFiles[fileIndex] = result
        }
        
        ElMessage.success('文件重命名成功')
        renameDialogVisible.value = false
        resetRenameForm()
      } catch (error) {
        console.error('文件重命名失败:', error)
        ElMessage.error('文件重命名失败，请重试')
      } finally {
        renaming.value = false
      }
    }
  })
}

// 删除文件
const handleDelete = async (row: CompetitorFile) => {
  try {
    const fileName = getFileName(row)
    await ElMessageBox.confirm(
      `确定要删除文件 "${fileName}" 吗？删除后无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用 dataStore 删除文件
    await dataStore.deleteCompetitorFile(row.competitor_file_id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('文件删除失败:', error)
      ElMessage.error('文件删除失败，请重试')
    }
  }
}

// 导出数据
const handleExport = () => {
  try {
    exporting.value = true
    
    // 准备导出数据，映射字段名
    const exportData = filteredFiles.value.map(item => ({
      '文件ID': item.competitor_file_id,
      '文件名': getFileName(item),
      '关联批次': getBatchNumber(item.batch_id),
      '关联人员': getPersonName(item.person_id),
      '文件大小': getFileSize(item),
      '上传时间': formatDateTime(item.upload_time)
    }))

    // 生成文件名
    let filename = '竞品数据'
    
    // 如果有筛选条件，添加到文件名中
    if (filterBatchId.value || filterPersonId.value) {
      const filters = []
      if (filterBatchId.value) {
        const batchNumber = getBatchNumber(filterBatchId.value)
        filters.push(`批次${batchNumber}`)
      }
      if (filterPersonId.value) {
        const personName = getPersonName(filterPersonId.value).split(' ')[0]
        filters.push(`人员${personName}`)
      }
      filename = `竞品数据_${filters.join('_')}`
    }
    
    // 导出文件
    exportToExcel(exportData, filename, {
      '文件ID': 10,
      '文件名': 30,
      '关联批次': 20,
      '关联人员': 25,
      '文件大小': 15,
      '上传时间': 20
    })
    
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('数据导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

// 重置上传表单
const resetUploadForm = () => {
  if (uploadFormRef.value) {
    uploadFormRef.value.resetFields()
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  Object.assign(uploadForm, {
    batch_id: undefined,
    person_id: undefined,
    file: null
  })
  fileList.value = []
}

// 重置重命名表单
const resetRenameForm = () => {
  if (renameFormRef.value) {
    renameFormRef.value.resetFields()
  }
  Object.assign(renameForm, {
    newFileName: ''
  })
  currentFileName.value = ''
  currentFileId.value = null
}
</script>

<style scoped>
.competitor-data {
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

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #409EFF;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.upload-demo {
  width: 100%;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-upload__tip) {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}
</style>