<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Saved Jobs</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">Manage jobs you saved for later review</p>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <ErrorState v-else-if="error" :message="error" />

    <!-- Empty State -->
    <EmptyState
      v-else-if="savedJobs.length === 0"
      title="You haven't saved any jobs yet"
      message="Start saving jobs you're interested in to return to them later"
      action-text="Search for Jobs"
      action-route="/jobs"
    >
      <template #icon>
        <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 19V5z" />
        </svg>
      </template>
    </EmptyState>

    <!-- Saved Jobs List -->
    <div v-else class="space-y-4">
      <!-- Filter and Sort -->
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search saved jobs..."
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          v-model="sortBy"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="recent">Newest First</option>
          <option value="salary-high">Salary (Highest First)</option>
          <option value="salary-low">Salary (Lowest First)</option>
          <option value="title">Name (A-Z)</option>
        </select>
      </div>

      <!-- Jobs Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="job in filteredJobs"
          :key="job.id"
          class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
          @click="goToJobDetails(job.id)"
        >
          <!-- Header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="font-bold text-gray-900 dark:text-white">{{ job.title }}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ job.company }}</p>
            </div>
            <button
              @click.stop="removeSavedJob(job.id)"
              class="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <!-- Meta Info -->
          <div class="space-y-2 mb-4 text-sm">
            <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
              {{ job.location }}
            </div>
            <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ getJobTypeLabel(job.job_type) }}
            </div>
          </div>

          <!-- Salary and Date -->
          <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Salary</p>
              <p class="font-bold text-gray-900 dark:text-white">{{ formatSalary(job) }}</p>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500 dark:text-gray-500">{{ formatDate(job.posted_date) }}</p>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="job.notes" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p class="text-sm text-gray-600 dark:text-gray-400">My Notes:</p>
            <p class="text-sm text-gray-700 dark:text-gray-300 mt-1">{{ job.notes }}</p>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <Pagination
        v-if="filteredJobs.length > 0"
        :current-page="currentPage"
        :page-size="pageSize"
        :total-items="filteredJobs.length"
        @update:current-page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import Pagination from '@/components/search/Pagination.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const jobsStore = useJobsStore()

const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const sortBy = ref('recent')
const currentPage = ref(1)
const pageSize = ref(12)

const savedJobs = computed(() => jobsStore.savedJobs)

const filteredJobs = computed(() => {
  let filtered = savedJobs.value.filter(job =>
    job.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    job.company.toLowerCase().includes(searchQuery.value.toLowerCase())
  )

  // Sort
  switch (sortBy.value) {
    case 'salary-high':
      filtered.sort((a, b) => (b.salary_max || 0) - (a.salary_max || 0))
      break
    case 'salary-low':
      filtered.sort((a, b) => (a.salary_min || 0) - (b.salary_min || 0))
      break
    case 'title':
      filtered.sort((a, b) => a.title.localeCompare(b.title, 'en'))
      break
    case 'recent':
    default:
      filtered.sort((a, b) => new Date(b.posted_date).getTime() - new Date(a.posted_date).getTime())
  }


  // Paginate
  const start = (currentPage.value - 1) * pageSize.value
  return filtered.slice(start, start + pageSize.value)
})

const formatSalary = (job: any) => {
  if (!job.salary_min && !job.salary_max) return 'Not specified'
  
  const min = job.salary_min || 0
  const max = job.salary_max || 0
  
  if (min === 0 && max === 0) return 'Not specified'
  if (min === 0) return `Up to ${max.toLocaleString('en-US')}`
  if (max === 0) return `From ${min.toLocaleString('en-US')}`
  
  return `${min.toLocaleString('en-US')} - ${max.toLocaleString('en-US')}`
}

const formatDate = (date: string) => {
  const now = new Date()
  const jobDate = new Date(date)
  const diffTime = Math.abs(now.getTime() - jobDate.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return `${Math.floor(diffDays / 30)} months ago`
}

const getJobTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    fulltime: 'Full-time',
    parttime: 'Part-time',
    internship: 'Internship',
    contract: 'Contract',
  }
  return labels[type] || type
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const removeSavedJob = async (jobId: string) => {
  try {
    // Find the saved job ID from the job ID
    const savedJob = savedJobs.value.find(j => j.id === jobId)
    if (savedJob) {
      await jobsStore.removeSavedJob(jobId)
    }
  } catch (err) {
    error.value = 'Failed to delete job'
  }
}

const goToJobDetails = (jobId: string) => {
  router.push({ name: 'JobDetails', params: { id: jobId } })
}

onMounted(async () => {
  loading.value = true
  try {
    await jobsStore.fetchSavedJobs()
  } catch (err) {
    error.value = 'Failed to load saved jobs'
  } finally {
    loading.value = false
  }
})
</script>
