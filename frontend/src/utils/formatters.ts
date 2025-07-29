import { useDataStore } from '../stores/data'

/**
 * 数据格式化工具函数
 */

/**
 * 获取批次号
 */
export function getBatchNumber(batchId: number): string {
  const dataStore = useDataStore()
  const batch = dataStore.batches.find(b => b.batch_id === batchId)
  return batch?.batch_number || '未知批次'
}

/**
 * 获取人员姓名
 */
export function getPersonName(personId: number): string {
  const dataStore = useDataStore()
  const person = dataStore.persons.find(p => p.person_id === personId)
  return person ? `${person.person_name} (ID: ${person.person_id})` : '未知人员'
}

/**
 * 格式化日期时间
 * 统一输出格式：YYYY-MM-DD HH:mm:ss（不带T）
 */
export function formatDateTime(dateTime: string | Date): string {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 格式化日期
 */
export function formatDate(date: string | Date): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  if (!bytes) return '未知大小'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}