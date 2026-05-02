<template>
  <div class="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 bg-gray-50 dark:bg-gray-950">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="fluent-card bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 p-10">
        <!-- Brand/Header -->
        <div class="text-center mb-10">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-[#0078d4]/10 rounded-2xl mb-6">
            <svg class="w-8 h-8 text-[#0078d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight">Welcome Back</h1>
          <p class="text-sm font-bold text-gray-400 uppercase tracking-widest mt-3">Access your professional dashboard</p>
        </div>

        <!-- Error Message -->
        <transition name="fade">
          <div
            v-if="authStore.error"
            class="mb-6 p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 rounded-xl flex items-center gap-3"
          >
            <svg class="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-red-700 dark:text-red-400 text-xs font-bold">{{ authStore.error }}</p>
          </div>
        </transition>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <FormInput
            v-model="formData.email"
            type="email"
            label="Professional Email"
            placeholder="name@company.com"
            :error="errors.email"
            required
          />

          <div class="space-y-1">
            <FormInput
              v-model="formData.password"
              type="password"
              label="Security Password"
              placeholder="••••••••"
              :error="errors.password"
              required
            />
            <div class="flex justify-end">
              <RouterLink
                to="/auth/forgot-password"
                class="text-xs font-bold text-[#0078d4] hover:underline uppercase tracking-tighter"
              >
                Forgot Credentials?
              </RouterLink>
            </div>
          </div>

          <div class="flex items-center gap-2 cursor-pointer group">
            <input
              id="remember"
              v-model="formData.rememberMe"
              type="checkbox"
              class="w-4 h-4 rounded border-gray-300 text-[#0078d4] focus:ring-[#0078d4]/20 transition-all cursor-pointer"
            />
            <label for="remember" class="text-xs font-bold text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300 cursor-pointer transition-colors uppercase tracking-widest">
              Maintain Session
            </label>
          </div>

          <FormButton
            label="Sign In"
            type="submit"
            variant="primary"
            class="w-full !py-4 shadow-lg shadow-blue-500/20"
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
          />
        </form>

        <div class="mt-10 pt-8 border-t border-gray-50 dark:border-gray-800 text-center">
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">
            New to the Platform?
            <RouterLink
              to="/auth/register"
              class="text-[#0078d4] hover:underline ml-1"
            >
              Create Account
            </RouterLink>
          </p>
        </div>
      </div>

      <div class="mt-8 text-center space-x-4">
        <a href="#" class="text-[10px] font-bold text-gray-400 uppercase tracking-widest hover:text-[#0078d4] transition-colors">Privacy</a>
        <span class="text-gray-300">•</span>
        <a href="#" class="text-[10px] font-bold text-gray-400 uppercase tracking-widest hover:text-[#0078d4] transition-colors">Terms</a>
        <span class="text-gray-300">•</span>
        <a href="#" class="text-[10px] font-bold text-gray-400 uppercase tracking-widest hover:text-[#0078d4] transition-colors">Support</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/features/auth/stores/auth'
import FormInput from '@/shared/components/ui/FormInput.vue'
import FormButton from '@/shared/components/ui/FormButton.vue'

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
    errors.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Invalid email address'
  }

  if (!formData.password) {
    errors.password = 'Password is required'
  } else if (formData.password.length < 6) {
    errors.password = 'Password must be at least 6 characters'
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
