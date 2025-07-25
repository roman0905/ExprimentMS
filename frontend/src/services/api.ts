import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://192.168.10.14:8000',
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
  age?: number
  batch_id?: number
  batch_number?: string
}

export interface ExperimentMember {
  id: number
  experiment_id: number
  person_id: number
  person_name?: string
}

export interface Experiment {
  experiment_id: number
  batch_id: number
  experiment_content?: string
  batch_number?: string
  created_time?: string
  members?: ExperimentMember[]
  member_ids?: number[]
}

export interface Activity {
  activity_id: number
  activity_type: string
  description: string
  createTime: string
  user_id?: number
  username?: string
}

export interface CompetitorFile {
  competitor_file_id: number
  person_id: number
  batch_id: number
  file_path: string
  person_name?: string
  batch_number?: string
  file_size?: number  // 文件大小（字节）
  filename?: string   // 从文件路径提取的文件名
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

  static async getBatchesForPerson(): Promise<Batch[]> {
    return api.get('/api/persons/batches')
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
    return api.get('/api/competitorFiles/')
  }

  static async uploadCompetitorFile(formData: FormData): Promise<CompetitorFile> {
    return api.post('/api/competitorFiles/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  static async downloadCompetitorFile(id: number): Promise<Blob> {
    const response = await api.get(`/api/competitorFiles/download/${id}`, {
      responseType: 'blob'
    })
    return response.data
  }

  static async deleteCompetitorFile(id: number): Promise<void> {
    return api.delete(`/api/competitorFiles/${id}`)
  }

  static async renameCompetitorFile(id: number, newFileName: string): Promise<CompetitorFile> {
    return api.put(`/api/competitorFiles/${id}/rename`, { new_file_name: newFileName })
  }

  // 指尖血数据管理
static async getFingerBloodData(): Promise<FingerBloodData[]> {
    return api.get('/api/fingerBloodData/')
  }

static async createFingerBloodData(data: Omit<FingerBloodData, 'finger_blood_file_id'>): Promise<FingerBloodData> {
    return api.post('/api/fingerBloodData/', data)
  }

static async updateFingerBloodData(id: number, data: Partial<FingerBloodData>): Promise<FingerBloodData> {
    return api.put(`/api/fingerBloodData/${id}`, data)
  }

  static async deleteFingerBloodData(id: number): Promise<void> {
    return api.delete(`/api/fingerBloodData/${id}`)
  }

  static async exportFingerBloodData(params?: {
    batch_id?: number;
    person_id?: number;
    start_time?: string;
    end_time?: string;
  }): Promise<Blob> {
    const searchParams = new URLSearchParams()
    if (params?.batch_id) searchParams.append('batch_id', params.batch_id.toString())
    if (params?.person_id) searchParams.append('person_id', params.person_id.toString())
    if (params?.start_time) searchParams.append('start_time', params.start_time)
    if (params?.end_time) searchParams.append('end_time', params.end_time)
    
    const response = await api.get(`/api/fingerBloodData/export/excel?${searchParams.toString()}`, {
      responseType: 'blob'
    })
    return response.data
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

  // 活动记录管理
  static async getActivities(limit: number = 10): Promise<Activity[]> {
    return api.get(`/api/activities/?limit=${limit}`)
  }

  static async createActivity(activity: Omit<Activity, 'activity_id' | 'created_time'>): Promise<Activity> {
    return api.post('/api/activities/', activity)
  }

  // 竞品数据导出
  static async exportCompetitorData(batchId?: number, personId?: number): Promise<Blob> {
    const params = new URLSearchParams()
    if (batchId) params.append('batch_id', batchId.toString())
    if (personId) params.append('person_id', personId.toString())
    
    const response = await api.get(`/api/competitorFiles/export?${params.toString()}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export default api