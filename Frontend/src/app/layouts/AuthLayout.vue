<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center transition-colors">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-blue-600 dark:text-blue-400">JobSpy</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Comprehensive job search platform</p>
      </div>

      <!-- Auth Content -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 transition-colors">
        <RouterView />
      </div>

      <!-- Footer -->
      <div class="text-center mt-8 text-gray-600 dark:text-gray-400 text-sm transition-colors">
        <p>© 2024 JobSpy. All rights reserved.</p>
      </div>
    </div>

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import ToastContainer from '@/shared/components/common/ToastContainer.vue'
</script>
