<template>
  <div class="space-y-6">
    <!-- Back Button -->
    <button
      @click="goBack"
      class="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
      aria-label="العودة للصفحة السابقة"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      العودة
    </button>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

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
              <p class="text-sm text-gray-600 dark:text-gray-400">الراتب</p>
            </div>
          </div>

          <!-- Job Meta -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">الموقع</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.location || 'غير محدد' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">نوع الوظيفة</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ formatJobType(job.job_type) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">مستوى الخبرة</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.experience_level || 'غير محدد' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">العمل</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.is_remote ? 'عن بعد' : 'في المقر' }}</p>
            </div>
          </div>
        </div>

        <!-- Job Description -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">وصف الوظيفة</h2>
          <div class="prose dark:prose-invert max-w-none">
            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ job.description || 'لا يوجد وصف متاح' }}</p>
          </div>
        </div>

        <!-- Skills -->
        <div v-if="job.skills && job.skills.length > 0" class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">المهارات المطلوبة</h2>
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
            label="تقديم الطلب"
            aria-label="تقديم طلب للوظيفة"
          />

          <FormButton
            :variant="isSaved ? 'danger' : 'secondary'"
            class="w-full"
            :loading="saveLoading"
            :disabled="applyLoading || saveLoading"
            @click="toggleSave"
            :label="isSaved ? 'تم الحفظ' : 'حفظ الوظيفة'"
            aria-label="حفظ أو إزالة الوظيفة من القائمة"
          />
        </div>

        <!-- Company Info -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h3 class="font-bold text-gray-900 dark:text-white mb-4">معلومات الشركة</h3>
          <div class="space-y-3">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">الشركة</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ job.company }}</p>
            </div>
            <div v-if="job.company_website">
              <p class="text-sm text-gray-600 dark:text-gray-400">الموقع الإلكتروني</p>
              <a
                :href="job.company_website"
                target="_blank"
                rel="noopener noreferrer"
                class="font-semibold text-blue-600 dark:text-blue-400 hover:underline"
              >
                زيارة الموقع
              </a>
            </div>
          </div>
        </div>

        <!-- Posted Date -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <p class="text-sm text-gray-600 dark:text-gray-400">تاريخ النشر</p>
          <p class="font-semibold text-gray-900 dark:text-white">{{ formatDate(job.posted_date) }}</p>
        </div>

        <!-- Source -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <p class="text-sm text-gray-600 dark:text-gray-400">المصدر</p>
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
  if (!job.value) return 'غير محدد'

  const { salary_min, salary_max, salary_currency } = job.value

  if (!salary_min && !salary_max) {
    return 'غير محدد'
  }

  const formatter = new Intl.NumberFormat('ar-EG', {
    style: 'currency',
    currency: salary_currency || 'EGP',
    minimumFractionDigits: 0,
  })

  if (salary_min && salary_max) {
    return `${formatter.format(salary_min)} - ${formatter.format(salary_max)}`
  }

  return formatter.format(salary_min || salary_max || 0)
}

/**
 * Format job type to Arabic
 */
const formatJobType = (jobType: string): string => {
  const typeMap: Record<string, string> = {
    fulltime: 'دوام كامل',
    parttime: 'دوام جزئي',
    internship: 'تدريب',
    contract: 'عقد',
  }
  return typeMap[jobType] || jobType
}

/**
 * Format date to Arabic locale
 */
const formatDate = (date: string): string => {
  try {
    return new Intl.DateTimeFormat('ar-EG', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(new Date(date))
  } catch {
    return 'تاريخ غير صحيح'
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
    error.value = 'رابط الوظيفة غير متاح'
    return
  }

  try {
    applyLoading.value = true
    error.value = ''

    // Open job URL in new tab
    window.open(job.value.source_url, '_blank', 'noopener,noreferrer')

    successMessage.value = 'تم فتح صفحة الوظيفة. يرجى إكمال التقديم على الموقع الأصلي.'

    // Clear success message after 5 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (err: any) {
    error.value = 'فشل فتح صفحة الوظيفة'
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
      successMessage.value = 'تم إزالة الوظيفة من القائمة'
    } else {
      // Add to saved jobs
      await jobsStore.addSavedJob(job.value)
      successMessage.value = 'تم حفظ الوظيفة بنجاح'
    }

    isSaved.value = !isSaved.value

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'فشل حفظ الوظيفة'
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
    error.value = err.response?.data?.detail || 'فشل تحميل تفاصيل الوظيفة'
    console.error('Error fetching job details:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJobDetails()
})
</script>
