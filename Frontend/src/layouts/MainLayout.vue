<template>
  <div class="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors selection:bg-blue-100 selection:text-blue-900">
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="flex-1 w-full py-8 md:py-12">
      <div class="w-full max-w-6xl mx-auto px-4 md:px-6">
        <router-view v-slot="{ Component }">
          <transition name="page-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
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
/* Page-level container transitions are handled via the transition wrapper above */
</style>
