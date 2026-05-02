<template>
  <div class="text-center py-12">
    <div class="inline-block">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
    <p v-if="text" class="text-gray-600 dark:text-gray-400 mt-4">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text?: string
}>()
</script>
