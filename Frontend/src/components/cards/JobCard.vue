<template>
  <div class="fluent-card bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800 p-5 transition-all group">
    <!-- Header -->
    <div class="flex justify-between items-start gap-4 mb-4">
      <div class="flex-1 min-w-0">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1 truncate group-hover:text-[#0078d4] transition-colors">{{ job.title }}</h3>
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-[#0078d4] dark:text-blue-400">{{ job.company }}</span>
          <span class="text-gray-300 dark:text-gray-700">•</span>
          <span class="text-xs text-gray-500 dark:text-gray-400 font-medium px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{{ job.site_name }}</span>
        </div>
      </div>
      <button
        @click="toggleSave"
        :class="[
          'p-2 rounded transition-all active:scale-90',
          isSaved
            ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'
            : 'bg-[#f3f2f1] dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-[#edebe9] dark:hover:bg-gray-700'
        ]"
        :title="isSaved ? 'Remove from saved' : 'Save job'"
      >
        <svg class="w-5 h-5" :fill="isSaved ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>
    </div>

    <!-- Job Meta -->
    <div class="flex flex-wrap gap-y-3 gap-x-4 mb-5">
      <!-- Location -->
      <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
        <svg class="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span class="truncate max-w-[150px]">{{ job.location }}</span>
        <span v-if="job.is_remote" class="ml-2 px-1.5 py-0.5 bg-green-50 dark:bg-green-900/20 text-[#107c10] dark:text-green-400 text-[10px] font-bold uppercase tracking-wider rounded border border-green-200 dark:border-green-800/50">Remote</span>
      </div>

      <!-- Job Type -->
      <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
        <svg class="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4m0 0L14 6m2-2l2 2M9 20h6m-6 0a9 9 0 01-9-9m9 9a9 9 0 019-9" />
        </svg>
        <span>{{ getJobTypeLabel(job.job_type) }}</span>
      </div>

      <!-- Salary -->
      <div v-if="job.salary_min || job.salary_max" class="flex items-center text-sm text-gray-700 dark:text-gray-300 font-semibold">
        <svg class="w-4 h-4 mr-1.5 text-[#107c10]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ formatSalary(job.salary_min) }} - {{ formatSalary(job.salary_max) }}</span>
      </div>
    </div>

    <!-- Description Preview -->
    <p v-if="job.description" class="text-sm text-gray-600 dark:text-gray-400 mb-6 line-clamp-2 leading-relaxed italic">
      {{ job.description }}
    </p>

    <!-- Actions -->
    <div class="flex gap-3 pt-2 border-t border-gray-100 dark:border-gray-800/50">
      <FormButton
        label="Quick View"
        variant="secondary"
        size="sm"
        class="flex-1"
        @click="$emit('view-details')"
      />
      <a
        :href="job.job_url"
        target="_blank"
        rel="noopener noreferrer"
        class="flex-1 bg-[#0078d4] hover:bg-[#106ebe] text-white px-4 py-2 rounded transition-all text-center text-xs font-bold shadow-sm active:scale-95 flex items-center justify-center gap-2"
      >
        Apply Now
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import FormButton from '@/components/forms/FormButton.vue'

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
    fulltime: 'Full-time',
    parttime: 'Part-time',
    internship: 'Internship',
    contract: 'Contract'
  }
  return labels[type] || type
}

const formatSalary = (salary?: number): string => {
  if (!salary) return 'Not specified'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(salary)
}

const formatDate = (date: string): string => {
  const d = new Date(date)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - d.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return d.toLocaleDateString('en-US')
}
</script>
