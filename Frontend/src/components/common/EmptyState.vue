<template>
  <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-12 text-center">
    <div class="mx-auto mb-4 flex justify-center">
      <slot name="icon">
        <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </slot>
    </div>
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ title }}</h3>
    <p class="text-gray-600 dark:text-gray-400" :class="{ 'mb-6': actionText }">{{ message }}</p>
    <RouterLink
      v-if="actionText && actionRoute"
      :to="actionRoute"
      class="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
    >
      {{ actionText }}
    </RouterLink>
    <button
      v-else-if="actionText"
      @click="$emit('action-click')"
      class="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
    >
      {{ actionText }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  message: string
  actionText?: string
  actionRoute?: string
}>()

defineEmits<{
  (e: 'action-click'): void
}>()
</script>
