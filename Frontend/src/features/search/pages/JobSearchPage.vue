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
            <label class="text-xs font-bold text-gray-400 uppercase tracking-widest px-1">Sort By</label>
            <FormSelect
              v-model="sortBy"
              :options="sortOptions"
              @update:model-value="handleSortChange"
            />
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
import { useJobsStore } from '@/features/jobs/stores/jobs'
import { apiClient } from '@/shared/services/api'
import SearchBar from '@/features/search/components/SearchBar.vue'
import FilterPanel from '@/features/search/components/FilterPanel.vue'
import Pagination from '@/features/search/components/Pagination.vue'
import JobCard from '@/features/jobs/components/JobCard.vue'
import ErrorState from '@/shared/components/common/ErrorState.vue'
import EmptyState from '@/shared/components/common/EmptyState.vue'
import FormSelect from '@/shared/components/ui/FormSelect.vue'
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

const sortOptions = [
  { label: 'Newest First', value: 'recent' },
  { label: 'High Salary', value: 'salary-high' },
  { label: 'Low Salary', value: 'salary-low' },
  { label: 'Relevance', value: 'relevance' }
]

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
 * Search jobs with current criteria
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4, 3.2, 3.3, 3.4, 8.5
 */
const searchJobs = async () => {
  loading.value = true
  error.value = ''

  try {
    let response

    console.log('🔍 Starting job search...', { 
      searchQuery: searchQuery.value, 
      currentPage: currentPage.value, 
      pageSize: pageSize.value 
    })

    // If there's a search query, use the search endpoint
    if (searchQuery.value.trim()) {
      const params: any = {
        query: searchQuery.value.trim(),
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }

      console.log('📡 Making search API call with params:', params)
      response = await apiClient.post('/jobs/search', null, { params })
    } else {
      // Otherwise, use the list endpoint
      const params: any = {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }

      // Add source filter if site is selected
      if (selectedSite.value) {
        params.source = selectedSite.value
      }

      console.log('📡 Making list API call with params:', params)
      response = await apiClient.get('/jobs', { params })
    }

    console.log('✅ API response received:', {
      status: response.status,
      dataKeys: Object.keys(response.data),
      total: response.data.total,
      itemsLength: response.data.items?.length
    })

    jobs.value = response.data.items || []
    totalJobs.value = response.data.total || 0

    console.log('📊 Updated state:', {
      jobsCount: jobs.value.length,
      totalJobs: totalJobs.value,
      firstJobTitle: jobs.value[0]?.title
    })
  } catch (err: any) {
    console.error('❌ Search error:', err)
    console.error('Error details:', {
      status: err.response?.status,
      statusText: err.response?.statusText,
      data: err.response?.data
    })
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
      await jobsStore.removeSavedJob(jobId)
    } else {
      // Find the job to save
      const jobToSave = jobs.value.find(j => j.id == jobId)
      if (jobToSave) {
        await jobsStore.addSavedJob(jobToSave.id)
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
  // Always load jobs on mount, either with search query or all jobs
  searchJobs()
})
</script>
