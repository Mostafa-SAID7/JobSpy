<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'px-6 py-2 rounded font-semibold transition-all duration-150',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
      'flex items-center justify-center gap-2',
      variantClasses,
      sizeClasses,
      disabled || loading ? 'opacity-60 cursor-not-allowed shadow-none' : 'cursor-pointer active:scale-[0.98]'
    ]"
    @click="$emit('click')"
  >
    <svg
      v-if="loading"
      class="w-4 h-4 animate-spin"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <slot v-else>
      <span>{{ label }}</span>
    </slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'outline' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

interface Props {
  label: string
  type?: 'button' | 'submit' | 'reset'
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false
})

defineEmits<{
  click: []
>()

const variantClasses = computed(() => {
  const variants: Record<ButtonVariant, string> = {
    primary: 'bg-[#0078d4] text-white hover:bg-[#106ebe] shadow-sm focus:ring-[#0078d4]',
    secondary: 'bg-[#f3f2f1] dark:bg-gray-800 text-[#323130] dark:text-gray-200 hover:bg-[#edebe9] dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:ring-gray-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 shadow-sm focus:ring-red-500',
    success: 'bg-[#107c10] text-white hover:bg-[#0b5a0b] shadow-sm focus:ring-[#107c10]',
    outline: 'border border-[#0078d4] text-[#0078d4] hover:bg-blue-50 dark:hover:bg-gray-800 focus:ring-[#0078d4]',
    ghost: 'text-[#0078d4] hover:bg-blue-50 dark:hover:bg-gray-800 focus:ring-[#0078d4]'
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes: Record<ButtonSize, string> = {
    sm: 'px-3 py-1 text-xs',
    md: 'px-5 py-2 text-sm',
    lg: 'px-8 py-3 text-base'
  }
  return sizes[props.size]
})
</script>
