<template>
  <button
    @click="toggleTheme"
    class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
    :title="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
    aria-label="Toggle theme"
  >
    <!-- Sun Icon (Light Mode) -->
    <svg
      v-if="isDark"
      class="w-5 h-5 text-yellow-500"
      fill="currentColor"
      viewBox="0 0 24 24"
    >
      <path d="M12 18a6 6 0 100-12 6 6 0 000 12zM12 2v4m0 12v4M4.22 4.22l2.83 2.83m4.24 4.24l2.83 2.83M2 12h4m12 0h4m-17.78 7.78l2.83-2.83m4.24-4.24l2.83-2.83" />
    </svg>

    <!-- Moon Icon (Dark Mode) -->
    <svg
      v-else
      class="w-5 h-5 text-gray-700"
      fill="currentColor"
      viewBox="0 0 24 24"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

const isDark = computed(() => uiStore.theme === 'dark')

const toggleTheme = () => {
  const newTheme = uiStore.theme === 'dark' ? 'light' : 'dark'
  uiStore.setTheme(newTheme)
}
</script>
