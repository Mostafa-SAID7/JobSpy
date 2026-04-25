<template>
  <div class="space-y-8 pb-12">
    <!-- Page Header -->
    <div class="relative overflow-hidden py-12 px-6 rounded-2xl bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-950 border border-gray-100 dark:border-gray-800 shadow-sm mb-8">
      <div class="relative z-10 max-w-3xl">
        <h1 class="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Your <span class="text-[#0078d4]">Saved Careers</span>
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-4 max-w-xl leading-relaxed">
          Manage and track the job opportunities you've bookmarked for later consideration.
        </p>
      </div>
      <div class="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-[#0078d4]/5 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <ErrorState v-else-if="error" :message="error" />

    <!-- Content Area -->
    <div v-else>
      <!-- Empty State -->
      <EmptyState
        v-if="savedJobs.length === 0"
        title="No saved jobs yet"
        message="Start exploring and save jobs you're interested in to build your shortlist."
        action-text="Browse Jobs"
        action-route="/jobs"
      >
        <template #icon>
          <div class="w-20 h-20 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6 border border-gray-100 dark:border-gray-700">
            <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 5a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 19V5z" />
            </svg>
          </div>
        </template>
      </EmptyState>

      <!-- Saved Jobs List -->
      <div v-else class="space-y-8">
        <!-- Controls Bar -->
        <div class="flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between bg-white dark:bg-gray-900 p-4 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm">
          <div class="flex-1 relative group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="w-4 h-4 text-gray-400 group-focus-within:text-[#0078d4] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Filter by title or company..."
              class="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-transparent focus:border-[#0078d4] rounded text-sm focus:ring-4 focus:ring-[#0078d4]/10 dark:text-white transition-all shadow-inner"
            />
          </div>
          
          <div class="flex items-center gap-3">
            <label class="text-xs font-bold text-gray-400 uppercase tracking-widest px-1">Sort</label>
            <div class="relative min-w-[160px]">
              <select
                v-model="sortBy"
                class="w-full appearance-none px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-transparent focus:border-[#0078d4] rounded text-sm font-medium focus:ring-4 focus:ring-[#0078d4]/10 dark:text-white transition-all cursor-pointer"
              >
                <option value="recent">Date Added</option>
                <option value="salary-high">Max Salary</option>
                <option value="salary-low">Min Salary</option>
                <option value="title">Job Title</option>
              </select>
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Jobs Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <transition-group name="list">
            <div
              v-for="job in filteredJobs"
              :key="job.id"
              class="fluent-card group bg-white dark:bg-gray-900 rounded border border-gray-100 dark:border-gray-800 p-6 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all cursor-pointer relative overflow-hidden"
              @click="goToJobDetails(job.id)"
            >
              <!-- Hover Accent -->
              <div class="absolute top-0 left-0 w-1 h-full bg-[#0078d4] transform scale-y-0 group-hover:scale-y-100 transition-transform origin-top"></div>

              <!-- Content -->
              <div class="flex items-start justify-between mb-6">
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 dark:text-white group-hover:text-[#0078d4] transition-colors leading-tight mb-1">{{ job.title }}</h3>
                  <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ job.company }}</p>
                </div>
                <button
                  @click.stop="removeSavedJob(job.id)"
                  class="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-all"
                  title="Remove from saved"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>

              <div class="space-y-3 mb-6">
                <div class="flex items-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-widest">
                  <svg class="w-3.5 h-3.5 mr-2 text-[#0078d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                  {{ job.location }}
                </div>
                <div class="flex items-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-widest">
                  <svg class="w-3.5 h-3.5 mr-2 text-[#0078d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ getJobTypeLabel(job.job_type) }}
                </div>
              </div>

              <div class="pt-5 border-t border-gray-100 dark:border-gray-800 flex justify-between items-end">
                <div>
                  <span class="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter mb-1">Target Salary</span>
                  <span class="text-sm font-extrabold text-gray-900 dark:text-white">{{ formatSalary(job) }}</span>
                </div>
                <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
                  {{ formatDate(job.posted_date) }}
                </span>
              </div>
            </div>
          </transition-group>
        </div>

        <!-- Pagination -->
        <div class="pt-8">
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
