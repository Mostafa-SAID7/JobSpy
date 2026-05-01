<template>
  <div id="app" class="min-h-screen bg-gray-50 flex flex-col">
    <ErrorBoundary>
      <RouterView />
    </ErrorBoundary>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ErrorBoundary from '@/components/ErrorBoundary.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Check if user is logged in on app mount
  authStore.checkAuth()
})
</script>

<style scoped>
#app {
  width: 100%;
}
</style>
