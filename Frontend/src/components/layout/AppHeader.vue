<template>
  <header class="bg-white dark:bg-gray-900 shadow-md sticky top-0 z-50 transition-colors">
    <div class="w-full max-w-7xl mx-auto px-4 py-4">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2">
          <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">JS</span>
          </div>
          <span class="text-xl font-bold text-gray-800 dark:text-white">JobSpy</span>
        </RouterLink>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-8">
          <RouterLink
            to="/jobs"
            class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            active-class="text-blue-600 dark:text-blue-400 font-semibold"
          >
            البحث عن الوظائف
          </RouterLink>

          <RouterLink
            v-if="authStore.isAuthenticated"
            to="/saved-jobs"
            class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            active-class="text-blue-600 dark:text-blue-400 font-semibold"
          >
            الوظائف المحفوظة
          </RouterLink>

          <RouterLink
            v-if="authStore.isAuthenticated"
            to="/alerts"
            class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            active-class="text-blue-600 dark:text-blue-400 font-semibold"
          >
            التنبيهات
          </RouterLink>
        </nav>

        <!-- User Menu & Theme Toggle -->
        <div class="flex items-center gap-4">
          <!-- Theme Toggle -->
          <ThemeToggle />

          <template v-if="authStore.isAuthenticated">
            <RouterLink
              to="/profile"
              class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            >
              {{ authStore.user?.full_name }}
            </RouterLink>
            <button
              @click="handleLogout"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              تسجيل الخروج
            </button>
          </template>

          <template v-else>
            <RouterLink
              to="/auth/login"
              class="px-4 py-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              دخول
            </RouterLink>
            <RouterLink
              to="/auth/register"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              تسجيل
            </RouterLink>
          </template>

          <!-- Mobile Menu Button -->
          <button
            @click="uiStore.toggleSidebar"
            class="md:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <svg class="w-6 h-6 text-gray-800 dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
import { useRouter } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

const authStore = useAuthStore()
const uiStore = useUIStore()
const router = useRouter()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>
