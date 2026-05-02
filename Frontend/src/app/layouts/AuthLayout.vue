<template>
  <div class="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center p-6 transition-colors relative overflow-hidden">
    <!-- Subtle Background Atmosphere -->
    <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
    
    <div class="absolute -top-24 -left-24 w-96 h-96 bg-blue-600/5 dark:bg-blue-600/10 rounded-full blur-[120px] animate-pulse"></div>
    <div class="absolute -bottom-24 -right-24 w-96 h-96 bg-indigo-600/5 dark:bg-indigo-600/10 rounded-full blur-[120px] animate-pulse" style="animation-delay: 2s"></div>

    <div class="w-full max-w-2xl relative z-10 transition-all animate-in fade-in zoom-in-95 duration-500">
      <!-- Direct Form View -->
      <RouterView />
    </div>

    <!-- System Status Bar -->
    <div class="fixed bottom-8 left-8 flex items-center gap-4 opacity-30 hover:opacity-100 transition-opacity pointer-events-none sm:pointer-events-auto">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
        <span class="text-[9px] font-bold text-gray-500 uppercase tracking-[0.2em]">System Secure</span>
      </div>
      <div class="w-px h-3 bg-gray-300 dark:bg-gray-800"></div>
      <div class="flex items-center gap-2">
        <span class="text-[9px] font-bold text-gray-500 uppercase tracking-[0.2em]">v{{ appVersion }}</span>
      </div>
    </div>

    <!-- Theme Control -->
    <div class="fixed top-8 right-8 z-50">
      <ThemeToggle />
    </div>

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import ToastContainer from '@/shared/components/common/ToastContainer.vue'
import ThemeToggle from '@/app/layouts/components/ThemeToggle.vue'

const appVersion = '1.0.4'
</script>

<style scoped>
.animate-pulse {
  animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.2; }
}
</style>
