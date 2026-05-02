<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-widest text-[10px]">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <input
        :id="id"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :class="[
          'w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none',
          error ? 'border-red-500 bg-red-50 dark:bg-red-900/10 focus:ring-red-500/20 focus:border-red-500' : '',
          type === 'password' ? 'pr-12' : ''
        ]"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      />
      
      <!-- Password Toggle -->
      <button
        v-if="type === 'password'"
        type="button"
        @click="toggleShow"
        tabindex="-1"
        class="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
      >
        <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.076m10.728 4.516H13.5M15.865 15.865L19 19m-4.632-4.632A3 3 0 119.532 9.532m0 0L5.122 5.122M19.383 14.383a9.96 9.96 0 001.075-2.383 9.96 9.96 0 00-1.075-2.383l-1.542-1.542M12 5c4.478 0 8.268 2.943 9.542 7a9.97 9.97 0 01-1.563 3.076M12 5a9.97 9.97 0 00-1.563.125m10.728 4.516a3 3 0 00-4.632-4.632" />
        </svg>
      </button>
    </div>
    <transition name="fade">
      <p v-if="error" class="mt-2 text-[11px] font-bold text-red-500 dark:text-red-400 uppercase tracking-wider">{{ error }}</p>
    </transition>
    <p v-if="hint" class="mt-2 text-[10px] text-gray-500 dark:text-gray-400 italic tracking-tight">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue: string | number
  type?: string
  label?: string
  placeholder?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
  id: () => `input-${Math.random().toString(36).substring(2, 9)}`
})

defineEmits<{
  'update:modelValue': [value: string | number]
  blur: []
  focus: []
}>()

const showPassword = ref(false)
const toggleShow = () => {
  showPassword.value = !showPassword.value
}

const inputType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type
})
</script>
