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
          placeholder="搜索传感器名称"
          style="width: 250px; margin-right: 12px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="filterBatch"
          placeholder="筛选批次"
          clearable
          style="width: 150px; margin-right: 12px"
          @change="handleFilter"
        >
          <el-option
            v-for="batch in availableBatchesForFilter"
            :key="batch.batch_id"
            :label="batch.batch_number"
            :value="batch.batch_id.toString()"
          />
        </el-select>
        
        <el-select
          v-model="filterPerson"
          placeholder="筛选人员"
          clearable
          style="width: 150px; margin-right: 12px"
          @change="handleFilter"
        >
          <el-option
            v-for="person in filteredPersonsForFilter"
            :key="person.person_id"
            :label="person.person_name"
            :value="person.person_id.toString()"
          />
        </el-select>
        
        <el-select
          v-model="filterStatus"
          placeholder="筛选状态"
          clearable
          style="width: 120px"
          @change="handleFilter"
        >
          <el-option label="未开始" value="not_started" />
          <el-option label="进行中" value="running" />
          <el-option label="已结束" value="finished" />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button 
          :disabled="!authStore.hasModulePermission('sensor_management', 'read')"
          @click="handleExport"
        >
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button 
          :disabled="!authStore.hasModulePermission('sensor_management', 'write')"
          type="primary" 
          @click="handleAdd"
        >
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
          <div class="stat-number">{{ notStartedSensors }}</div>
          <div class="stat-label">未开始</div>
        </div>
        <div class="stat-icon not-started">
          <el-icon><Clock /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ runningSensors }}</div>
          <div class="stat-label">进行中</div>
        </div>
        <div class="stat-icon running">
          <el-icon><CircleCheck /></el-icon>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ finishedSensors }}</div>
          <div class="stat-label">已结束</div>
        </div>
        <div class="stat-icon finished">
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
        :data="paginatedSensors"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="sensor_id" label="传感器ID" width="100" />
        <el-table-column prop="sensor_name" label="传感器名称" width="200" />
        <el-table-column label="关联人员" width="150">
          <template #default="{ row }">
          <el-tag type="success">
            {{ getPersonName(row.person_id) }}
          </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联批次" width="150">
          <template #default="{ row }">
           <el-tag type="primary">
            {{ getBatchNumber(row.batch_id) }}
           </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template #default="{ row }">
            {{ row.end_time ? formatDateTime(row.end_time) : getSensorStatus(row).label }}
          </template>
        </el-table-column>
        <el-table-column prop="end_reason" label="结束原因" width="150">
          <template #default="{ row }">
            <span v-if="row.end_reason" class="end-reason-text">{{ row.end_reason }}</span>
            <span v-else class="no-data">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getSensorStatus(row).type">{{ getSensorStatus(row).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              :disabled="!authStore.hasModulePermission('sensor_management', 'write')"
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              :disabled="!authStore.hasModulePermission('sensor_management', 'delete')"
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
            <el-form-item label="关联人员" prop="person_id">
              <el-select
                v-model="form.person_id"
                placeholder="请选择人员"
                style="width: 100%"
                filterable
                :disabled="isEdit"
              >
                <el-option
                  v-for="person in filteredPersonsForSensor"
                  :key="person.person_id"
                  :label="`${person.person_name} (ID: ${person.person_id})`"
                  :value="person.person_id"
                />
              </el-select>
              <div class="form-tip" v-if="!isEdit">
                {{ form.batch_id ? '显示该批次下的人员' : '请先选择批次' }}
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关联批次" prop="batch_id">
              <el-select
                v-model="form.batch_id"
                placeholder="请选择批次"
                style="width: 100%"
                filterable
                :disabled="isEdit"
              >
                <el-option
                  v-for="batch in batches"
                  :key="batch.batch_id"
                  :label="`${batch.batch_number} (ID: ${batch.batch_id})`"
                  :value="batch.batch_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
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
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                placeholder="选择结束时间（可选）"
                style="width: 100%"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束原因">
              <el-input
                v-model="form.end_reason"
                placeholder="请输入结束原因（可选）"
                maxlength="255"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>
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
import {
  Search,
  Download,
  Plus,
  Monitor,
  CircleCheck,
  CircleClose,
  Clock
} from '@element-plus/icons-vue'
import { useDataStore, type Sensor, type Person, type Batch } from '../stores/data'
import { ApiService } from '../services/api'
import { useAuthStore } from '../stores/auth'
import { usePagination } from '@/composables/usePagination'

import { formatDateTime } from '@/utils/formatters'
import { exportToExcel } from '@/utils/excel'

const dataStore = useDataStore()
const authStore = useAuthStore()

// 人员和批次数据
const persons = ref<Person[]>([])
const batches = ref<Batch[]>([])

// 本地格式化函数
const getPersonName = (personId: number): string => {
  const person = persons.value.find(p => p.person_id === personId)
  return person ? `${person.person_name} (ID: ${person.person_id})` : '未知人员'
}

