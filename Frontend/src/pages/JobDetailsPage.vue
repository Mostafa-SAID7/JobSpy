<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-16">
    <!-- Navigation & Status Area -->
    <div class="flex items-center justify-between">
      <button
        @click="goBack"
        class="group flex items-center gap-2 text-gray-500 hover:text-[#0078d4] font-bold text-sm transition-all"
      >
        <svg class="w-4 h-4 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Search
      </button>

      <div v-if="job" class="flex items-center gap-2">
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Job Source:</span>
        <span class="px-2 py-0.5 bg-[#0078d4]/10 text-[#0078d4] rounded text-xs font-bold uppercase tracking-tight">
          {{ job.site_name }}
        </span>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div v-if="job && !loading" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left Column: Details -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Header Card -->
        <div class="fluent-card bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800">
          <div class="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
            <div class="flex-1">
              <h1 class="text-4xl font-extrabold text-gray-900 dark:text-white leading-tight tracking-tight mb-3">
                {{ job.title }}
              </h1>
              <div class="flex items-center gap-3">
                <span class="text-xl font-bold text-[#0078d4]">{{ job.company }}</span>
                <span class="text-gray-300 dark:text-gray-700">|</span>
                <span class="text-gray-500 dark:text-gray-400 font-medium">{{ job.location || 'Remote' }}</span>
              </div>
            </div>
            <div class="flex flex-col items-end">
              <div class="text-2xl font-black text-[#107c10] tracking-tighter">
                {{ formatSalary() }}
              </div>
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">Est. Compensation</span>
            </div>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-8 border-t border-gray-50 dark:border-gray-800">
            <div class="space-y-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Type</span>
              <p class="font-bold text-gray-800 dark:text-gray-200">{{ formatJobType(job.job_type) }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Level</span>
              <p class="font-bold text-gray-800 dark:text-gray-200">{{ job.experience_level || 'Mid Level' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Remote</span>
              <p class="font-bold text-gray-800 dark:text-gray-200">{{ job.is_remote ? 'Available' : 'On-site' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Posted</span>
              <p class="font-bold text-gray-800 dark:text-gray-200">{{ formatDate(job.posted_date) }}</p>
            </div>
          </div>
        </div>

        <!-- Description Card -->
        <div class="fluent-card bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800">
          <h2 class="text-xl font-black text-gray-900 dark:text-white mb-6 flex items-center gap-3">
            <div class="w-1.5 h-6 bg-[#0078d4] rounded-full"></div>
            Role Overview
          </h2>
          <div class="prose dark:prose-invert max-w-none">
            <p class="text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-wrap font-medium">
              {{ job.description || 'Detailed description is available on the source website.' }}
            </p>
          </div>
        </div>

        <!-- Skills Section -->
        <div v-if="job.skills && job.skills.length > 0" class="fluent-card bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800">
          <h2 class="text-xl font-black text-gray-900 dark:text-white mb-6 flex items-center gap-3">
            <div class="w-1.5 h-6 bg-[#0078d4] rounded-full"></div>
            Required Expertise
          </h2>
          <div class="flex flex-wrap gap-2.5">
            <span
              v-for="(skill, idx) in job.skills"
              :key="idx"
              class="px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-bold hover:border-[#0078d4] hover:text-[#0078d4] transition-all cursor-default"
            >
              {{ skill }}
            </span>
          </div>
        </div>
      </div>

      <!-- Right Column: Sidebar -->
      <aside class="space-y-6">
        <!-- Application Card -->
        <div class="fluent-card bg-white dark:bg-gray-900 p-6 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 sticky top-8">
          <div class="space-y-4">
            <FormButton
              variant="primary"
              class="w-full !py-4 text-base shadow-lg shadow-blue-500/20"
              :loading="applyLoading"
              :disabled="applyLoading || saveLoading"
              @click="handleApply"
            >
              Apply via {{ job.site_name }}
              <template #icon>
                <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </template>
            </FormButton>

            <FormButton
              :variant="isSaved ? 'secondary' : 'secondary'"
              class="w-full !py-4"
              :loading="saveLoading"
              :disabled="applyLoading || saveLoading"
              @click="toggleSave"
              :class="isSaved ? 'bg-red-50 dark:bg-red-900/20 text-red-600 border-red-100' : ''"
            >
              {{ isSaved ? 'Remove from Saved' : 'Save for Later' }}
            </FormButton>

            <p class="text-[10px] text-center text-gray-400 font-bold uppercase tracking-widest mt-4">
              Direct Application Guaranteed
            </p>
          </div>

          <div class="mt-8 pt-8 border-t border-gray-50 dark:border-gray-800 space-y-6">
            <div>
              <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-3">About the Company</h3>
              <p class="font-bold text-gray-900 dark:text-white">{{ job.company }}</p>
              <a 
                v-if="job.company_website"
                :href="job.company_website" 
                target="_blank"
                class="text-sm font-bold text-[#0078d4] hover:underline mt-2 inline-block"
              >
                Explore Organization
              </a>
            </div>

            <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
              <div>
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Posted</span>
                <span class="text-xs font-bold text-gray-800 dark:text-gray-200">{{ formatDate(job.posted_date) }}</span>
              </div>
              <div class="text-right">
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">ID</span>
                <span class="text-xs font-bold text-gray-800 dark:text-gray-200">#{{ String(job.id).slice(-6) }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-32 space-y-4">
      <div class="w-12 h-12 border-4 border-[#0078d4] border-t-transparent rounded-full animate-spin"></div>
      <p class="text-sm font-bold text-gray-400 uppercase tracking-widest">Loading Job Details</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="max-w-lg mx-auto py-20 text-center">
      <div class="p-8 fluent-card bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 rounded-2xl">
        <svg class="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 class="text-xl font-bold text-red-900 dark:text-red-400 mb-2">Something went wrong</h3>
        <p class="text-red-700 dark:text-red-500 text-sm font-medium mb-6">{{ error }}</p>
        <FormButton variant="danger" size="sm" @click="fetchJobDetails" label="Try Again" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import { apiClient } from '@/services/api'
import type { Job } from '@/types'
import FormButton from '@/components/forms/FormButton.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorState from '@/components/common/ErrorState.vue'

const router = useRouter()
const route = useRoute()
const jobsStore = useJobsStore()

const loading = ref(false)
const error = ref('')
const successMessage = ref('')
const job = ref<Job | null>(null)
const isSaved = ref(false)
const applyLoading = ref(false)
const saveLoading = ref(false)

/**
 * Format salary range with currency
 * Validates: Requirement 1.4 - Display all required job fields including salary
 */
const formatSalary = (): string => {
  if (!job.value) return 'Not specified'

  const { salary_min, salary_max, salary_currency } = job.value

  if (!salary_min && !salary_max) {
    return 'Not specified'
  }

  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: salary_currency || 'USD',
    minimumFractionDigits: 0,
  })

  if (salary_min && salary_max) {
    return `${formatter.format(salary_min)} - ${formatter.format(salary_max)}`
  }

  return formatter.format(salary_min || salary_max || 0)
}

/**
 * Format job type to English
 */
const formatJobType = (jobType: string): string => {
  const typeMap: Record<string, string> = {
    fulltime: 'Full-time',
    parttime: 'Part-time',
    internship: 'Internship',
    contract: 'Contract',
  }
  return typeMap[jobType] || jobType
}

/**
 * Format date to English locale
 */
const formatDate = (date: string): string => {
  try {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(new Date(date))
  } catch {
    return 'Invalid date'
  }
}

/**
 * Navigate back to previous page
 */
const goBack = (): void => {
  router.back()
}

/**
 * Handle job application
 * Opens job URL in new tab
 * Validates: Requirement 8.5 - Apply button from UI succeeds
 */
const handleApply = async (): Promise<void> => {
  if (!job.value?.source_url) {
    error.value = 'Job link not available'
    return
  }

  try {
    applyLoading.value = true
    error.value = ''

    // Open job URL in new tab
    window.open(job.value.source_url, '_blank', 'noopener,noreferrer')

    successMessage.value = 'Job page opened. Please complete the application on the original site.'

    // Clear success message after 5 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (err: any) {
    error.value = 'Failed to open job page'
  } finally {
    applyLoading.value = false
  }
}

/**
 * Toggle save/unsave job
 * Validates: Requirement 5.1 - Save job functionality
 * Validates: Requirement 5.3 - Display saved jobs
 * Validates: Requirement 8.5 - Save button from UI succeeds
 */
const toggleSave = async (): Promise<void> => {
  if (!job.value) return

  try {
    saveLoading.value = true
    error.value = ''

    if (isSaved.value) {
      // Remove from saved jobs
      await jobsStore.removeSavedJob(job.value.id.toString())
      successMessage.value = 'Job removed from list'
    } else {
      // Add to saved jobs
      await jobsStore.addSavedJob(job.value)
      successMessage.value = 'Job saved successfully'
    }

    isSaved.value = !isSaved.value

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to save job'
  } finally {
    saveLoading.value = false
  }
}

/**
 * Fetch job details from API
 * Validates: Requirement 1.4 - Display all required job fields
 */
const fetchJobDetails = async (): Promise<void> => {
  loading.value = true
  error.value = ''

  try {
    const jobId = route.params.id as string

    // Fetch job details from API
    const response = await apiClient.get(`/jobs/${jobId}`)
    job.value = response.data

    // Check if job is already saved
    isSaved.value = jobsStore.savedJobs.some(j => j.id === job.value?.id)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load job details'
    console.error('Error fetching job details:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJobDetails()
})
</script>
