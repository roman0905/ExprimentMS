import { ref, computed, watch } from 'vue'
import { useDataStore } from '../stores/data'

/**
 * 批次和人员筛选组合式函数
 * 提供通用的批次-人员联动筛选逻辑
 */
export function useBatchPersonFilter(resetPagination?: () => void) {
  const dataStore = useDataStore()
  const filterBatchId = ref<number | undefined>()
  const filterPersonId = ref<number | undefined>()

  // 根据选择的批次过滤人员
  const filteredPersonsForFilter = computed(() => {
    if (!filterBatchId.value) {
      return dataStore.persons
    }
    return dataStore.persons.filter(person => person.batch_id === filterBatchId.value)
  })

  // 监听批次选择变化，清空人员过滤
  watch(() => filterBatchId.value, (newBatchId, oldBatchId) => {
    if (newBatchId !== oldBatchId) {
      filterPersonId.value = undefined
      if (resetPagination) {
        resetPagination()
      }
    }
  })

  // 重置筛选
  const resetFilter = () => {
    filterBatchId.value = undefined
    filterPersonId.value = undefined
  }

  return {
    filterBatchId,
    filterPersonId,
    filteredPersonsForFilter,
    resetFilter
  }
}

/**
 * 搜索筛选组合式函数
 */
export function useSearch(resetPagination?: () => void) {
  const searchKeyword = ref('')

  // 搜索处理
  const handleSearch = () => {
    if (resetPagination) {
      resetPagination()
    }
  }

  // 重置搜索
  const resetSearch = () => {
    searchKeyword.value = ''
  }

  return {
    searchKeyword,
    handleSearch,
    resetSearch
  }
}