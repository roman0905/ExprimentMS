import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 注意：请求和响应拦截器现在由 auth.ts 中的 setupApiInterceptors 方法统一管理

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
  upload_time: string
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
  end_reason?: string
  person_name?: string
  batch_number?: string
}

// API服务类
export class ApiService {
  // 用户认证管理
  static async login(data: { username: string; password: string }) {
    const response = await api.post('/api/auth/login', data)
    return response.data
  }

  static async register(data: { username: string; password: string }) {
    const response = await api.post('/api/auth/register', data)
    return response.data
  }

  static async getCurrentUser() {
    const response = await api.get('/api/auth/me')
    return response.data
  }

  static async logout() {
    const response = await api.post('/api/auth/logout')
    return response.data
  }

  static async getUsers() {
    const response = await api.get('/api/auth/users')
    return response.data
  }

  static async createUser(data: any) {
    const response = await api.post('/api/auth/users', data)
    return response.data
  }

  static async updateUser(userId: number, data: any) {
    const response = await api.put(`/api/auth/users/${userId}`, data)
    return response.data
  }

  static async deleteUser(userId: number) {
    await api.delete(`/api/auth/users/${userId}`)
  }

  static async getUserPermissions(userId: number) {
    const response = await api.get(`/api/auth/users/${userId}/permissions`)
    return response.data
  }

  static async assignPermissions(data: any) {
    const response = await api.post('/api/auth/assign-permissions', data)
    return response.data
  }
  // 批次管理
  static async getBatches(): Promise<Batch[]> {
    const response = await api.get('/api/batches/')
    return response.data
  }

  static async createBatch(batch: Omit<Batch, 'batch_id'>): Promise<Batch> {
    const response = await api.post('/api/batches/', batch)
    return response.data
  }

  static async updateBatch(id: number, batch: Partial<Batch>): Promise<Batch> {
    const response = await api.put(`/api/batches/${id}`, batch)
    return response.data
  }

  static async deleteBatch(id: number): Promise<void> {
    await api.delete(`/api/batches/${id}`)
  }

  // 人员管理
  static async getPersons(): Promise<Person[]> {
    const response = await api.get('/api/persons/')
    return response.data
  }

  static async createPerson(person: Omit<Person, 'person_id'>): Promise<Person> {
    const response = await api.post('/api/persons/', person)
    return response.data
  }

  static async updatePerson(id: number, person: Partial<Person>): Promise<Person> {
    const response = await api.put(`/api/persons/${id}`, person)
    return response.data
  }

  static async deletePerson(id: number): Promise<void> {
    await api.delete(`/api/persons/${id}`)
  }

  static async getBatchesForPerson(): Promise<Batch[]> {
    const response = await api.get('/api/persons/batches')
    return response.data
  }

  // 实验管理
  static async getExperiments(): Promise<Experiment[]> {
    const response = await api.get('/api/experiments/')
    return response.data
  }

  static async createExperiment(experiment: Omit<Experiment, 'experiment_id'>): Promise<Experiment> {
    const response = await api.post('/api/experiments/', experiment)
    return response.data
  }

  static async updateExperiment(id: number, experiment: Partial<Experiment>): Promise<Experiment> {
    const response = await api.put(`/api/experiments/${id}`, experiment)
    return response.data
  }

  static async deleteExperiment(id: number): Promise<void> {
    await api.delete(`/api/experiments/${id}`)
  }

  // 竞品文件管理
  static async getCompetitorFiles(): Promise<CompetitorFile[]> {
    const response = await api.get('/api/competitorFiles/')
    return response.data
  }

  static async uploadCompetitorFile(formData: FormData): Promise<CompetitorFile> {
    const response = await api.post('/api/competitorFiles/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  static async downloadCompetitorFile(id: number): Promise<Blob> {
    const response = await api.get(`/api/competitorFiles/download/${id}`, {
      responseType: 'blob'
    })
    return response.data
  }

  static async deleteCompetitorFile(id: number): Promise<void> {
    await api.delete(`/api/competitorFiles/${id}`)
  }

  static async renameCompetitorFile(id: number, newFileName: string): Promise<CompetitorFile> {
    const response = await api.put(`/api/competitorFiles/${id}/rename`, { new_file_name: newFileName })
    return response.data
  }

  // 指尖血数据管理
  static async getFingerBloodData(): Promise<FingerBloodData[]> {
    const response = await api.get('/api/fingerBloodData/')
    return response.data
  }

  static async createFingerBloodData(data: Omit<FingerBloodData, 'finger_blood_file_id'>): Promise<FingerBloodData> {
    const response = await api.post('/api/fingerBloodData/', data)
    return response.data
  }

  static async updateFingerBloodData(id: number, data: Partial<FingerBloodData>): Promise<FingerBloodData> {
    const response = await api.put(`/api/fingerBloodData/${id}`, data)
    return response.data
  }

  static async deleteFingerBloodData(id: number): Promise<void> {
    await api.delete(`/api/fingerBloodData/${id}`)
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
    const response = await api.get('/api/sensors/')
    return response.data
  }

  static async createSensor(sensor: Omit<Sensor, 'sensor_id'>): Promise<Sensor> {
    const response = await api.post('/api/sensors/', sensor)
    return response.data
  }

  static async updateSensor(id: number, sensor: Partial<Sensor>): Promise<Sensor> {
    const response = await api.put(`/api/sensors/${id}`, sensor)
    return response.data
  }

  static async deleteSensor(id: number): Promise<void> {
    await api.delete(`/api/sensors/${id}`)
  }

  // 活动记录管理
  static async getActivities(limit: number = 10): Promise<Activity[]> {
    const response = await api.get(`/api/activities/?limit=${limit}`)
    return response.data
  }

  static async createActivity(activity: Omit<Activity, 'activity_id' | 'created_time'>): Promise<Activity> {
    const response = await api.post('/api/activities/', activity)
    return response.data
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

// 为了向后兼容，导出userApi对象
export const userApi = {
  login: (data: { username: string; password: string }) => ApiService.login(data),
  register: (data: { username: string; password: string }) => ApiService.register(data),
  getCurrentUser: () => ApiService.getCurrentUser(),
  logout: () => ApiService.logout(),
  getUsers: () => ApiService.getUsers(),
  createUser: (data: any) => ApiService.createUser(data),
  updateUser: (userId: number, data: any) => ApiService.updateUser(userId, data),
  deleteUser: (userId: number) => ApiService.deleteUser(userId),
  getUserPermissions: (userId: number) => ApiService.getUserPermissions(userId),
  assignPermissions: (data: any) => ApiService.assignPermissions(data)
}

export default api