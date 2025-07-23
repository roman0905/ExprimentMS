<template>
  <div class="sensor-management">
    <div class="page-header">
      <h2>传感器管理</h2>
      <p>管理实验中使用的各类传感器设备</p>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索传感器名称或型号"
          style="width: 250px; margin-right: 12px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="filterType"
          placeholder="筛选类型"
          clearable
          style="width: 150px; margin-right: 12px"
          @change="handleFilter"
        >
          <el-option label="温度传感器" value="Temperature" />
          <el-option label="湿度传感器" value="Humidity" />
          <el-option label="压力传感器" value="Pressure" />
          <el-option label="光照传感器" value="Light" />
          <el-option label="运动传感器" value="Motion" />
          <el-option label="心率传感器" value="HeartRate" />
          <el-option label="其他" value="Other" />
        </el-select>
        
        <el-select
          v-model="filterStatus"
          placeholder="筛选状态"
          clearable
          style="width: 120px"
          @change="handleFilter"
        >
          <el-option label="正常" value="Normal" />
          <el-option label="维护中" value="Maintenance" />
          <el-option label="故障" value="Fault" />
          <el-option label="停用" value="Disabled" />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加传感器
        </el-button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ totalSensors }}</div>
          <div class="stat-label">传感器总数</div>
        </div>
        <div class="stat-icon total">
          <el-icon><Monitor /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ normalSensors }}</div>
          <div class="stat-label">正常运行</div>
        </div>
        <div class="stat-icon normal">
          <el-icon><CircleCheck /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ maintenanceSensors }}</div>
          <div class="stat-label">维护中</div>
        </div>
        <div class="stat-icon maintenance">
          <el-icon><Tools /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ faultSensors }}</div>
          <div class="stat-label">故障设备</div>
        </div>
        <div class="stat-icon fault">
          <el-icon><CircleClose /></el-icon>
        </div>
      </el-card>
    </div>
    
    <!-- 传感器列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>传感器列表</span>
          <span class="data-count">共 {{ filteredSensors.length }} 个传感器</span>
        </div>
      </template>
      
      <el-table
        :data="filteredSensors"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="sensor_id" label="传感器ID" width="100" />
        <el-table-column prop="sensor_name" label="传感器名称" width="180" />
        <el-table-column prop="sensor_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getSensorTypeColor(row.sensor_type)">
              {{ getSensorTypeLabel(row.sensor_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="型号" width="150" />
        <el-table-column prop="manufacturer" label="制造商" width="120" />
        <el-table-column prop="installation_date" label="安装日期" width="120" />
        <el-table-column prop="last_maintenance" label="最后维护" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleMaintenance(row)"
              :disabled="row.status === 'Maintenance'"
            >
              维护
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
      :title="isEdit ? '编辑传感器' : '添加传感器'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="传感器名称" prop="sensor_name">
              <el-input
                v-model="form.sensor_name"
                placeholder="请输入传感器名称"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="传感器类型" prop="sensor_type">
              <el-select
                v-model="form.sensor_type"
                placeholder="请选择类型"
                style="width: 100%"
              >
                <el-option label="温度传感器" value="Temperature" />
                <el-option label="湿度传感器" value="Humidity" />
                <el-option label="压力传感器" value="Pressure" />
                <el-option label="光照传感器" value="Light" />
                <el-option label="运动传感器" value="Motion" />
                <el-option label="心率传感器" value="HeartRate" />
                <el-option label="其他" value="Other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号" prop="model">
              <el-input
                v-model="form.model"
                placeholder="请输入型号"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="制造商" prop="manufacturer">
              <el-input
                v-model="form.manufacturer"
                placeholder="请输入制造商"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="安装日期" prop="installation_date">
              <el-date-picker
                v-model="form.installation_date"
                type="date"
                placeholder="选择安装日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select
                v-model="form.status"
                placeholder="请选择状态"
                style="width: 100%"
              >
                <el-option label="正常" value="Normal" />
                <el-option label="维护中" value="Maintenance" />
                <el-option label="故障" value="Fault" />
                <el-option label="停用" value="Disabled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="位置" prop="location">
          <el-input
            v-model="form.location"
            placeholder="请输入传感器位置"
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入传感器描述信息"
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
    
    <!-- 维护记录对话框 -->
    <el-dialog
      v-model="maintenanceDialogVisible"
      title="传感器维护"
      width="500px"
    >
      <el-form
        ref="maintenanceFormRef"
        :model="maintenanceForm"
        :rules="maintenanceRules"
        label-width="120px"
      >
        <el-form-item label="维护类型" prop="maintenance_type">
          <el-select
            v-model="maintenanceForm.maintenance_type"
            placeholder="请选择维护类型"
            style="width: 100%"
          >
            <el-option label="定期保养" value="Regular" />
            <el-option label="故障维修" value="Repair" />
            <el-option label="校准调试" value="Calibration" />
            <el-option label="清洁保养" value="Cleaning" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="维护日期" prop="maintenance_date">
          <el-date-picker
            v-model="maintenanceForm.maintenance_date"
            type="date"
            placeholder="选择维护日期"
            style="width: 100%"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="维护说明" prop="maintenance_notes">
          <el-input
            v-model="maintenanceForm.maintenance_notes"
            type="textarea"
            :rows="4"
            placeholder="请输入维护说明"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="maintenanceDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleMaintenanceSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import {
  Search,
  Download,
  Plus,
  Monitor,
  CircleCheck,
  Tools,
  CircleClose
} from '@element-plus/icons-vue'
import { useDataStore, type Sensor } from '../stores/data'
import { ApiService } from '../services/api'

const dataStore = useDataStore()

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    const sensorsData = await ApiService.getSensors()
    dataStore.sensors = sensorsData
  } catch (error) {
    console.error('Failed to load sensors:', error)
    ElMessage.error('加载传感器数据失败')
  } finally {
    loading.value = false
  }
})

