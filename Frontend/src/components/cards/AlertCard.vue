<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow">
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ alert.name }}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ alert.query }} • {{ getFrequencyLabel(alert.frequency) }}
        </p>
      </div>
      <div
        :class="[
          'px-3 py-1 rounded-full text-xs font-medium',
          alert.is_active
            ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-400'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400'
        ]"
      >
        {{ alert.is_active ? 'Active' : 'Inactive' }}
      </div>
    </div>

    <!-- Alert Details -->
    <div class="space-y-2 mb-4 text-sm text-gray-600 dark:text-gray-400">
      <!-- Notification Method -->
      <div class="flex items-center">
        <span class="font-medium text-gray-700 dark:text-gray-300 w-32">Notification:</span>
        <span>{{ getNotificationLabel(alert.notification_method) }}</span>
      </div>

      <!-- Last Triggered -->
      <div class="flex items-center">
        <span class="font-medium text-gray-700 dark:text-gray-300 w-32">Last Triggered:</span>
        <span>{{ formatDate(alert.last_triggered) }}</span>
      </div>

      <!-- Next Trigger -->
      <div class="flex items-center">
        <span class="font-medium text-gray-700 dark:text-gray-300 w-32">Next Trigger:</span>
        <span>{{ formatDate(alert.next_trigger) }}</span>
      </div>

      <!-- Created Date -->
      <div class="flex items-center">
        <span class="font-medium text-gray-700 dark:text-gray-300 w-32">Created:</span>
        <span>{{ formatDate(alert.created_at) }}</span>
      </div>

      <!-- New Jobs Count -->
      <div class="flex items-center">
        <span class="font-medium text-gray-700 dark:text-gray-300 w-32">New Jobs:</span>
        <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-400 text-xs rounded">
          {{ alert.new_jobs_count }}
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-2">
      <button
        @click="toggleActive"
        :disabled="isOperating"
        :class="[
          'flex-1 px-4 py-2 rounded-lg transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed',
          alert.is_active
            ? 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-800 disabled:hover:bg-red-100'
            : 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-800 disabled:hover:bg-green-100'
        ]"
      >
        <span v-if="isOperating" class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        <span v-else>{{ alert.is_active ? 'Disable' : 'Enable' }}</span>
      </button>
      <button
        @click="$emit('edit')"
        :disabled="isOperating"
        class="flex-1 border border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400 px-4 py-2 rounded-lg hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
      >
        Edit
      </button>
      <button
        @click="$emit('delete')"
        :disabled="isOperating"
        class="flex-1 border border-red-600 dark:border-red-400 text-red-600 dark:text-red-400 px-4 py-2 rounded-lg hover:bg-red-50 dark:hover:bg-gray-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Alert {
  id: string
  name: string
  query: string
  frequency: string
  notification_method: string
  is_active: boolean
  last_triggered?: string
  next_trigger?: string
  created_at: string
  new_jobs_count: number
}

interface Props {
  alert: Alert
  isOperating?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  'toggle-active': []
  edit: []
  delete: []
}>()

const toggleActive = () => {
  emit('toggle-active')
}

const getFrequencyLabel = (frequency: string): string => {
  const labels: Record<string, string> = {
    hourly: 'Hourly',
    daily: 'Daily',
    weekly: 'Weekly'
  }
  return labels[frequency] || frequency
}

const getNotificationLabel = (method: string): string => {
  const labels: Record<string, string> = {
    email: 'Email',
    in_app: 'In-App Notification'
  }
  return labels[method] || method
}

const formatDate = (date?: string): string => {
  if (!date) return 'Never triggered'
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
