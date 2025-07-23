<template>
  <div class="finger-blood-data">
    <div class="page-header">
      <h2>指尖血数据管理</h2>
      <p>管理血糖数据的录入、查询和可视化展示</p>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="filterBatchId"
          placeholder="筛选批次"
          clearable
          style="width: 150px; margin-right: 12px"
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
          style="width: 150px; margin-right: 12px"
          @change="handleFilter"
        >
          <el-option
            v-for="person in dataStore.persons"
            :key="person.person_id"
            :label="person.person_name"
            :value="person.person_id"
          />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 350px"
          @change="handleFilter"
        />
      </div>
      
      <div class="toolbar-right">
        <el-button @click="toggleChartView">
          <el-icon><TrendCharts /></el-icon>
          {{ showChart ? '隐藏图表' : '显示图表' }}
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          录入数据
        </el-button>
      </div>
    </div>
    
    <!-- 图表展示 -->
    <el-card v-if="showChart" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>血糖值变化趋势</span>
        </div>
      </template>
      <div class="chart-container">
        <v-chart
          class="chart"
          :option="chartOption"
          :loading="chartLoading"
        />
      </div>
    </el-card>
    
    <!-- 数据表格 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>血糖数据列表</span>
          <span class="data-count">共 {{ filteredData.length }} 条记录</span>
        </div>
      </template>
      
      <el-table
        :data="filteredData"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="finger_blood_file_id" label="数据ID" width="100" />
        <el-table-column prop="collection_time" label="采集时间" width="180" />
        <el-table-column prop="blood_glucose_value" label="血糖值(mmol/L)" width="140">
          <template #default="{ row }">
            <el-tag
              :type="getGlucoseLevel(row.blood_glucose_value).type"
              class="glucose-tag"
            >
              {{ row.blood_glucose_value }}
            </el-tag>
            <span class="glucose-level">
              {{ getGlucoseLevel(row.blood_glucose_value).label }}
            </span>
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
      :title="isEdit ? '编辑血糖数据' : '录入血糖数据'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
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
              :label="`${person.person_name} (${person.gender === 'Male' ? '男' : person.gender === 'Female' ? '女' : '其他'})`"
              :value="person.person_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="采集时间" prop="collection_time">
          <el-date-picker
            v-model="form.collection_time"
            type="datetime"
            placeholder="选择采集时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="血糖值(mmol/L)" prop="blood_glucose_value">
          <el-input-number
            v-model="form.blood_glucose_value"
            :min="0"
            :max="30"
            :precision="1"
            :step="0.1"
            placeholder="请输入血糖值"
            style="width: 100%"
          />
          <div class="glucose-hint">
            正常范围：3.9-6.1 mmol/L（空腹）
          </div>
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
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { TrendCharts, Plus } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import { useDataStore, type FingerBloodData } from '../stores/data'
import { ApiService } from '../services/api'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

const dataStore = useDataStore()

const loading = ref(false)

// 组件挂载时获取最新数据
onMounted(async () => {
  try {
    loading.value = true
    const fingerBloodDataData = await ApiService.getFingerBloodData()
    dataStore.fingerBloodData = fingerBloodDataData
  } catch (error) {
    console.error('Failed to load finger blood data:', error)
    ElMessage.error('加载血糖数据失败')
  } finally {
    loading.value = false
  }
})
const chartLoading = ref(false)
const showChart = ref(true)
const filterBatchId = ref<number | undefined>()
const filterPersonId = ref<number | undefined>()
const dateRange = ref<[string, string] | null>(null)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  finger_blood_file_id: 0,
  batch_id: undefined as number | undefined,
  person_id: undefined as number | undefined,
  collection_time: '',
  blood_glucose_value: undefined as number | undefined
})

const rules = {
  batch_id: [
    { required: true, message: '请选择关联批次', trigger: 'change' }
  ],
  person_id: [
    { required: true, message: '请选择关联人员', trigger: 'change' }
  ],
  collection_time: [
    { required: true, message: '请选择采集时间', trigger: 'change' }
  ],
  blood_glucose_value: [
    { required: true, message: '请输入血糖值', trigger: 'blur' },
    { type: 'number', min: 0, max: 30, message: '血糖值应在0-30之间', trigger: 'blur' }
  ]
}

// 过滤后的数据列表
const filteredData = computed(() => {
  let result = dataStore.fingerBloodData
  
  if (filterBatchId.value) {
    result = result.filter(data => data.batch_id === filterBatchId.value)
  }
  
  if (filterPersonId.value) {
    result = result.filter(data => data.person_id === filterPersonId.value)
  }
  
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    result = result.filter(data => {
      const collectionTime = new Date(data.collection_time).getTime()
      const startTime = new Date(dateRange.value![0]).getTime()
      const endTime = new Date(dateRange.value![1]).getTime()
      return collectionTime >= startTime && collectionTime <= endTime
    })
  }
  
  return result.sort((a, b) => new Date(a.collection_time).getTime() - new Date(b.collection_time).getTime())
})