const loading = ref(false)
const searchKeyword = ref('')
const filterType = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const maintenanceDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const maintenanceFormRef = ref<FormInstance>()
const currentSensor = ref<Sensor | null>(null)

const form = reactive({
  sensor_id: 0,
  sensor_name: '',
  sensor_type: '',
  model: '',
  manufacturer: '',
  installation_date: '',
  last_maintenance: '',
  status: 'Normal',
  location: '',
  description: ''
})

const maintenanceForm = reactive({
  maintenance_type: '',
  maintenance_date: '',
  maintenance_notes: ''
})

const rules = {
  sensor_name: [
    { required: true, message: '请输入传感器名称', trigger: 'blur' }
  ],
  sensor_type: [
    { required: true, message: '请选择传感器类型', trigger: 'change' }
  ],
  model: [
    { required: true, message: '请输入型号', trigger: 'blur' }
  ],
  manufacturer: [
    { required: true, message: '请输入制造商', trigger: 'blur' }
  ],
  installation_date: [
    { required: true, message: '请选择安装日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  location: [
    { required: true, message: '请输入位置', trigger: 'blur' }
  ]
}

const maintenanceRules = {
  maintenance_type: [
    { required: true, message: '请选择维护类型', trigger: 'change' }
  ],
  maintenance_date: [
    { required: true, message: '请选择维护日期', trigger: 'change' }
  ],
  maintenance_notes: [
    { required: true, message: '请输入维护说明', trigger: 'blur' }
  ]
}

// 过滤后的传感器列表
const filteredSensors = computed(() => {
  let result = dataStore.sensors
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(sensor => 
      sensor.sensor_name.toLowerCase().includes(keyword) ||
      sensor.model.toLowerCase().includes(keyword)
    )
  }
  
  if (filterType.value) {
    result = result.filter(sensor => sensor.sensor_type === filterType.value)
  }
  
  if (filterStatus.value) {
    result = result.filter(sensor => sensor.status === filterStatus.value)
  }
  
  return result
})

// 统计数据
const totalSensors = computed(() => dataStore.sensors.length)
const normalSensors = computed(() => dataStore.sensors.filter(s => s.status === 'Normal').length)
const maintenanceSensors = computed(() => dataStore.sensors.filter(s => s.status === 'Maintenance').length)
const faultSensors = computed(() => dataStore.sensors.filter(s => s.status === 'Fault').length)

