import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ApiService } from '../services/api'
import type {
  Batch,
  Person,
  Experiment,
  CompetitorFile,
  FingerBloodData,
  Sensor
} from '../services/api'

// 重新导出类型
export type {
  Batch,
  Person,
  Experiment,
  CompetitorFile,
  FingerBloodData,
  Sensor
}

export const useDataStore = defineStore('data', () => {
  // 响应式数据
  const batches = ref<Batch[]>([])
  const persons = ref<Person[]>([])
  const experiments = ref<Experiment[]>([])
  const competitorFiles = ref<CompetitorFile[]>([])
  const fingerBloodData = ref<FingerBloodData[]>([])
  const sensors = ref<Sensor[]>([])
  
  // 加载状态
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 初始化数据
  const initializeData = async () => {
    try {
      loading.value = true
      error.value = null
      
      const [batchesData, personsData, experimentsData, competitorFilesData, fingerBloodDataData, sensorsData] = await Promise.all([
        ApiService.getBatches(),
        ApiService.getPersons(),
        ApiService.getExperiments(),
        ApiService.getCompetitorFiles(),
        ApiService.getFingerBloodData(),
        ApiService.getSensors()
      ])
      
      batches.value = batchesData
      persons.value = personsData
      experiments.value = experimentsData
      competitorFiles.value = competitorFilesData
      fingerBloodData.value = fingerBloodDataData
      sensors.value = sensorsData
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载数据失败'
      console.error('Failed to initialize data:', err)
    } finally {
      loading.value = false
    }
  }

  // 批次管理
  const addBatch = async (batch: Omit<Batch, 'batch_id'>) => {
    try {
      const newBatch = await ApiService.createBatch(batch)
      batches.value.push(newBatch)
      return newBatch
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建批次失败'
      throw err
    }
  }

  const updateBatch = async (id: number, batch: Partial<Batch>) => {
    try {
      const updatedBatch = await ApiService.updateBatch(id, batch)
      const index = batches.value.findIndex(b => b.batch_id === id)
      if (index !== -1) {
        batches.value[index] = updatedBatch
      }
      return updatedBatch
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新批次失败'
      throw err
    }
  }

  const deleteBatch = async (id: number) => {
    try {
      await ApiService.deleteBatch(id)
      const index = batches.value.findIndex(b => b.batch_id === id)
      if (index !== -1) {
        batches.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除批次失败'
      throw err
    }
  }

  // 人员管理
  const addPerson = async (person: Omit<Person, 'person_id'>) => {
    try {
      const newPerson = await ApiService.createPerson(person)
      persons.value.push(newPerson)
      return newPerson
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建人员失败'
      throw err
    }
  }

  const updatePerson = async (id: number, person: Partial<Person>) => {
    try {
      const updatedPerson = await ApiService.updatePerson(id, person)
      const index = persons.value.findIndex(p => p.person_id === id)
      if (index !== -1) {
        persons.value[index] = updatedPerson
      }
      return updatedPerson
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新人员失败'
      throw err
    }
  }

  const deletePerson = async (id: number) => {
    try {
      await ApiService.deletePerson(id)
      const index = persons.value.findIndex(p => p.person_id === id)
      if (index !== -1) {
        persons.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除人员失败'
      throw err
    }
  }

  // 实验管理
  const addExperiment = async (experiment: Omit<Experiment, 'experiment_id'>) => {
    try {
      const newExperiment = await ApiService.createExperiment(experiment)
      experiments.value.push(newExperiment)
      return newExperiment
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建实验失败'
      throw err
    }
  }

  const updateExperiment = async (id: number, experiment: Partial<Experiment>) => {
    try {
      const updatedExperiment = await ApiService.updateExperiment(id, experiment)
      const index = experiments.value.findIndex(e => e.experiment_id === id)
      if (index !== -1) {
        experiments.value[index] = updatedExperiment
      }
      return updatedExperiment
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新实验失败'
      throw err
    }
  }

  const deleteExperiment = async (id: number) => {
    try {
      await ApiService.deleteExperiment(id)
      const index = experiments.value.findIndex(e => e.experiment_id === id)
      if (index !== -1) {
        experiments.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除实验失败'
      throw err
    }
  }

  // 竞品文件管理
  const addCompetitorFile = async (formData: FormData) => {
    try {
      const newFile = await ApiService.uploadCompetitorFile(formData)
      competitorFiles.value.push(newFile)
      return newFile
    } catch (err) {
      error.value = err instanceof Error ? err.message : '上传竞品文件失败'
      throw err
    }
  }

  const deleteCompetitorFile = async (id: number) => {
    try {
      await ApiService.deleteCompetitorFile(id)
      const index = competitorFiles.value.findIndex(f => f.competitor_file_id === id)
      if (index !== -1) {
        competitorFiles.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除竞品文件失败'
      throw err
    }
  }

  // 指尖血数据管理
  const addFingerBloodData = async (data: Omit<FingerBloodData, 'finger_blood_file_id'>) => {
    try {
      const newData = await ApiService.createFingerBloodData(data)
      fingerBloodData.value.push(newData)
      return newData
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建指尖血数据失败'
      throw err
    }
  }

  const updateFingerBloodData = async (id: number, data: Partial<FingerBloodData>) => {
    try {
      const updatedData = await ApiService.updateFingerBloodData(id, data)
      const index = fingerBloodData.value.findIndex(d => d.finger_blood_file_id === id)
      if (index !== -1) {
        fingerBloodData.value[index] = updatedData
      }
      return updatedData
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新指尖血数据失败'
      throw err
    }
  }

  const deleteFingerBloodData = async (id: number) => {
    try {
      await ApiService.deleteFingerBloodData(id)
      const index = fingerBloodData.value.findIndex(d => d.finger_blood_file_id === id)
      if (index !== -1) {
        fingerBloodData.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除指尖血数据失败'
      throw err
    }
  }

  // 传感器管理
  const addSensor = async (sensor: Omit<Sensor, 'sensor_id'>) => {
    try {
      const newSensor = await ApiService.createSensor(sensor)
      sensors.value.push(newSensor)
      return newSensor
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建传感器失败'
      throw err
    }
  }

  const updateSensor = async (sensorId: number, updates: Partial<Sensor>) => {
    try {
      const updatedSensor = await ApiService.updateSensor(sensorId, updates)
      const index = sensors.value.findIndex(s => s.sensor_id === sensorId)
      if (index !== -1) {
        sensors.value[index] = updatedSensor
      }
      return updatedSensor
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新传感器失败'
      throw err
    }
  }

  const deleteSensor = async (sensorId: number) => {
    try {
      await ApiService.deleteSensor(sensorId)
      const index = sensors.value.findIndex(s => s.sensor_id === sensorId)
      if (index !== -1) {
        sensors.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除传感器失败'
      throw err
    }
  }

  return {
    // 数据
    batches,
    persons,
    experiments,
    competitorFiles,
    fingerBloodData,
    sensors,
    // 状态
    loading,
    error,
    // 初始化
    initializeData,
    // 批次管理
    addBatch,
    updateBatch,
    deleteBatch,
    // 人员管理
    addPerson,
    updatePerson,
    deletePerson,
    // 实验管理
    addExperiment,
    updateExperiment,
    deleteExperiment,
    // 竞品文件管理
    addCompetitorFile,
    deleteCompetitorFile,
    // 指尖血数据管理
    addFingerBloodData,
    updateFingerBloodData,
    deleteFingerBloodData,
    // 传感器管理
    addSensor,
    updateSensor,
    deleteSensor
  }
})