<template>
  <header class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50 transition-all">
    <div class="w-full max-w-6xl mx-auto px-4 md:px-6 py-3">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2 group">
          <div class="w-9 h-9 bg-[#0078d4] rounded flex items-center justify-center transition-transform group-hover:scale-105 shadow-sm">
            <span class="text-white font-bold text-sm tracking-tighter">JS</span>
          </div>
          <span class="text-lg font-bold text-gray-900 dark:text-white tracking-tight">JobSpy</span>
        </RouterLink>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-6">
          <RouterLink
            to="/jobs"
            class="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors py-2 relative group"
            active-class="text-[#0078d4] dark:text-blue-400"
          >
            Search Jobs
            <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-[#0078d4] transition-all group-hover:w-full" :class="route.name === 'JobSearch' ? 'w-full' : ''"></span>
          </RouterLink>

          <RouterLink
            v-if="authStore.isAuthenticated"
            to="/saved-jobs"
            class="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors py-2 relative group"
            active-class="text-[#0078d4] dark:text-blue-400"
          >
            Saved Jobs
            <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-[#0078d4] transition-all group-hover:w-full" :class="route.name === 'SavedJobs' ? 'w-full' : ''"></span>
          </RouterLink>

          <RouterLink
            v-if="authStore.isAuthenticated"
            to="/alerts"
            class="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors py-2 relative group"
            active-class="text-[#0078d4] dark:text-blue-400"
          >
            Alerts
            <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-[#0078d4] transition-all group-hover:w-full" :class="route.name === 'Alerts' ? 'w-full' : ''"></span>
          </RouterLink>
        </nav>

        <!-- User Menu & Theme Toggle -->
        <div class="flex items-center gap-3">
          <!-- Theme Toggle -->
          <ThemeToggle />

          <div class="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-1 hidden sm:block"></div>

          <template v-if="authStore.isAuthenticated">
            <RouterLink
              to="/profile"
              class="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors"
            >
              {{ authStore.user?.full_name }}
            </RouterLink>
            <button
              @click="handleLogout"
              class="text-sm font-semibold px-4 py-1.5 bg-[#f3f2f1] dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-[#edebe9] dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded transition-all active:scale-95"
            >
              Logout
            </button>
          </template>

          <template v-else>
            <RouterLink
              to="/auth/login"
              class="text-sm font-semibold px-4 py-1.5 text-[#0078d4] dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-800 rounded transition-all"
            >
              Login
            </RouterLink>
            <RouterLink
              to="/auth/register"
              class="text-sm font-semibold px-4 py-1.5 bg-[#0078d4] hover:bg-[#106ebe] text-white rounded shadow-sm transition-all active:scale-95"
            >
              Register
            </RouterLink>
          </template>

          <!-- Mobile Menu Button -->
          <button
            @click="uiStore.toggleSidebar"
            class="md:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
            aria-label="Toggle menu"
          >
            <svg class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { useRouter, useRoute } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

const authStore = useAuthStore()
const uiStore = useUIStore()
const router = useRouter()
const route = useRoute()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>
