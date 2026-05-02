<template>
  <div class="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 bg-gray-50 dark:bg-gray-950">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="fluent-card bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 p-10">
        <!-- Brand/Header -->
        <div class="text-center mb-10">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-[#0078d4]/10 rounded-2xl mb-6">
            <svg class="w-8 h-8 text-[#0078d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight">Join JobSpy</h1>
          <p class="text-sm font-bold text-gray-400 uppercase tracking-widest mt-3">Start your career journey today</p>
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
        <form @submit.prevent="handleRegister" class="space-y-5">
          <FormInput
            v-model="formData.fullName"
            type="text"
            label="Full Professional Name"
            placeholder="Johnathan Doe"
            :error="errors.fullName"
            required
          />

          <FormInput
            v-model="formData.email"
            type="email"
            label="Professional Email"
            placeholder="name@company.com"
            :error="errors.email"
            required
          />

          <FormInput
            v-model="formData.password"
            type="password"
            label="Create Password"
            placeholder="••••••••"
            :error="errors.password"
            hint="Min 8 characters, letters & numbers"
            required
          />

          <FormInput
            v-model="formData.confirmPassword"
            type="password"
            label="Confirm Password"
            placeholder="••••••••"
            :error="errors.confirmPassword"
            required
          />

          <!-- Terms & Conditions -->
          <div class="space-y-3">
            <label class="flex items-start gap-3 cursor-pointer group">
              <input
                v-model="formData.agreeToTerms"
                type="checkbox"
                class="w-4 h-4 mt-1 rounded border-gray-300 text-[#0078d4] focus:ring-[#0078d4]/20 transition-all cursor-pointer"
              />
              <span class="text-xs font-bold text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors leading-relaxed uppercase tracking-tighter">
                I agree to the 
                <a href="#" class="text-[#0078d4] hover:underline">Terms of Service</a>
                and
                <a href="#" class="text-[#0078d4] hover:underline">Privacy Policy</a>
              </span>
            </label>
            <p v-if="errors.agreeToTerms" class="text-[10px] font-bold text-red-500 uppercase tracking-widest">
              {{ errors.agreeToTerms }}
            </p>
          </div>

          <FormButton
            label="Create Account"
            type="submit"
            variant="primary"
            class="w-full !py-4 shadow-lg shadow-blue-500/20"
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
          />
        </form>

        <div class="mt-10 pt-8 border-t border-gray-50 dark:border-gray-800 text-center">
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">
            Already have an account?
            <RouterLink
              to="/auth/login"
              class="text-[#0078d4] hover:underline ml-1"
            >
              Sign In
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
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/features/auth/stores/auth'
import FormInput from '@/shared/components/ui/FormInput.vue'
import FormButton from '@/shared/components/ui/FormButton.vue'

const router = useRouter()
const authStore = useAuthStore()

const formData = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false
})

const errors = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: ''
})

const validateForm = (): boolean => {
  errors.fullName = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''
  errors.agreeToTerms = ''

  if (!formData.fullName) {
    errors.fullName = 'Full name is required'
  } else if (formData.fullName.length < 3) {
    errors.fullName = 'Name must be at least 3 characters'
  }

  if (!formData.email) {
    errors.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Invalid email address'
  }

  if (!formData.password) {
    errors.password = 'Password is required'
  } else if (formData.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
  } else if (!/[a-zA-Z]/.test(formData.password) || !/[0-9]/.test(formData.password)) {
    errors.password = 'Password must contain letters and numbers'
  }

  if (!formData.confirmPassword) {
    errors.confirmPassword = 'Confirm password is required'
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
  }

  if (!formData.agreeToTerms) {
    errors.agreeToTerms = 'You must agree to the Terms of Service'
  }

  return (
    !errors.fullName &&
    !errors.email &&
    !errors.password &&
    !errors.confirmPassword &&
    !errors.agreeToTerms
  )
}

const handleRegister = async () => {
  if (!validateForm()) return

  const success = await authStore.register(
    formData.email,
    formData.password,
    formData.fullName
  )

  if (success) {
    // Redirect to home page
    router.push('/')
  }
}
</script>
