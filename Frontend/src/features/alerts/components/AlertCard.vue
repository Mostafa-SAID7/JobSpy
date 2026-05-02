<template>
  <div class="fluent-card bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm hover:shadow-md transition-all group relative overflow-hidden">
    <!-- Status Indicator Line -->
    <div 
      class="absolute top-0 left-0 w-1 h-full transition-colors duration-300"
      :class="alert.is_active ? 'bg-[#0078d4]' : 'bg-gray-300 dark:bg-gray-700'"
    ></div>

    <!-- Header -->
    <div class="flex justify-between items-start mb-6">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-1">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white group-hover:text-[#0078d4] transition-colors leading-tight">
            {{ alert.name }}
          </h3>
          <span
            class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
            :class="alert.is_active 
              ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400' 
              : 'bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400'"
          >
            {{ alert.is_active ? 'Active' : 'Paused' }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <svg class="w-3.5 h-3.5 text-[#0078d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          "{{ alert.query }}"
        </p>
      </div>
      
      <div class="flex items-center gap-1">
        <button
          @click="$emit('edit')"
          class="p-2 text-gray-400 hover:text-[#0078d4] hover:bg-[#0078d4]/5 rounded-lg transition-all"
          title="Edit alert"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        </button>
        <button
          @click="$emit('delete')"
          class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
          title="Delete alert"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Details Grid -->
    <div class="grid grid-cols-2 gap-y-4 gap-x-6 mb-8">
      <div class="space-y-1">
        <span class="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter">Frequency</span>
        <div class="flex items-center text-xs font-semibold text-gray-700 dark:text-gray-300">
          <svg class="w-3.5 h-3.5 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ getFrequencyLabel(alert.frequency) }}
        </div>
      </div>

      <div class="space-y-1">
        <span class="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter">Delivery</span>
        <div class="flex items-center text-xs font-semibold text-gray-700 dark:text-gray-300">
          <svg class="w-3.5 h-3.5 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          {{ getNotificationLabel(alert.notification_method) }}
        </div>
      </div>

      <div class="space-y-1">
        <span class="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter">Last Checked</span>
        <div class="text-xs font-semibold text-gray-700 dark:text-gray-300">
          {{ formatDate(alert.last_triggered) }}
        </div>
      </div>

      <div class="space-y-1">
        <span class="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter">New Matches</span>
        <div class="flex items-center gap-2">
          <span class="text-xs font-extrabold text-[#0078d4]">
            {{ alert.new_jobs_count || 0 }}
          </span>
          <span class="text-[9px] font-bold px-1.5 py-0.5 bg-[#0078d4]/10 text-[#0078d4] rounded" v-if="alert.new_jobs_count > 0">
            NEW
          </span>
        </div>
      </div>
    </div>

    <!-- Footer Action -->
    <div class="pt-5 border-t border-gray-50 dark:border-gray-800">
      <FormButton
        :variant="alert.is_active ? 'secondary' : 'primary'"
        class="w-full"
        size="sm"
        @click="toggleActive"
        :loading="isOperating"
      >
        {{ alert.is_active ? 'Pause Alert' : 'Resume Alert' }}
      </FormButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import FormButton from '@/components/forms/FormButton.vue'
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