// 图表配置
const chartOption = computed(() => {
  const data = filteredData.value
  
  if (data.length === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16
        }
      }
    }
  }
  
  // 按人员分组数据
  const groupedData = data.reduce((acc, item) => {
    const personName = getPersonName(item.person_id)
    if (!acc[personName]) {
      acc[personName] = []
    }
    acc[personName].push({
      time: item.collection_time,
      value: item.blood_glucose_value
    })
    return acc
  }, {} as Record<string, Array<{ time: string; value: number }>>)
  
  const series = Object.entries(groupedData).map(([personName, personData]) => ({
    name: personName,
    type: 'line',
    data: personData.map(item => [item.time, item.value]),
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: {
      width: 2
    }
  }))
  
  return {
    title: {
      text: '血糖值变化趋势',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let result = `<div style="font-weight: bold;">${params[0].axisValue}</div>`
        params.forEach((param: any) => {
          const level = getGlucoseLevel(param.value[1])
          result += `<div style="margin-top: 4px;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${param.color}; margin-right: 8px;"></span>
            ${param.seriesName}: <strong>${param.value[1]} mmol/L</strong>
            <span style="color: ${level.type === 'success' ? '#67C23A' : level.type === 'warning' ? '#E6A23C' : '#F56C6C'}; margin-left: 8px;">(${level.label})</span>
          </div>`
        })
        return result
      }
    },
    legend: {
      top: 30,
      data: Object.keys(groupedData)
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLabel: {
        formatter: '{MM}-{dd} {HH}:{mm}'
      }
    },
    yAxis: {
      type: 'value',
      name: '血糖值 (mmol/L)',
      min: 0,
      max: 15,
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 100
      }
    ],
    series,
    // 添加正常范围标识线
    markLine: {
      data: [
        {
          yAxis: 3.9,
          lineStyle: { color: '#67C23A', type: 'dashed' },
          label: { formatter: '正常下限 3.9' }
        },
        {
          yAxis: 6.1,
          lineStyle: { color: '#67C23A', type: 'dashed' },
          label: { formatter: '正常上限 6.1' }
        }
      ]
    }
  }
})

// 获取血糖水平
const getGlucoseLevel = (value: number) => {
  if (value < 3.9) {
    return { type: 'danger', label: '偏低' }
  } else if (value <= 6.1) {
    return { type: 'success', label: '正常' }
  } else if (value <= 7.8) {
    return { type: 'warning', label: '偏高' }
  } else {
    return { type: 'danger', label: '过高' }
  }
}

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

// 筛选处理
const handleFilter = () => {
  // 筛选逻辑已在computed中处理
}

// 切换图表显示
const toggleChartView = () => {
  showChart.value = !showChart.value
}

// 新建数据
const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
  resetForm()
}

// 编辑数据
const handleEdit = (row: FingerBloodData) => {
  isEdit.value = true
  dialogVisible.value = true
  Object.assign(form, row)
}

// 删除数据
const handleDelete = async (row: FingerBloodData) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条血糖数据吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    dataStore.deleteFingerBloodData(row.finger_blood_file_id)
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
        dataStore.updateFingerBloodData(form.finger_blood_file_id, {
          batch_id: form.batch_id!,
          person_id: form.person_id!,
          collection_time: form.collection_time,
          blood_glucose_value: form.blood_glucose_value!
        })
        ElMessage.success('更新成功')
      } else {
        // 新建
        dataStore.addFingerBloodData({
          batch_id: form.batch_id!,
          person_id: form.person_id!,
          collection_time: form.collection_time,
          blood_glucose_value: form.blood_glucose_value!
        })
        ElMessage.success('录入成功')
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
    finger_blood_file_id: 0,
    batch_id: undefined,
    person_id: undefined,
    collection_time: '',
    blood_glucose_value: undefined
  })
}

// 监听筛选条件变化，更新图表
watch([filterBatchId, filterPersonId, dateRange], () => {
  chartLoading.value = true
  setTimeout(() => {
    chartLoading.value = false
  }, 500)
})
</script>

<style scoped>
.finger-blood-data {
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

.chart-card {
  margin-bottom: 20px;
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

.chart-container {
  height: 400px;
}

.chart {
  height: 100%;
  width: 100%;
}

.glucose-tag {
  margin-right: 8px;
}

.glucose-level {
  font-size: 12px;
  color: #909399;
}

.glucose-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
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
}
</style>