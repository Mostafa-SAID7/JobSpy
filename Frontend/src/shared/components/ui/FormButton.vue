<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'fluent-button',
      variantClasses,
      sizeClasses,
      loading ? 'relative !text-transparent' : ''
    ]"
    @click="$emit('click')"
  >
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
      <svg
        class="w-5 h-5 animate-spin text-current"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
    <slot>
      <span>{{ label }}</span>
    </slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'outline' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

interface Props {
  label?: string
  type?: 'button' | 'submit' | 'reset'
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
  type: 'button',
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false
})

defineEmits<{
  click: []
}>()

const variantClasses = computed(() => {
  const variants: Record<ButtonVariant, string> = {
    primary: 'fluent-button-primary shadow-sm',
    secondary: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600',
    danger: 'bg-error text-white hover:opacity-90 shadow-sm',
    success: 'bg-success text-white hover:opacity-90 shadow-sm',
    outline: 'border border-brand text-brand hover:bg-brand-dim',
    ghost: 'text-brand hover:bg-brand-dim'
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
