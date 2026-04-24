<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 transition-colors">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">{{ label }}</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-white">{{ value }}</p>
        <p v-if="subtitle" class="text-xs text-gray-500 dark:text-gray-500 mt-2">{{ subtitle }}</p>
      </div>
      <div
        :class="[
          'p-3 rounded-lg',
          iconBgClass
        ]"
      >
        <component :is="icon" class="w-8 h-8" :class="iconColorClass" />
      </div>
    </div>

    <!-- Trend Indicator -->
    <div v-if="trend" class="mt-4 flex items-center gap-1">
      <svg
        v-if="trend > 0"
        class="w-4 h-4 text-green-600 dark:text-green-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4" />
      </svg>
      <svg
        v-else-if="trend < 0"
        class="w-4 h-4 text-red-600 dark:text-red-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
      </svg>
      <span :class="trend > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'" class="text-sm font-medium">
        {{ Math.abs(trend) }}% {{ trend > 0 ? 'زيادة' : 'انخفاض' }}
      </span>
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
