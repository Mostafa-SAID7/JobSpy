<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Search for Jobs</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">Find the right job for you from thousands of available opportunities</p>
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
            Number of results: <span class="font-semibold">{{ totalJobs }}</span>
          </div>
          <div class="flex items-center gap-2">
            <label for="sort-select" class="text-sm text-gray-700 dark:text-gray-300">Sort by:</label>
            <select
              id="sort-select"
              v-model="sortBy"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-sm"
              @change="handleSortChange"
            >
              <option value="recent">Newest First</option>
              <option value="salary-high">Salary (Highest First)</option>
              <option value="salary-low">Salary (Lowest First)</option>
              <option value="relevance">Most Relevant</option>
            </select>
          </div>
        </div>

        <!-- Loading State -->
        <LoadingSpinner v-if="loading" text="Searching for jobs..." />

        <!-- Error State -->
        <ErrorState v-else-if="error" :message="error" />

        <!-- Empty State -->
        <EmptyState v-else-if="jobs.length === 0" title="No jobs found" message="Try changing your search and filter criteria" />

        <!-- Jobs List -->
        <div v-else class="space-y-4">
          <JobCard
            v-for="job in jobs"
            :key="job.id"
            :job="job"
            :is-saved="isSaved(job.id)"
            @toggle-save="toggleSaveJob(job.id)"
            @view-details="goToJobDetails(job.id)"
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
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import type { Job } from '@/types'

const router = useRouter()
const route = useRoute()
const jobsStore = useJobsStore()

const loading = ref(false)
const error = ref('')
const jobs = ref<Job[]>([])
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
  jobTypes: [] as string[],
  remote: [] as string[],
  experienceLevel: '',
  postedDate: '',
  companySizes: [] as string[]
})

/**
 * Check if a job is saved
 * Validates: Requirements 5.1, 5.3
 */
const isSaved = (jobId: string | number) => {
  return jobsStore.savedJobs.some(job => job.id === Number(jobId))
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
    error.value = err.response?.data?.detail || 'Failed to search for jobs. Please try again.'
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
const toggleSaveJob = async (jobId: string | number) => {
  try {
    if (isSaved(jobId)) {
      await jobsStore.removeSavedJob(Number(jobId))
    } else {
      // Find the job to save
      const jobToSave = jobs.value.find(j => j.id === Number(jobId))
      if (jobToSave) {
        await jobsStore.addSavedJob(jobToSave)
      }
    }
  } catch (err) {
    error.value = 'Failed to save job'
  }
}

/**
 * Navigate to job details page
 */
const goToJobDetails = (jobId: string | number) => {
  router.push({ name: 'JobDetails', params: { id: String(jobId) } })
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
