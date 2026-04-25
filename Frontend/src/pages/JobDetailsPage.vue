<template>
  <div class="space-y-6">
    <!-- Back Button -->
    <button
      @click="goBack"
      class="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
      aria-label="Return to previous page"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back
    </button>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <ErrorState v-if="error" :message="error" />

    <!-- Success Toast -->
    <div v-if="successMessage" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
      <p class="text-green-800 dark:text-green-200">{{ successMessage }}</p>
    </div>

    <!-- Job Details -->
    <div v-if="job && !loading" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Job Header -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ job.title }}</h1>
              <p class="text-gray-600 dark:text-gray-400 mt-2">{{ job.company }}</p>
            </div>
            <div class="text-right">
              <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ formatSalary() }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Salary</p>
            </div>
          </div>

          <!-- Job Meta -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Location</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.location || 'Not specified' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Job Type</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ formatJobType(job.job_type) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Experience Level</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.experience_level || 'Not specified' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Work</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.is_remote ? 'Remote' : 'On-site' }}</p>
            </div>
          </div>
        </div>

        <!-- Job Description -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Job Description</h2>
          <div class="prose dark:prose-invert max-w-none">
            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ job.description || 'No description available' }}</p>
          </div>
        </div>

        <!-- Skills -->
        <div v-if="job.skills && job.skills.length > 0" class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Required Skills</h2>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(skill, idx) in job.skills"
              :key="idx"
              class="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm"
            >
              {{ skill }}
            </span>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="lg:col-span-1 space-y-4">
        <!-- Action Buttons -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm space-y-3">
          <FormButton
            variant="primary"
            class="w-full"
            :loading="applyLoading"
            :disabled="applyLoading || saveLoading"
            @click="handleApply"
            label="Apply"
            aria-label="Apply for this job"
          />

          <FormButton
            :variant="isSaved ? 'danger' : 'secondary'"
            class="w-full"
            :loading="saveLoading"
            :disabled="applyLoading || saveLoading"
            @click="toggleSave"
            :label="isSaved ? 'Saved' : 'Save Job'"
            aria-label="Save or remove job from list"
          />
        </div>

        <!-- Company Info -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h3 class="font-bold text-gray-900 dark:text-white mb-4">Company Information</h3>
          <div class="space-y-3">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Company</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.company }}</p>
            </div>
            <div v-if="job.company_website">
              <p class="text-sm text-gray-600 dark:text-gray-400">Website</p>
              <a
                :href="job.company_website"
                target="_blank"
                rel="noopener noreferrer"
                class="font-semibold text-blue-600 dark:text-blue-400 hover:underline"
              >
                Visit Website
              </a>
            </div>
          </div>
        </div>

        <!-- Posted Date -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <p class="text-sm text-gray-600 dark:text-gray-400">Posted Date</p>
          <p class="font-semibold text-gray-900 dark:text-white">{{ formatDate(job.posted_date) }}</p>
        </div>

        <!-- Source -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <p class="text-sm text-gray-600 dark:text-gray-400">Source</p>
          <p class="font-semibold text-gray-900 dark:text-white capitalize">{{ job.site_name }}</p>
        </div>
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
