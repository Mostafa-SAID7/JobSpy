<template>
  <div class="flex items-center justify-center p-6 sm:p-12">
    <div class="w-full max-w-lg space-y-12">
      <!-- Content -->
      <div class="transition-all animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div class="text-center mb-12">
          <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-tight">
            Secure <span class="text-blue-600 dark:text-blue-400">Access</span>
          </h1>
          <p class="text-sm font-bold text-gray-400 uppercase tracking-[0.2em] mt-4">Identify yourself to continue</p>
        </div>

        <!-- Error Message -->
        <transition name="fade">
          <div
            v-if="authStore.error"
            class="mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center gap-4 backdrop-blur-sm"
          >
            <div class="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p class="text-red-700 dark:text-red-400 text-xs font-bold uppercase tracking-wide">{{ authStore.error }}</p>
          </div>
        </transition>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-8">
          <div class="space-y-6">
            <FormInput
              v-model="formData.email"
              type="email"
              label="Professional Identification"
              placeholder="name@company.com"
              :error="errors.email"
              required
            />

            <div>
              <div class="flex items-center justify-between mb-2 px-1">
                <label class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-widest text-[10px]">Security Key</label>
                <RouterLink
                  to="/auth/forgot-password"
                  class="text-[10px] font-bold text-blue-600 hover:text-blue-500 uppercase tracking-widest"
                >
                  Reset Key?
                </RouterLink>
              </div>
              <FormInput
                v-model="formData.password"
                type="password"
                placeholder="••••••••"
                :error="errors.password"
                required
              />
            </div>
          </div>

          <div class="flex items-center gap-3 p-4 rounded-2xl hover:bg-white/50 dark:hover:bg-white/5 transition-all cursor-pointer group">
            <input
              v-model="formData.rememberMe"
              type="checkbox"
              class="w-5 h-5 rounded-lg border-gray-300 text-blue-600 focus:ring-blue-500/20 transition-all cursor-pointer"
            />
            <span class="text-[11px] font-bold text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors uppercase tracking-widest">Maintain Active Session</span>
          </div>

          <FormButton
            label="Authorize Access"
            type="submit"
            variant="primary"
            class="w-full !py-5 shadow-2xl shadow-blue-500/30 text-xs font-black uppercase tracking-[0.2em]"
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
          />
        </form>

        <div class="mt-12 pt-10 border-t border-gray-200/50 dark:border-gray-800/50 text-center">
          <p class="text-[11px] font-bold text-gray-400 uppercase tracking-[0.2em]">
            New to the Network?
            <RouterLink
              to="/auth/register"
              class="text-blue-600 hover:text-blue-500 transition-colors ml-2"
            >
              Request Access
            </RouterLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
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
    if (formData.rememberMe) {
      localStorage.setItem('rememberMe', 'true')
    }
    router.push('/')
  }
}
</script>
