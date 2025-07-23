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
  file_path: string
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
  person_id: number
  batch_id: number
  start_time: string
  end_time?: string
  person_name?: string
  batch_number?: string
}

// API服务类
export class ApiService {
  // 批次管理
  static async getBatches(): Promise<Batch[]> {
    return api.get('/api/batches/')
  }

  static async createBatch(batch: Omit<Batch, 'batch_id'>): Promise<Batch> {
    return api.post('/api/batches/', batch)
  }

  static async updateBatch(id: number, batch: Partial<Batch>): Promise<Batch> {
    return api.put(`/api/batches/${id}`, batch)
  }

  static async deleteBatch(id: number): Promise<void> {
    return api.delete(`/api/batches/${id}`)
  }

  // 人员管理
  static async getPersons(): Promise<Person[]> {
    return api.get('/api/persons/')
  }

  static async createPerson(person: Omit<Person, 'person_id'>): Promise<Person> {
    return api.post('/api/persons/', person)
  }

  static async updatePerson(id: number, person: Partial<Person>): Promise<Person> {
    return api.put(`/api/persons/${id}`, person)
  }

  static async deletePerson(id: number): Promise<void> {
    return api.delete(`/api/persons/${id}`)
  }

  // 实验管理
  static async getExperiments(): Promise<Experiment[]> {
    return api.get('/api/experiments/')
  }

  static async createExperiment(experiment: Omit<Experiment, 'experiment_id'>): Promise<Experiment> {
    return api.post('/api/experiments/', experiment)
  }

  static async updateExperiment(id: number, experiment: Partial<Experiment>): Promise<Experiment> {
    return api.put(`/api/experiments/${id}`, experiment)
  }

  static async deleteExperiment(id: number): Promise<void> {
    return api.delete(`/api/experiments/${id}`)
  }

  // 竞品文件管理
  static async getCompetitorFiles(): Promise<CompetitorFile[]> {
    return api.get('/api/competitor-files/')
  }

  static async createCompetitorFile(file: Omit<CompetitorFile, 'competitor_file_id'>): Promise<CompetitorFile> {
    return api.post('/api/competitor-files/', file)
  }

  static async deleteCompetitorFile(id: number): Promise<void> {
    return api.delete(`/api/competitor-files/${id}`)
  }

  // 指尖血数据管理
  static async getFingerBloodData(): Promise<FingerBloodData[]> {
    return api.get('/api/finger-blood-data/')
  }

  static async createFingerBloodData(data: Omit<FingerBloodData, 'finger_blood_file_id'>): Promise<FingerBloodData> {
    return api.post('/api/finger-blood-data/', data)
  }

  static async updateFingerBloodData(id: number, data: Partial<FingerBloodData>): Promise<FingerBloodData> {
    return api.put(`/api/finger-blood-data/${id}`, data)
  }

  static async deleteFingerBloodData(id: number): Promise<void> {
    return api.delete(`/api/finger-blood-data/${id}`)
  }

  // 传感器管理
  static async getSensors(): Promise<Sensor[]> {
    return api.get('/api/sensors/')
  }

  static async createSensor(sensor: Omit<Sensor, 'sensor_id'>): Promise<Sensor> {
    return api.post('/api/sensors/', sensor)
  }

  static async updateSensor(id: number, sensor: Partial<Sensor>): Promise<Sensor> {
    return api.put(`/api/sensors/${id}`, sensor)
  }

  static async deleteSensor(id: number): Promise<void> {
    return api.delete(`/api/sensors/${id}`)
  }
}

export default api