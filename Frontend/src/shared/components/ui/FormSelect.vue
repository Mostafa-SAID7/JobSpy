<template>
  <div :class="label ? 'mb-4' : ''">
    <label
      v-if="label"
      :for="id"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <div class="relative">
      <select
        :id="id"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :class="[
          'fluent-select',
          error ? 'border-red-500 bg-red-50 dark:bg-red-900/20 focus:ring-red-500 focus:border-red-500' : ''
        ]"
        @change="handleChange"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      >
        <option v-if="placeholder" value="">
          {{ placeholder }}
        </option>
        <option
          v-for="option in normalizedOptions"
          :key="getOptionValue(option)"
          :value="getOptionValue(option)"
        >
          {{ getOptionLabel(option) }}
        </option>
      </select>

      <!-- Dropdown Icon -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg
          class="w-4 h-4 text-gray-400 dark:text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </div>

    <!-- Error Message -->
    <p v-if="error" class="mt-1 text-sm text-red-500 dark:text-red-400">
      {{ error }}
    </p>

    <!-- Helper Text -->
    <p v-if="hint && !error" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Option {
  value: string | number
  label: string
}

type OptionType = Option | string | number

interface Props {
  modelValue: string | number
  options: OptionType[]
  label?: string
  placeholder?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  id: () => `select-${Math.random().toString(36).substr(2, 9)}`
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: []
  focus: []
}>()

// Normalize options to always have value and label
const normalizedOptions = computed(() => {
  return props.options.map(option => {
    if (typeof option === 'object' && option !== null && 'value' in option) {
      return option as Option
    }
    return {
      value: option as string | number,
      label: String(option)
    }
  })
})

const getOptionValue = (option: Option) => option.value
const getOptionLabel = (option: Option) => option.label

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const value = target.value
  
  // Try to preserve the original type (number or string)
  const originalOption = normalizedOptions.value.find(opt => String(opt.value) === value)
  if (originalOption) {
    emit('update:modelValue', originalOption.value)
  } else {
    emit('update:modelValue', value)
  }
}
</script>

<style scoped>
/* Remove default select arrow in IE/Edge */
select::-ms-expand {
  display: none;
}
</style>
