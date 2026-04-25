<template>
  <div class="fluent-card bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800 p-6 transition-all">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ label }}</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">{{ value }}</p>
        <p v-if="subtitle" class="text-xs text-gray-400 dark:text-gray-500 mt-1.5">{{ subtitle }}</p>
      </div>
      <div
        :class="[
          'p-2.5 rounded',
          iconBgClass
        ]"
      >
        <component :is="icon" class="w-6 h-6" :class="iconColorClass" />
      </div>
    </div>

    <!-- Trend Indicator -->
    <div v-if="trend" class="mt-4 flex items-center gap-1.5">
      <div :class="trend > 0 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30'" class="p-0.5 rounded-full">
        <svg
          v-if="trend > 0"
          class="w-3 h-3 text-green-700 dark:text-green-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 15l7-7 7 7" />
        </svg>
        <svg
          v-else
          class="w-3 h-3 text-red-700 dark:text-red-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      <span :class="trend > 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'" class="text-xs font-bold">
        {{ Math.abs(trend) }}% {{ trend > 0 ? 'up' : 'down' }}
      </span>
      <span class="text-xs text-gray-400 dark:text-gray-500">vs last month</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type CardVariant = 'primary' | 'success' | 'warning' | 'danger' | 'info'

interface Props {
  label: string
  value: string | number
  subtitle?: string
  variant?: CardVariant
  trend?: number
  icon?: any
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary'
})

const iconBgClass = computed(() => {
  const variants: Record<CardVariant, string> = {
    primary: 'bg-blue-100 dark:bg-blue-900',
    success: 'bg-green-100 dark:bg-green-900',
    warning: 'bg-yellow-100 dark:bg-yellow-900',
    danger: 'bg-red-100 dark:bg-red-900',
    info: 'bg-purple-100 dark:bg-purple-900'
  }
  return variants[props.variant]
})

const iconColorClass = computed(() => {
  const variants: Record<CardVariant, string> = {
    primary: 'text-blue-600 dark:text-blue-400',
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    danger: 'text-red-600 dark:text-red-400',
    info: 'text-purple-600 dark:text-purple-400'
  }
  return variants[props.variant]
})
</script>
