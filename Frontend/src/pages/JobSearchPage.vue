<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">البحث عن الوظائف</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">ابحث عن الوظائف المناسبة لك من آلاف الفرص المتاحة</p>
    </div>

    <!-- Search Bar Component -->
    <SearchBar
      v-model="searchQuery"
      v-model:site="selectedSite"
      v-model:filters="searchFilters"
      @search="handleSearch"
    />

    <!-- Search and Filters Section -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Filters Sidebar -->
      <div class="lg:col-span-1">
        <FilterPanel
          :filters="filterState"
          @update:filters="updateFilters"
          @filter-change="handleFilterChange"
        />
      </div>

      <!-- Jobs List -->
      <div class="lg:col-span-3">
        <!-- Results Header with Sort -->
        <div v-if="jobs.length > 0" class="flex justify-between items-center mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            عدد النتائج: <span class="font-semibold">{{ totalJobs }}</span>
          </div>
          <div class="flex items-center gap-2">
            <label for="sort-select" class="text-sm text-gray-700 dark:text-gray-300">ترتيب:</label>
            <select
              id="sort-select"
              v-model="sortBy"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-sm"
              @change="handleSortChange"
            >
              <option value="recent">الأحدث أولاً</option>
              <option value="salary-high">الراتب (الأعلى أولاً)</option>
              <option value="salary-low">الراتب (الأقل أولاً)</option>
              <option value="relevance">الأكثر ملاءمة</option>
            </select>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
          <p class="text-gray-600 dark:text-gray-400 mt-4">جاري البحث عن الوظائف...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <div>
              <p class="text-red-800 dark:text-red-200 font-medium">خطأ</p>
              <p class="text-red-700 dark:text-red-300 text-sm mt-1">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="jobs.length === 0" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-12 text-center">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">لم يتم العثور على وظائف</h3>
          <p class="text-gray-600 dark:text-gray-400">حاول تغيير معايير البحث والتصفية</p>
        </div>

        <!-- Jobs List -->
        <div v-else class="space-y-4">
          <JobCard
            v-for="job in jobs"
            :key="job.job_id"
            :job="job"
            :is-saved="isSaved(job.job_id)"
            @toggle-save="toggleSaveJob(job.job_id)"
            @view-details="goToJobDetails(job.job_id)"
          />
        </div>

        <!-- Pagination Component -->
        <Pagination
          v-if="jobs.length > 0"
          :current-page="currentPage"
          :page-size="pageSize"
          :total-items="totalJobs"
          @update:current-page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          @page-change="searchJobs"
          @page-size-change="searchJobs"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import { apiClient } from '@/services/api'
import SearchBar from '@/components/search/SearchBar.vue'
import FilterPanel from '@/components/search/FilterPanel.vue'
import Pagination from '@/components/search/Pagination.vue'
import JobCard from '@/components/cards/JobCard.vue'

const router = useRouter()
const route = useRoute()
const jobsStore = useJobsStore()

const loading = ref(false)
const error = ref('')
const jobs = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(25)
const totalJobs = ref(0)
const sortBy = ref('recent')

const searchQuery = ref((route.query.q as string) || '')
const selectedSite = ref((route.query.site as string) || '')

const searchFilters = ref({
  jobTypes: [],
  remote: [],
  experienceLevel: '',
  postedDate: ''
})

const filterState = ref({
  minSalary: 0,
  maxSalary: 500000,
  location: '',
  jobTypes: [],
  remote: [],
  experienceLevel: '',
  postedDate: '',
  companySizes: []
})

/**
 * Check if a job is saved
 * Validates: Requirements 5.1, 5.3
 */
const isSaved = (jobId: string) => {
  return jobsStore.savedJobs.some(job => job.job_id === jobId)
}

/**
 * Handle search form submission
 * Resets pagination and triggers search
 */
const handleSearch = async () => {
  currentPage.value = 1
  await searchJobs()
}

/**
 * Handle filter changes
 * Resets pagination and triggers search
 */
