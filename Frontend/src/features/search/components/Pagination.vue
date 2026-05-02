<template>
  <div class="flex flex-col md:flex-row items-center justify-between gap-4 py-4">
    <!-- Page Size Selector -->
    <div class="flex items-center gap-3">
      <span class="text-sm text-gray-700 dark:text-gray-300">Items per page:</span>
      <FormSelect
        :model-value="pageSize"
        :options="pageSizeOptions"
        @update:model-value="handlePageSizeChange"
      />
    </div>

    <!-- Page Info -->
    <div class="text-sm text-gray-600 dark:text-gray-400">
      Showing
      <span class="font-semibold">{{ startItem }}</span>
      to
      <span class="font-semibold">{{ endItem }}</span>
      of
      <span class="font-semibold">{{ totalItems }}</span>
      results
    </div>

    <!-- Pagination Controls -->
    <div class="flex items-center gap-2">
      <!-- Previous Button -->
      <button
        type="button"
        :disabled="currentPage === 1"
        class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        @click="goToPreviousPage"
      >
        Previous
      </button>

      <!-- Page Numbers -->
      <div class="flex items-center gap-1">
        <!-- First Page -->
        <button
          v-if="showFirstPage"
          type="button"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
          @click="goToPage(1)"
        >
          1
        </button>

        <!-- Ellipsis -->
        <span v-if="showFirstEllipsis" class="px-2 text-gray-500 dark:text-gray-400">...</span>

        <!-- Page Range -->
        <button
          v-for="page in pageRange"
          :key="page"
          type="button"
          :class="[
            'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            page === currentPage
              ? 'bg-blue-600 text-white'
              : 'border border-gray-300 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700'
          ]"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>

        <!-- Ellipsis -->
        <span v-if="showLastEllipsis" class="px-2 text-gray-500 dark:text-gray-400">...</span>

        <!-- Last Page -->
        <button
          v-if="showLastPage"
          type="button"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
          @click="goToPage(totalPages)"
        >
          {{ totalPages }}
        </button>
      </div>

      <!-- Next Button -->
      <button
        type="button"
        :disabled="currentPage === totalPages"
        class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        @click="goToNextPage"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FormSelect from '@/shared/components/ui/FormSelect.vue'

const props = withDefaults(
  defineProps<{
    currentPage?: number
    pageSize?: number
    totalItems?: number
    maxVisiblePages?: number
  }>(),
  {
    currentPage: 1,
    pageSize: 25,
    totalItems: 0,
    maxVisiblePages: 5
  }
)

const emit = defineEmits<{
  'update:currentPage': [page: number]
  'update:pageSize': [size: number]
  'page-change': [page: number]
  'page-size-change': [size: number]
}>()

const pageSizeOptions = [
  { label: '10', value: 10 },
  { label: '25', value: 25 },
  { label: '50', value: 50 },
  { label: '100', value: 100 }
]

const totalPages = computed(() => Math.ceil(props.totalItems / props.pageSize))

const startItem = computed(() => {
  if (props.totalItems === 0) return 0
  return (props.currentPage - 1) * props.pageSize + 1
})

const endItem = computed(() => {
  const end = props.currentPage * props.pageSize
  return Math.min(end, props.totalItems)
})

const pageRange = computed(() => {
  const pages: number[] = []
  const halfVisible = Math.floor(props.maxVisiblePages / 2)
  let start = Math.max(1, props.currentPage - halfVisible)
  let end = Math.min(totalPages.value, props.currentPage + halfVisible)

  // Adjust range if near the beginning or end
  if (start === 1) {
    end = Math.min(totalPages.value, props.maxVisiblePages)
  } else if (end === totalPages.value) {
    start = Math.max(1, totalPages.value - props.maxVisiblePages + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

const showFirstPage = computed(() => {
  return pageRange.value[0] > 1
})

const showFirstEllipsis = computed(() => {
  return pageRange.value[0] > 2
})

const showLastPage = computed(() => {
  return pageRange.value[pageRange.value.length - 1] < totalPages.value
})

const showLastEllipsis = computed(() => {
  return pageRange.value[pageRange.value.length - 1] < totalPages.value - 1
})

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
    emit('update:currentPage', page)
    emit('page-change', page)
  }
}

const goToPreviousPage = () => {
  if (props.currentPage > 1) {
    goToPage(props.currentPage - 1)
  }
}

const goToNextPage = () => {
  if (props.currentPage < totalPages.value) {
    goToPage(props.currentPage + 1)
  }
}

const handlePageSizeChange = (newSize: string | number) => {
  const size = typeof newSize === 'string' ? parseInt(newSize) : newSize
  emit('update:pageSize', size)
  emit('page-size-change', size)
  // Reset to first page when page size changes
  emit('update:currentPage', 1)
  emit('page-change', 1)
}
</script>
