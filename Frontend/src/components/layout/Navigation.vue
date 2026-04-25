<template>
  <nav class="bg-white shadow-md sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex-shrink-0">
          <router-link to="/" class="flex items-center">
            <span class="text-2xl font-bold text-blue-600">JobSpy</span>
          </router-link>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <router-link
            to="/search"
            class="text-gray-700 hover:text-blue-600 transition-colors"
            :class="{ 'text-blue-600 font-semibold': isActive('/search') }"
          >
            البحث
          </router-link>
          <router-link
            to="/saved-jobs"
            class="text-gray-700 hover:text-blue-600 transition-colors"
            :class="{ 'text-blue-600 font-semibold': isActive('/saved-jobs') }"
          >
            الوظائف المحفوظة
          </router-link>
          <router-link
            to="/alerts"
            class="text-gray-700 hover:text-blue-600 transition-colors"
            :class="{ 'text-blue-600 font-semibold': isActive('/alerts') }"
          >
            التنبيهات
          </router-link>
          <router-link
            to="/profile"
            class="text-gray-700 hover:text-blue-600 transition-colors"
            :class="{ 'text-blue-600 font-semibold': isActive('/profile') }"
          >
            الملف الشخصي
          </router-link>
        </div>

        <!-- User Menu & Mobile Toggle -->
        <div class="flex items-center space-x-4">
          <!-- User Dropdown -->
          <div v-if="authStore.isAuthenticated" class="relative">
            <button
              @click="toggleUserMenu"
              class="flex items-center space-x-2 text-gray-700 hover:text-blue-600"
            >
              <span class="text-sm font-medium">{{ authStore.user?.full_name }}</span>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-if="showUserMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50"
            >
              <router-link
                to="/profile"
                class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                @click="showUserMenu = false"
              >
                الملف الشخصي
              </router-link>
              <button
                @click="logout"
                class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100"
              >
                تسجيل الخروج
              </button>
            </div>
          </div>

          <!-- Auth Links -->
          <div v-if="!authStore.isAuthenticated" class="hidden md:flex space-x-4">
            <router-link
              to="/login"
              class="text-gray-700 hover:text-blue-600 font-medium"
            >
              دخول
            </router-link>
            <router-link
              to="/register"
              class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              تسجيل
            </router-link>
          </div>

          <!-- Mobile Menu Toggle -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden text-gray-700 hover:text-blue-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="showMobileMenu" class="md:hidden pb-4 space-y-2">
        <router-link
          to="/search"
          class="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
          @click="showMobileMenu = false"
        >
          البحث
        </router-link>
        <router-link
          to="/saved-jobs"
          class="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
          @click="showMobileMenu = false"
        >
          الوظائف المحفوظة
        </router-link>
        <router-link
          to="/alerts"
          class="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
          @click="showMobileMenu = false"
        >
          التنبيهات
        </router-link>
        <router-link
          to="/profile"
          class="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
          @click="showMobileMenu = false"
        >
          الملف الشخصي
        </router-link>
        <div v-if="!authStore.isAuthenticated" class="flex space-x-2 px-4 pt-2">
          <router-link
            to="/login"
            class="flex-1 text-center px-4 py-2 text-gray-700 border border-gray-300 rounded hover:bg-gray-100"
            @click="showMobileMenu = false"
          >
            دخول
          </router-link>
          <router-link
            to="/register"
            class="flex-1 text-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            @click="showMobileMenu = false"
          >
            تسجيل
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const showMobileMenu = ref(false)
const showUserMenu = ref(false)

const isActive = (path: string) => {
  return router.currentRoute.value.path === path
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const logout = async () => {
  await authStore.logout()
  showUserMenu.value = false
  router.push('/login')
}
</script>
