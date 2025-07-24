import { ref, computed } from 'vue'

/**
 * 分页组合式函数
 * 提供通用的分页逻辑和状态管理
 */
export function usePagination(defaultPageSize = 10) {
  const currentPage = ref(1)
  const pageSize = ref(defaultPageSize)
  const pageSizes = [10, 20, 50, 100]
  const total = ref(0)

  // 分页事件处理
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
  }

  const handleCurrentChange = (val: number) => {
    currentPage.value = val
  }

  // 重置分页到第一页
  const resetPagination = () => {
    currentPage.value = 1
  }

  return {
    currentPage,
    pageSize,
    pageSizes,
    total,
    handleSizeChange,
    handleCurrentChange,
    resetPagination
  }
}