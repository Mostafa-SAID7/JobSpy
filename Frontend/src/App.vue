<template>
  <div id="app" class="min-h-screen bg-gray-50 flex flex-col">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

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