// 获取传感器类型颜色
const getSensorTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    Temperature: 'danger',
    Humidity: 'primary',
    Pressure: 'warning',
    Light: 'success',
    Motion: 'info',
    HeartRate: 'danger',
    Other: ''
  }
  return colors[type] || ''
}

// 获取传感器类型标签
const getSensorTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    Temperature: '温度传感器',
    Humidity: '湿度传感器',
    Pressure: '压力传感器',
    Light: '光照传感器',
    Motion: '运动传感器',
    HeartRate: '心率传感器',
    Other: '其他'
  }
  return labels[type] || type
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    Normal: 'success',
    Maintenance: 'warning',
    Fault: 'danger',
    Disabled: 'info'
  }
  return colors[status] || ''
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    Normal: '正常',
    Maintenance: '维护中',
    Fault: '故障',
    Disabled: '停用'
  }
  return labels[status] || status
}

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

// 筛选处理
const handleFilter = () => {
  // 筛选逻辑已在computed中处理
}

// 导出数据
const handleExport = () => {
  ElMessage.info('导出功能开发中...')
}

// 新建传感器
const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
  resetForm()
}

// 编辑传感器
const handleEdit = (row: Sensor) => {
  isEdit.value = true
  dialogVisible.value = true
  Object.assign(form, row)
}

// 维护传感器
const handleMaintenance = (row: Sensor) => {
  currentSensor.value = row
  maintenanceDialogVisible.value = true
  resetMaintenanceForm()
}

// 删除传感器
const handleDelete = async (row: Sensor) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除传感器 "${row.sensor_name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    dataStore.deleteSensor(row.sensor_id)
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
        dataStore.updateSensor(form.sensor_id, {
          sensor_name: form.sensor_name,
          sensor_type: form.sensor_type,
          model: form.model,
          manufacturer: form.manufacturer,
          installation_date: form.installation_date,
          last_maintenance: form.last_maintenance,
          status: form.status,
          location: form.location,
          description: form.description
        })
        ElMessage.success('更新成功')
      } else {
        // 新建
        dataStore.addSensor({
          sensor_name: form.sensor_name,
          sensor_type: form.sensor_type,
          model: form.model,
          manufacturer: form.manufacturer,
          installation_date: form.installation_date,
          last_maintenance: '',
          status: form.status,
          location: form.location,
          description: form.description
        })
        ElMessage.success('添加成功')
      }
      
      dialogVisible.value = false
      resetForm()
    }
  })
}

// 提交维护表单
const handleMaintenanceSubmit = async () => {
  if (!maintenanceFormRef.value || !currentSensor.value) return
  
  await maintenanceFormRef.value.validate((valid) => {
    if (valid) {
      // 更新传感器的最后维护时间和状态
      dataStore.updateSensor(currentSensor.value!.sensor_id, {
        ...currentSensor.value!,
        last_maintenance: maintenanceForm.maintenance_date,
        status: 'Normal' // 维护后状态设为正常
      })
      
      ElMessage.success('维护记录已保存')
      maintenanceDialogVisible.value = false
      resetMaintenanceForm()
    }
  })
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    sensor_id: 0,
    sensor_name: '',
    sensor_type: '',
    model: '',
    manufacturer: '',
    installation_date: '',
    last_maintenance: '',
    status: 'Normal',
    location: '',
    description: ''
  })
}

// 重置维护表单
const resetMaintenanceForm = () => {
  if (maintenanceFormRef.value) {
    maintenanceFormRef.value.resetFields()
  }
  Object.assign(maintenanceForm, {
    maintenance_type: '',
    maintenance_date: '',
    maintenance_notes: ''
  })
}
</script>

<style scoped>
.sensor-management {
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
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.normal {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
}

.stat-icon.maintenance {
  background: linear-gradient(135deg, #E6A23C 0%, #f0c78a 100%);
}

.stat-icon.fault {
  background: linear-gradient(135deg, #F56C6C 0%, #f89898 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.data-count {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
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

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left {
    justify-content: center;
  }
  
  .toolbar-right {
    justify-content: center;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>