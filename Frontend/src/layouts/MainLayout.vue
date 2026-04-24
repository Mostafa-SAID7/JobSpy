<template>
  <div class="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="flex-1 w-full py-8">
      <div class="w-full max-w-7xl mx-auto px-4">
        <RouterView />
      </div>
    </main>

    <!-- Footer -->
    <AppFooter />

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
</script>

<style scoped>
main {
  direction: rtl;
}
</style>
