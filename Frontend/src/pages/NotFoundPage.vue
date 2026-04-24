<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="text-center">
      <!-- 404 Illustration -->
      <div class="mb-8">
        <div class="text-9xl font-bold text-gray-200 mb-4">404</div>
        <svg
          class="w-32 h-32 mx-auto text-gray-400 mb-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      <!-- Content -->
      <h1 class="text-4xl font-bold text-gray-900 mb-4">الصفحة غير موجودة</h1>
      <p class="text-xl text-gray-600 mb-8">
        عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها.
      </p>

      <!-- Suggestions -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8 text-left">
        <h2 class="font-semibold text-gray-900 mb-3">قد تكون مهتماً بـ:</h2>
        <ul class="space-y-2 text-gray-700">
          <li class="flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 10 10.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            <RouterLink to="/" class="text-blue-600 hover:text-blue-700 font-medium">
              الصفحة الرئيسية
            </RouterLink>
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 10 10.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            <RouterLink to="/jobs" class="text-blue-600 hover:text-blue-700 font-medium">
              البحث عن الوظائف
            </RouterLink>
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 10 10.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            <RouterLink to="/saved-jobs" class="text-blue-600 hover:text-blue-700 font-medium">
              الوظائف المحفوظة
            </RouterLink>
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 10 10.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            <RouterLink to="/alerts" class="text-blue-600 hover:text-blue-700 font-medium">
              التنبيهات
            </RouterLink>
          </li>
        </ul>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          @click="goBack"
          class="px-6 py-3 bg-gray-300 text-gray-900 rounded-lg hover:bg-gray-400 transition-colors font-semibold"
        >
          العودة للخلف
        </button>
        <RouterLink
          to="/"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold text-center"
        >
          الذهاب للصفحة الرئيسية
        </RouterLink>
      </div>

      <!-- Error Code -->
      <div class="mt-12 pt-8 border-t border-gray-200">
        <p class="text-sm text-gray-500">
          رمز الخطأ: 404 - الصفحة غير موجودة
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>
