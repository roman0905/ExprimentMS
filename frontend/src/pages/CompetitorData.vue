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
        <el-button type="primary" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          上传文件
        </el-button>
      </div>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table
        :data="filteredFiles"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="competitor_file_id" label="文件ID" width="100" />
        <el-table-column prop="file_name" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon class="file-icon"><Document /></el-icon>
              {{ row.file_name }}
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
            {{ getFileSize(row.file_name) }}
          </template>
        </el-table-column>
        <el-table-column label="上传时间" width="180">
          <template #default="{ row }">
            {{ getUploadTime(row.competitor_file_id) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleDownload(row)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
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
              v-for="person in dataStore.persons"
              :key="person.person_id"
              :label="`${person.person_name} (${person.gender === 'Male' ? '男' : person.gender === 'Female' ? '女' : '其他'})`"
              :value="person.person_id"
            />
          </el-select>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type UploadFile } from 'element-plus'
import {
  Upload,
  Download,
  Delete,
  Document,
  UploadFilled
} from '@element-plus/icons-vue'
import { useDataStore, type CompetitorFile } from '../stores/data'

const dataStore = useDataStore()

const loading = ref(false)
const uploading = ref(false)
const filterBatchId = ref<number | undefined>()
const filterPersonId = ref<number | undefined>()
const uploadDialogVisible = ref(false)
const uploadFormRef = ref<FormInstance>()
const uploadRef = ref()
const fileList = ref<UploadFile[]>([])

const uploadForm = reactive({
  batch_id: undefined as number | undefined,
  person_id: undefined as number | undefined,
  file: null as File | null
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

// 过滤后的文件列表
const filteredFiles = computed(() => {
  let result = dataStore.competitorFiles
  
  if (filterBatchId.value) {
    result = result.filter(file => file.batch_id === filterBatchId.value)
  }
  
  if (filterPersonId.value) {
    result = result.filter(file => file.person_id === filterPersonId.value)
  }
  
  return result
})

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

// 模拟获取文件大小
const getFileSize = (fileName: string): string => {
  // 模拟文件大小
  const sizes = ['1.2MB', '856KB', '2.1MB', '654KB', '3.4MB']
  const hash = fileName.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0)
  return sizes[Math.abs(hash) % sizes.length]
}

// 模拟获取上传时间
const getUploadTime = (fileId: number): string => {
  // 模拟上传时间
  const baseTime = new Date('2024-01-01 10:00:00').getTime()
  const uploadTime = new Date(baseTime + fileId * 3600000)
  return uploadTime.toLocaleString('zh-CN')
}

// 筛选处理
const handleFilter = () => {
  // 筛选逻辑已在computed中处理
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
  
  await uploadFormRef.value.validate((valid) => {
    if (valid && uploadForm.file) {
      uploading.value = true
      
      // 模拟上传过程
      setTimeout(() => {
        dataStore.addCompetitorFile({
          batch_id: uploadForm.batch_id!,
          person_id: uploadForm.person_id!,
          file_name: uploadForm.file!.name
        })
        
        ElMessage.success('文件上传成功')
        uploadDialogVisible.value = false
        resetUploadForm()
        uploading.value = false
      }, 2000)
    }
  })
}

// 下载文件
const handleDownload = (row: CompetitorFile) => {
  // 模拟文件下载
  ElMessage.info(`正在下载文件: ${row.file_name}`)
  
  // 实际项目中这里应该调用下载API
  setTimeout(() => {
    ElMessage.success('文件下载完成')
  }, 1000)
}

// 删除文件
const handleDelete = async (row: CompetitorFile) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${row.file_name}" 吗？删除后无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    dataStore.deleteCompetitorFile(row.competitor_file_id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消删除
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