<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border border-gray-200 dark:border-gray-700">
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ job.title }}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">{{ job.company }}</p>
      </div>
      <button
        @click="toggleSave"
        :class="[
          'p-2 rounded-lg transition-colors',
          isSaved
            ? 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-800'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
        ]"
        :title="isSaved ? 'إزالة من المحفوظات' : 'حفظ الوظيفة'"
      >
        <svg class="w-5 h-5" :fill="isSaved ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h6a2 2 0 012 2v12a2 2 0 01-2 2H7a2 2 0 01-2-2V5z" />
        </svg>
      </button>
    </div>

    <!-- Job Details -->
    <div class="space-y-3 mb-4">
      <!-- Location -->
      <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span>{{ job.location }}</span>
        <span v-if="job.is_remote" class="ml-2 px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-400 text-xs rounded">عن بعد</span>
      </div>

      <!-- Job Type -->
      <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4m0 0L14 6m2-2l2 2M9 20h6m-6 0a9 9 0 01-9-9m9 9a9 9 0 019-9" />
        </svg>
        <span>{{ getJobTypeLabel(job.job_type) }}</span>
      </div>

      <!-- Salary -->
      <div v-if="job.salary_min || job.salary_max" class="flex items-center text-sm text-gray-600 dark:text-gray-400">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ formatSalary(job.salary_min) }} - {{ formatSalary(job.salary_max) }}</span>
      </div>

      <!-- Posted Date -->
      <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span>{{ formatDate(job.posted_date) }}</span>
      </div>

      <!-- Source -->
      <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
        <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-400 text-xs rounded font-medium">{{ job.site_name }}</span>
      </div>
    </div>

    <!-- Description Preview -->
    <p v-if="job.description" class="text-sm text-gray-700 dark:text-gray-300 mb-4 line-clamp-2">
      {{ job.description }}
    </p>

    <!-- Actions -->
    <div class="flex gap-2">
      <a
        :href="job.job_url"
        target="_blank"
        rel="noopener noreferrer"
        class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-center text-sm font-medium"
      >
        عرض الوظيفة
      </a>
      <button
        @click="$emit('view-details')"
        class="flex-1 border border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400 px-4 py-2 rounded-lg hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors text-sm font-medium"
      >
        التفاصيل
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Job {
  job_id: string
  title: string
  company: string
  location: string
  job_url: string
  description?: string
  salary_min?: number
  salary_max?: number
  job_type: string
  is_remote: boolean
  posted_date: string
  site_name: string
}

interface Props {
  job: Job
  isSaved?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSaved: false
})

const emit = defineEmits<{
  'toggle-save': []
  'view-details': []
}>()

const toggleSave = () => {
  emit('toggle-save')
}

const getJobTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    fulltime: 'دوام كامل',
    parttime: 'دوام جزئي',
    internship: 'تدريب',
    contract: 'عقد'
  }
  return labels[type] || type
}

const formatSalary = (salary?: number): string => {
  if (!salary) return 'غير محدد'
  return new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency: 'SAR',
    maximumFractionDigits: 0
  }).format(salary)
}

const formatDate = (date: string): string => {
  const d = new Date(date)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - d.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'اليوم'
  if (diffDays === 1) return 'أمس'
  if (diffDays < 7) return `منذ ${diffDays} أيام`
  if (diffDays < 30) return `منذ ${Math.floor(diffDays / 7)} أسابيع`
  return d.toLocaleDateString('ar-SA')
}
</script>
