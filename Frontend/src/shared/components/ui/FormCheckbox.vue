<template>
  <div class="mb-4">
    <div class="flex items-center">
      <input
        :id="id"
        type="checkbox"
        :checked="modelValue"
        :disabled="disabled"
        :class="[
          'w-4 h-4 rounded transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-blue-500',
          error
            ? 'border-red-500 text-red-600'
            : 'border-gray-300 text-blue-600',
          disabled ? 'bg-gray-100 cursor-not-allowed' : 'cursor-pointer'
        ]"
        @change="$emit('update:modelValue', $event.target.checked)"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      />
      <label
        v-if="label"
        :for="id"
        :class="[
          'ml-3 text-sm font-medium',
          disabled ? 'text-gray-500 cursor-not-allowed' : 'text-gray-700 cursor-pointer'
        ]"
      >
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-500">{{ error }}</p>
    <p v-if="hint" class="mt-1 text-sm text-gray-500">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  label?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  id: () => `checkbox-${Math.random().toString(36).substr(2, 9)}`
})

defineEmits<{
  'update:modelValue': [value: boolean]
  blur: []
  focus: []
}>()
</script>
