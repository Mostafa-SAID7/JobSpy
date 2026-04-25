<template>
  <div class="space-y-8 pb-12">
    <!-- Page Header -->
    <div class="relative overflow-hidden py-12 px-6 rounded-2xl bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-950 border border-gray-100 dark:border-gray-800 shadow-sm mb-8">
      <div class="relative z-10 max-w-3xl">
        <h1 class="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Explore Your <span class="text-[#0078d4]">Next Career</span>
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-4 max-w-xl leading-relaxed">
          Discover thousands of job opportunities across multiple platforms, aggregated and filtered just for you.
        </p>
      </div>
      <!-- Subtle Decorative Background -->
      <div class="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-[#0078d4]/5 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Search Bar Section -->
    <div class="max-w-5xl mx-auto -mt-16 relative z-20">
      <div class="fluent-card bg-white dark:bg-gray-900 p-6 shadow-2xl border border-gray-100 dark:border-gray-800">
        <SearchBar
          v-model="searchQuery"
          v-model:site="selectedSite"
          v-model:filters="searchFilters"
          @search="handleSearch"
        />
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-12">
      <!-- Filters Sidebar -->
      <aside class="lg:col-span-3 space-y-6">
        <FilterPanel
          :filters="filterState"
          @update:filters="updateFilters"
          @filter-change="handleFilterChange"
        />
      </aside>

      <!-- Jobs List Area -->
      <main class="lg:col-span-9">
        <!-- Results Controls -->
        <div v-if="jobs.length > 0 || loading" class="flex flex-col sm:flex-row justify-between items-center mb-6 px-4 py-3 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded shadow-sm">
          <div class="flex items-center space-x-3 mb-4 sm:mb-0">
            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Found <span class="text-gray-900 dark:text-white font-bold">{{ totalJobs }}</span> matching positions
            </span>
            <div v-if="loading" class="w-4 h-4 border-2 border-[#0078d4] border-t-transparent rounded-full animate-spin"></div>
          </div>
          
          <div class="flex items-center gap-3">
            <label for="sort-select" class="text-xs font-bold text-gray-400 uppercase tracking-widest px-1">Sort By</label>
            <div class="relative min-w-[160px]">
              <select
                id="sort-select"
                v-model="sortBy"
                class="w-full appearance-none px-4 py-1.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded text-sm font-medium focus:ring-2 focus:ring-[#0078d4]/20 focus:border-[#0078d4] dark:text-white transition-all cursor-pointer"
                @change="handleSortChange"
              >
                <option value="recent">Newest First</option>
                <option value="salary-high">High Salary</option>
                <option value="salary-low">Low Salary</option>
                <option value="relevance">Relevance</option>
              </select>
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Job Display -->
        <div class="relative min-h-[400px]">
          <!-- Loading State -->
          <transition name="fade">
            <div v-if="loading" class="space-y-4">
              <div v-for="i in 5" :key="i" class="h-32 bg-gray-100 dark:bg-gray-800 animate-pulse rounded-lg border border-gray-200 dark:border-gray-700"></div>
            </div>

            <!-- Content -->
            <div v-else>
              <!-- Error State -->
              <ErrorState v-if="error" :message="error" />

              <!-- Empty State -->
              <EmptyState v-else-if="jobs.length === 0" title="No matching jobs" message="We couldn't find any jobs matching your current search. Try adjusting your filters or keywords." />

              <!-- Jobs List -->
              <div v-else class="space-y-5">
                <transition-group name="list" tag="div" class="space-y-4">
                  <JobCard
                    v-for="job in jobs"
                    :key="job.id"
                    :job="job"
                    :is-saved="isSaved(job.id)"
                    @toggle-save="toggleSaveJob(job.id)"
                    @view-details="goToJobDetails(job.id)"
                  />
                </transition-group>
              </div>

              <!-- Pagination -->
              <div class="mt-12 flex justify-center">
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
          </transition>
        </div>
      </main>
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