const getBatchNumber = (batchId: number): string => {
  const batch = batches.value.find(b => b.batch_id === batchId)
  return batch?.batch_number || '未知批次'
}

// 根据传感器数据中实际存在的批次进行筛选
const availableBatchesForFilter = computed(() => {
  const batchIds = [...new Set(dataStore.sensors.map(sensor => sensor.batch_id))]
  return batches.value.filter(batch => batchIds.includes(batch.batch_id))
})

// 根据传感器数据中实际存在的人员进行筛选
const availablePersonsForFilter = computed(() => {
  const personIds = [...new Set(dataStore.sensors.map(sensor => sensor.person_id))]
  return persons.value.filter(person => personIds.includes(person.person_id))
})

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    const [sensorsData, personsData, batchesData] = await Promise.all([
      ApiService.getSensors(),
      ApiService.getPersons(),
      ApiService.getBatches()
    ])
    dataStore.sensors = sensorsData
    persons.value = personsData
    batches.value = batchesData
  } catch (error) {
    console.error('Failed to load data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
})

const loading = ref(false)
const searchKeyword = ref('')
const filterBatch = ref('')
const filterPerson = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const currentSensor = ref<Sensor | null>(null)

// 分页相关
const { currentPage, pageSize, pageSizes, handleSizeChange, handleCurrentChange, resetPagination } = usePagination()

const form = reactive({
  sensor_id: 0,
  sensor_name: '',
  person_id: null,
  batch_id: null,
  start_time: '',
  end_time: '',
  end_reason: ''
})

const rules = computed(() => {
  const baseRules = {
    sensor_name: [
      { required: true, message: '请输入传感器名称', trigger: 'blur' }
    ],
    start_time: [
      { required: true, message: '请选择开始时间', trigger: 'change' }
    ]
  }
  
  // 新建模式下需要验证批次和人员
  if (!isEdit.value) {
    return {
      ...baseRules,
      person_id: [
        { required: true, message: '请选择关联人员', trigger: 'change' }
      ],
      batch_id: [
        { required: true, message: '请选择关联批次', trigger: 'change' }
      ]
    }
  }
  
  return baseRules
})

// 根据选择的批次过滤人员（传感器表单）
const filteredPersonsForSensor = computed(() => {
  if (isEdit.value) {
    // 如果当前选中的人员存在，确保它在列表中
    if (form.person_id) {
      const currentPerson = persons.value.find(p => p.person_id === form.person_id)
      if (currentPerson) {
        // 确保当前人员在列表的第一位，方便识别
        const otherPersons = persons.value.filter(p => p.person_id !== form.person_id)
        return [currentPerson, ...otherPersons]
      }
    }
    return persons.value
  }
  if (!form.batch_id) {
    return []
  }
  return persons.value.filter(person => person.batch_id === form.batch_id)
})

// 监听批次选择变化，清空人员选择（传感器表单）
watch(() => form.batch_id, (newBatchId, oldBatchId) => {
  if (newBatchId !== oldBatchId && !isEdit.value) {
    form.person_id = null
  }
})

// 获取传感器状态
const getSensorStatus = (sensor: Sensor) => {
  const now = new Date()
  const startTime = new Date(sensor.start_time)
  const endTime = sensor.end_time ? new Date(sensor.end_time) : null
  
  if (endTime && now > endTime) {
    return { type: 'info', label: '已结束' }
  } else if (now >= startTime) {
    return { type: 'success', label: '进行中' }
  } else {
    return { type: 'warning', label: '未开始' }
  }
}



// 过滤后的传感器列表
const filteredSensors = computed(() => {
  let result = dataStore.sensors
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(sensor => 
      sensor.sensor_name.toLowerCase().includes(keyword)
    )
  }
  
  if (filterBatch.value) {
    result = result.filter(sensor => sensor.batch_id.toString() === filterBatch.value)
  }
  
  if (filterPerson.value) {
    result = result.filter(sensor => sensor.person_id.toString() === filterPerson.value)
  }
  
  if (filterStatus.value) {
    const now = new Date()
    if (filterStatus.value === 'not_started') {
      result = result.filter(sensor => {
        const startTime = new Date(sensor.start_time)
        return now < startTime
      })
    } else if (filterStatus.value === 'running') {
      result = result.filter(sensor => {
        const startTime = new Date(sensor.start_time)
        const endTime = sensor.end_time ? new Date(sensor.end_time) : null
        return now >= startTime && (!endTime || now <= endTime)
      })
    } else if (filterStatus.value === 'finished') {
      result = result.filter(sensor => {
        const endTime = sensor.end_time ? new Date(sensor.end_time) : null
        return endTime && now > endTime
      })
    }
  }
  
  // 按传感器ID倒序排列，最新创建的在前面
  return result.sort((a, b) => b.sensor_id - a.sensor_id)
})

