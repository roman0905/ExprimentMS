import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

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

// API服务类
export class ApiService {
  // 批次管理
  static async getBatches(): Promise<Batch[]> {
    return api.get('/batches/')
  }

  static async createBatch(batch: Omit<Batch, 'batch_id'>): Promise<Batch> {
    return api.post('/batches/', batch)
  }

  static async updateBatch(id: number, batch: Partial<Batch>): Promise<Batch> {
    return api.put(`/batches/${id}`, batch)
  }

  static async deleteBatch(id: number): Promise<void> {
    return api.delete(`/batches/${id}`)
  }

  // 人员管理
  static async getPersons(): Promise<Person[]> {
    return api.get('/persons/')
  }

  static async createPerson(person: Omit<Person, 'person_id'>): Promise<Person> {
    return api.post('/persons/', person)
  }

  static async updatePerson(id: number, person: Partial<Person>): Promise<Person> {
    return api.put(`/persons/${id}`, person)
  }

  static async deletePerson(id: number): Promise<void> {
    return api.delete(`/persons/${id}`)
  }

  // 实验管理
  static async getExperiments(): Promise<Experiment[]> {
    return api.get('/experiments/')
  }

  static async createExperiment(experiment: Omit<Experiment, 'experiment_id'>): Promise<Experiment> {
    return api.post('/experiments/', experiment)
  }

  static async updateExperiment(id: number, experiment: Partial<Experiment>): Promise<Experiment> {
    return api.put(`/experiments/${id}`, experiment)
  }

  static async deleteExperiment(id: number): Promise<void> {
    return api.delete(`/experiments/${id}`)
  }

  // 竞品文件管理
  static async getCompetitorFiles(): Promise<CompetitorFile[]> {
    return api.get('/competitor-files/')
  }

  static async createCompetitorFile(file: Omit<CompetitorFile, 'competitor_file_id'>): Promise<CompetitorFile> {
    return api.post('/competitor-files/', file)
  }

  static async deleteCompetitorFile(id: number): Promise<void> {
    return api.delete(`/competitor-files/${id}`)
  }

  // 指尖血数据管理
  static async getFingerBloodData(): Promise<FingerBloodData[]> {
    return api.get('/finger-blood-data/')
  }

  static async createFingerBloodData(data: Omit<FingerBloodData, 'finger_blood_file_id'>): Promise<FingerBloodData> {
    return api.post('/finger-blood-data/', data)
  }

  static async updateFingerBloodData(id: number, data: Partial<FingerBloodData>): Promise<FingerBloodData> {
    return api.put(`/finger-blood-data/${id}`, data)
  }

  static async deleteFingerBloodData(id: number): Promise<void> {
    return api.delete(`/finger-blood-data/${id}`)
  }

  // 传感器管理
  static async getSensors(): Promise<Sensor[]> {
    return api.get('/sensors/')
  }

  static async createSensor(sensor: Omit<Sensor, 'sensor_id'>): Promise<Sensor> {
    return api.post('/sensors/', sensor)
  }

  static async updateSensor(id: number, sensor: Partial<Sensor>): Promise<Sensor> {
    return api.put(`/sensors/${id}`, sensor)
  }

  static async deleteSensor(id: number): Promise<void> {
    return api.delete(`/sensors/${id}`)
  }
}

export default api