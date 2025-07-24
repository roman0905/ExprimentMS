import * as XLSX from 'xlsx'

/**
 * Excel导出工具函数
 */

/**
 * 导出数据到Excel文件
 * @param data 要导出的数据数组
 * @param filename 文件名（不包含扩展名）
 * @param sheetNameOrColWidths 工作表名称或列宽配置对象
 */
export function exportToExcel(
  data: any[], 
  filename: string, 
  sheetNameOrColWidths: string | Record<string, number> = 'Sheet1'
) {
  try {
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(data)
    
    // 设置列宽
    let colWidths: any[]
    let sheetName: string
    
    if (typeof sheetNameOrColWidths === 'string') {
      // 如果是字符串，作为工作表名称，自动计算列宽
      sheetName = sheetNameOrColWidths
      colWidths = Object.keys(data[0] || {}).map(key => {
        const maxLength = Math.max(
          key.length,
          ...data.map(row => String(row[key] || '').length)
        )
        return { wch: Math.min(maxLength + 2, 50) }
      })
    } else {
      // 如果是对象，作为列宽配置
      sheetName = 'Sheet1'
      colWidths = Object.keys(data[0] || {}).map(key => ({
        wch: sheetNameOrColWidths[key] || 15
      }))
    }
    
    ws['!cols'] = colWidths
    
    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(wb, ws, sheetName)
    
    // 导出文件
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
    const fullFilename = `${filename}_${timestamp}.xlsx`
    XLSX.writeFile(wb, fullFilename)
    
    return true
  } catch (error) {
    console.error('Excel导出失败:', error)
    return false
  }
}

/**
 * 批量导出多个工作表到一个Excel文件
 * @param sheets 工作表数组，每个元素包含 { data, name }
 * @param filename 文件名（不包含扩展名）
 */
export function exportMultipleSheetsToExcel(
  sheets: Array<{ data: any[], name: string }>,
  filename: string
) {
  try {
    const wb = XLSX.utils.book_new()
    
    sheets.forEach(sheet => {
      const ws = XLSX.utils.json_to_sheet(sheet.data)
      
      // 设置列宽
      if (sheet.data.length > 0) {
        const colWidths = Object.keys(sheet.data[0]).map(key => {
          const maxLength = Math.max(
            key.length,
            ...sheet.data.map(row => String(row[key] || '').length)
          )
          return { wch: Math.min(maxLength + 2, 50) }
        })
        ws['!cols'] = colWidths
      }
      
      XLSX.utils.book_append_sheet(wb, ws, sheet.name)
    })
    
    // 导出文件
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
    const fullFilename = `${filename}_${timestamp}.xlsx`
    XLSX.writeFile(wb, fullFilename)
    
    return true
  } catch (error) {
    console.error('Excel导出失败:', error)
    return false
  }
}