// 当前页数据
const paginatedSensors = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSensors.value.slice(start, end)
})

// 总数据量
const total = computed(() => filteredSensors.value.length)

// 统计数据
const totalSensors = computed(() => dataStore.sensors.length)
const notStartedSensors = computed(() => {
  const now = new Date()
  return dataStore.sensors.filter(sensor => {
    const startTime = new Date(sensor.start_time)
    return now < startTime
  }).length
})
const runningSensors = computed(() => {
  const now = new Date()
  return dataStore.sensors.filter(sensor => {
    const startTime = new Date(sensor.start_time)
    const endTime = sensor.end_time ? new Date(sensor.end_time) : null
    return now >= startTime && (!endTime || now <= endTime)
  }).length
})
const finishedSensors = computed(() => {
  const now = new Date()
  return dataStore.sensors.filter(sensor => {
    const endTime = sensor.end_time ? new Date(sensor.end_time) : null
    return endTime && now > endTime
  }).length
})





// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
  resetPagination()
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
    const exportData = filteredSensors.value.map(sensor => ({
      '传感器ID': sensor.sensor_id,
      '传感器名称': sensor.sensor_name,
      '关联人员': getPersonName(sensor.person_id),
      '关联批次': getBatchNumber(sensor.batch_id),
      '开始时间': formatDateTime(sensor.start_time),
      '结束时间': formatDateTime(sensor.end_time),
      '结束原因': sensor.end_reason || '-',
      '状态': getSensorStatus(sensor).label
    }))
    
    // 生成文件名
    let filename = '传感器数据'
    
    // 如果有筛选条件，添加到文件名中
    if (filterBatch.value || filterPerson.value) {
      const filters = []
      if (filterBatch.value) {
        const batchNumber = getBatchNumber(parseInt(filterBatch.value))
        filters.push(`批次${batchNumber}`)
      }
      if (filterPerson.value) {
        const personName = getPersonName(parseInt(filterPerson.value)).split(' ')[0]
        filters.push(`人员${personName}`)
      }
      filename = `传感器数据_${filters.join('_')}`
    }
    
    // 导出文件
    exportToExcel(exportData, filename, {
      '传感器ID': 12,
      '传感器名称': 20,
      '关联人员': 20,
      '关联批次': 15,
      '开始时间': 20,
      '结束时间': 20,
      '结束原因': 25,
      '状态': 10
    })
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败，请重试')
  }
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
  // 确保数据完整复制，包括所有字段
  Object.assign(form, {
    sensor_id: row.sensor_id,
    sensor_name: row.sensor_name,
    person_id: row.person_id,
    batch_id: row.batch_id,
    start_time: row.start_time,
    end_time: row.end_time || '',
    end_reason: row.end_reason || ''
  })
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
    
    await dataStore.deleteSensor(row.sensor_id)
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
          await dataStore.updateSensor(form.sensor_id, {
            sensor_name: form.sensor_name,
            person_id: form.person_id,
            batch_id: form.batch_id,
            start_time: form.start_time,
            end_time: form.end_time,
            end_reason: form.end_reason
          })
          ElMessage.success('更新成功')
        } else {
          // 新建
          await dataStore.addSensor({
            sensor_name: form.sensor_name,
            person_id: form.person_id,
            batch_id: form.batch_id,
            start_time: form.start_time,
            end_time: form.end_time,
            end_reason: form.end_reason
          })
          ElMessage.success('添加成功')
        }
        
        dialogVisible.value = false
        resetForm()
      } catch (error) {
        console.error('Submit failed:', error)
        ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
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
    sensor_id: 0,
    sensor_name: '',
    person_id: null,
    batch_id: null,
    start_time: '',
    end_time: '',
    end_reason: ''
  })
}

// 根据选择的批次过滤人员（过滤区域）
const filteredPersonsForFilter = computed(() => {
  if (!filterBatch.value) {
    return availablePersonsForFilter.value
  }
  return availablePersonsForFilter.value.filter(person => person.batch_id.toString() === filterBatch.value)
})

// 监听过滤批次选择变化，清空人员过滤
watch(() => filterBatch.value, (newBatchId, oldBatchId) => {
  if (newBatchId !== oldBatchId && newBatchId) {
    // 如果当前选择的人员不属于新批次，则清空人员过滤
    if (filterPerson.value) {
      const selectedPerson = availablePersonsForFilter.value.find(p => p.person_id.toString() === filterPerson.value)
      if (!selectedPerson || selectedPerson.batch_id.toString() !== newBatchId) {
        filterPerson.value = ''
      }
    }
  }
})
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

.stat-icon.running {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
}

.stat-icon.not-started {
  background: linear-gradient(135deg, #E6A23C 0%, #eebe77 100%);
}

.stat-icon.finished {
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

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
}

.end-reason-text {
  color: #606266;
  font-size: 13px;
}

.no-data {
  color: #C0C4CC;
  font-style: italic;
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