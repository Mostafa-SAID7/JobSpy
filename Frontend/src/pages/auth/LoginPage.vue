<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">تسجيل الدخول</h1>
          <p class="text-gray-600">أدخل بيانات حسابك للمتابعة</p>
        </div>

        <!-- Error Message -->
        <div
          v-if="authStore.error"
          class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-red-700 text-sm">{{ authStore.error }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Email Input -->
          <FormInput
            v-model="formData.email"
            type="email"
            label="البريد الإلكتروني"
            placeholder="example@email.com"
            :error="errors.email"
            required
          />

          <!-- Password Input -->
          <FormInput
            v-model="formData.password"
            type="password"
            label="كلمة المرور"
            placeholder="••••••••"
            :error="errors.password"
            required
          />

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="formData.rememberMe"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-gray-700">تذكرني</span>
            </label>
            <RouterLink
              to="/auth/forgot-password"
              class="text-blue-600 hover:text-blue-700 font-medium"
            >
              هل نسيت كلمة المرور؟
            </RouterLink>
          </div>

          <!-- Submit Button -->
          <FormButton
            label="تسجيل الدخول"
            type="submit"
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
            class="w-full"
          />
        </form>

        <!-- Divider -->
        <div class="my-6 flex items-center gap-4">
          <div class="flex-1 h-px bg-gray-300"></div>
          <span class="text-gray-500 text-sm">أو</span>
          <div class="flex-1 h-px bg-gray-300"></div>
        </div>

        <!-- Sign Up Link -->
        <p class="text-center text-gray-600">
          ليس لديك حساب؟
          <RouterLink
            to="/auth/register"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            إنشاء حساب جديد
          </RouterLink>
        </p>
      </div>

      <!-- Footer -->
      <p class="text-center text-gray-600 text-sm mt-6">
        بالمتابعة، أنت توافق على
        <a href="#" class="text-blue-600 hover:text-blue-700">شروط الخدمة</a>
        و
        <a href="#" class="text-blue-600 hover:text-blue-700">سياسة الخصوصية</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import FormInput from '@/components/forms/FormInput.vue'
import FormButton from '@/components/forms/FormButton.vue'

const router = useRouter()
const authStore = useAuthStore()

const formData = reactive({
  email: '',
  password: '',
  rememberMe: false
})

const errors = reactive({
  email: '',
  password: ''
})

const validateForm = (): boolean => {
  errors.email = ''
  errors.password = ''

  if (!formData.email) {
    errors.email = 'البريد الإلكتروني مطلوب'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'البريد الإلكتروني غير صحيح'
  }

  if (!formData.password) {
    errors.password = 'كلمة المرور مطلوبة'
  } else if (formData.password.length < 6) {
    errors.password = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
  }

  return !errors.email && !errors.password
}

const handleLogin = async () => {
  if (!validateForm()) return

  const success = await authStore.login(formData.email, formData.password)

  if (success) {
    // Store remember me preference
    if (formData.rememberMe) {
      localStorage.setItem('rememberMe', 'true')
    }
    // Redirect to home page
    router.push('/')
  }
}
</script>