const handleFilterChange = async () => {
  currentPage.value = 1
  await searchJobs()
}

/**
 * Handle sort order change
 * Triggers search with new sort order
 */
const handleSortChange = async () => {
  currentPage.value = 1
  await searchJobs()
}

/**
 * Update filter state
 */
const updateFilters = (newFilters: any) => {
  filterState.value = newFilters
}

/**
 * Handle page change
 */
const handlePageChange = (page: number) => {
  currentPage.value = page
}

/**
 * Handle page size change
 */
const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

/**
 * Build sort parameter for API
 */
const getSortParam = (): string => {
  const sortMap: Record<string, string> = {
    recent: 'posted_date:desc',
    'salary-high': 'salary_max:desc',
    'salary-low': 'salary_min:asc',
    relevance: 'relevance:desc'
  }
  return sortMap[sortBy.value] || 'posted_date:desc'
}

/**
 * Search jobs with current criteria
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4, 3.2, 3.3, 3.4, 8.5
 */
const searchJobs = async () => {
  loading.value = true
  error.value = ''

  try {
    // Build query parameters
    const params: any = {
      page: currentPage.value,
      limit: pageSize.value,
      sort: getSortParam()
    }

    // Add search query
    if (searchQuery.value) {
      params.q = searchQuery.value
    }

    // Add site filter
    if (selectedSite.value) {
      params.site_name = selectedSite.value
    }

    // Add location filter
    if (filterState.value.location) {
      params.location = filterState.value.location
    }

    // Add job type filters
    if (filterState.value.jobTypes.length > 0) {
      params.job_types = filterState.value.jobTypes.join(',')
    }

    // Add remote filter
    if (filterState.value.remote.length > 0) {
      params.remote = filterState.value.remote.includes('remote')
    }

    // Add salary range filters
    if (filterState.value.minSalary > 0) {
      params.salary_min = filterState.value.minSalary
    }
    if (filterState.value.maxSalary < 500000) {
      params.salary_max = filterState.value.maxSalary
    }

    // Add experience level filter
    if (filterState.value.experienceLevel) {
      params.experience_level = filterState.value.experienceLevel
    }

    // Add posted date filter
    if (filterState.value.postedDate) {
      params.hours_old = parseInt(filterState.value.postedDate) * 24
    }

    // Add company size filters
    if (filterState.value.companySizes.length > 0) {
      params.company_sizes = filterState.value.companySizes.join(',')
    }

    // Call API
    const response = await apiClient.get('/jobs', { params })

    jobs.value = response.data.results || response.data.jobs || []
    totalJobs.value = response.data.total || response.data.count || 0
  } catch (err: any) {
    console.error('Search error:', err)
    error.value = err.response?.data?.detail || 'فشل البحث عن الوظائف. يرجى المحاولة مرة أخرى.'
    jobs.value = []
    totalJobs.value = 0
  } finally {
    loading.value = false
  }
}

/**
 * Toggle save job
 * Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
 */
const toggleSaveJob = async (jobId: string) => {
  try {
    if (isSaved(jobId)) {
      await jobsStore.removeSavedJob(jobId)
    } else {
      // Find the job to save
      const jobToSave = jobs.value.find(j => j.job_id === jobId)
      if (jobToSave) {
        await jobsStore.addSavedJob(jobToSave)
      }
    }
  } catch (err) {
    error.value = 'فشل حفظ الوظيفة'
  }
}

/**
 * Navigate to job details page
 */
const goToJobDetails = (jobId: string) => {
  router.push({ name: 'JobDetails', params: { id: jobId } })
}

/**
 * Watch for route query changes
 */
watch(
  () => route.query,
  (newQuery) => {
    if (newQuery.q) {
      searchQuery.value = newQuery.q as string
      handleSearch()
    }
  }
)

/**
 * Initialize on mount
 */
onMounted(() => {
  if (searchQuery.value) {
    searchJobs()
  }
})
</script>
