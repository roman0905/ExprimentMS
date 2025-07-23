import { defineStore } from 'pinia'
import { ref } from 'vue'

// 数据类型定义
export interface Batch {
  batch_id: number
  batch_number: string
  start_time: string
  end_time?: string
}

export interface Person {
  person_id: number
  person_name: string
  gender?: 'Male' | 'Female' | 'Other'
  height_cm?: number
  weight_kg?: number
  age?: number
}

export interface Experiment {
  experiment_id: number
  batch_id: number
  person_id: number
  experiment_content?: string
  batch_number?: string
  person_name?: string
}

export interface CompetitorFile {
  competitor_file_id: number
  person_id: number
  batch_id: number
  file_name: string
  person_name?: string
  batch_number?: string
}

export interface FingerBloodData {
  finger_blood_file_id: number
  person_id: number
  batch_id: number
  collection_time: string
  blood_glucose_value: number
  person_name?: string
  batch_number?: string
}

export interface Sensor {
  sensor_id: number
  sensor_name: string
  sensor_type: string
  model: string
  manufacturer: string
  installation_date: string
  last_maintenance: string
  status: string
  location: string
  description?: string
}

export const useDataStore = defineStore('data', () => {
  // 模拟数据
  const batches = ref<Batch[]>([
    {
      batch_id: 1,
      batch_number: 'BATCH001',
      start_time: '2024-01-01 09:00:00',
      end_time: '2024-01-01 17:00:00'
    },
    {
      batch_id: 2,
      batch_number: 'BATCH002',
      start_time: '2024-01-02 09:00:00'
    }
  ])

  const persons = ref<Person[]>([
    {
      person_id: 1,
      person_name: '张三',
      gender: 'Male',
      height_cm: 175,
      weight_kg: 70,
      age: 25
    },
    {
      person_id: 2,
      person_name: '李四',
      gender: 'Female',
      height_cm: 165,
      weight_kg: 55,
      age: 28
    }
  ])

  const experiments = ref<Experiment[]>([
    {
      experiment_id: 1,
      batch_id: 1,
      person_id: 1,
      experiment_content: '血糖监测实验'
    }
  ])

  const competitorFiles = ref<CompetitorFile[]>([
    {
      competitor_file_id: 1,
      person_id: 1,
      batch_id: 1,
      file_name: 'competitor_data_001.xlsx'
    }
  ])

  const fingerBloodData = ref<FingerBloodData[]>([
    {
      finger_blood_file_id: 1,
      person_id: 1,
      batch_id: 1,
      collection_time: '2024-01-01 10:00:00',
      blood_glucose_value: 5.6
    },
    {
      finger_blood_file_id: 2,
      person_id: 1,
      batch_id: 1,
      collection_time: '2024-01-01 14:00:00',
      blood_glucose_value: 7.2
    }
  ])

  const sensors = ref<Sensor[]>([
    {
      sensor_id: 1,
      sensor_name: '血糖传感器001',
      sensor_type: 'Blood Glucose',
      model: 'BGS-2024',
      manufacturer: 'MedTech Corp',
      installation_date: '2024-01-01',
      last_maintenance: '2024-01-01',
      status: 'Normal',
      location: 'Lab Room 1',
      description: '高精度血糖监测传感器'
    }
  ])

  // 获取下一个ID
  const getNextId = (array: any[]) => {
    return array.length > 0 ? Math.max(...array.map(item => Object.values(item)[0] as number)) + 1 : 1
  }

  // 批次管理
  const addBatch = (batch: Omit<Batch, 'batch_id'>) => {
    const newBatch = {
      ...batch,
      batch_id: getNextId(batches.value)
    }
    batches.value.push(newBatch)
    return newBatch
  }

  const updateBatch = (id: number, batch: Partial<Batch>) => {
    const index = batches.value.findIndex(b => b.batch_id === id)
    if (index !== -1) {
      batches.value[index] = { ...batches.value[index], ...batch }
    }
  }

  const deleteBatch = (id: number) => {
    const index = batches.value.findIndex(b => b.batch_id === id)
    if (index !== -1) {
      batches.value.splice(index, 1)
    }
  }

  // 人员管理
  const addPerson = (person: Omit<Person, 'person_id'>) => {
    const newPerson = {
      ...person,
      person_id: getNextId(persons.value)
    }
    persons.value.push(newPerson)
    return newPerson
  }

  const updatePerson = (id: number, person: Partial<Person>) => {
    const index = persons.value.findIndex(p => p.person_id === id)
    if (index !== -1) {
      persons.value[index] = { ...persons.value[index], ...person }
    }
  }

  const deletePerson = (id: number) => {
    const index = persons.value.findIndex(p => p.person_id === id)
    if (index !== -1) {
      persons.value.splice(index, 1)
    }
  }

  // 实验管理
  const addExperiment = (experiment: Omit<Experiment, 'experiment_id'>) => {
    const newExperiment = {
      ...experiment,
      experiment_id: getNextId(experiments.value)
    }
    experiments.value.push(newExperiment)
    return newExperiment
  }

  const updateExperiment = (id: number, experiment: Partial<Experiment>) => {
    const index = experiments.value.findIndex(e => e.experiment_id === id)
    if (index !== -1) {
      experiments.value[index] = { ...experiments.value[index], ...experiment }
    }
  }

  const deleteExperiment = (id: number) => {
    const index = experiments.value.findIndex(e => e.experiment_id === id)
    if (index !== -1) {
      experiments.value.splice(index, 1)
    }
  }

  // 竞品文件管理
  const addCompetitorFile = (file: Omit<CompetitorFile, 'competitor_file_id'>) => {
    const newFile = {
      ...file,
      competitor_file_id: getNextId(competitorFiles.value)
    }
    competitorFiles.value.push(newFile)
    return newFile
  }

  const deleteCompetitorFile = (id: number) => {
    const index = competitorFiles.value.findIndex(f => f.competitor_file_id === id)
    if (index !== -1) {
      competitorFiles.value.splice(index, 1)
    }
  }

  // 指尖血数据管理
  const addFingerBloodData = (data: Omit<FingerBloodData, 'finger_blood_file_id'>) => {
    const newData = {
      ...data,
      finger_blood_file_id: getNextId(fingerBloodData.value)
    }
    fingerBloodData.value.push(newData)
    return newData
  }

  const updateFingerBloodData = (id: number, data: Partial<FingerBloodData>) => {
    const index = fingerBloodData.value.findIndex(d => d.finger_blood_file_id === id)
    if (index !== -1) {
      fingerBloodData.value[index] = { ...fingerBloodData.value[index], ...data }
    }
  }

  const deleteFingerBloodData = (id: number) => {
    const index = fingerBloodData.value.findIndex(d => d.finger_blood_file_id === id)
    if (index !== -1) {
      fingerBloodData.value.splice(index, 1)
    }
  }

  // 传感器管理
  const addSensor = (sensor: Omit<Sensor, 'sensor_id'>) => {
    const newSensor = {
      ...sensor,
      sensor_id: getNextId(sensors.value)
    }
    sensors.value.push(newSensor)
    return newSensor
  }

  const updateSensor = (sensorId: number, updates: Partial<Sensor>) => {
    const index = sensors.value.findIndex(s => s.sensor_id === sensorId)
    if (index !== -1) {
      sensors.value[index] = { ...sensors.value[index], ...updates }
    }
  }

  const deleteSensor = (sensorId: number) => {
    const index = sensors.value.findIndex(s => s.sensor_id === sensorId)
    if (index !== -1) {
      sensors.value.splice(index, 1)
    }
  }

  return {
    batches,
    persons,
    experiments,
    competitorFiles,
    fingerBloodData,
    sensors,
    addBatch,
    updateBatch,
    deleteBatch,
    addPerson,
    updatePerson,
    deletePerson,
    addExperiment,
    updateExperiment,
    deleteExperiment,
    addCompetitorFile,
    deleteCompetitorFile,
    addFingerBloodData,
    updateFingerBloodData,
    deleteFingerBloodData,
    addSensor,
    updateSensor,
    deleteSensor
  }
})