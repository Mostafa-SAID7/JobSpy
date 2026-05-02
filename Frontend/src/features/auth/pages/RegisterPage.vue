<template>
  <div class="flex items-center justify-center p-6 sm:p-12">
    <div class="w-full max-w-lg space-y-12">
      <!-- Content -->
      <div class="transition-all animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div class="text-center mb-12">
          <h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-tight">
            Elevate Your <span class="text-blue-600 dark:text-blue-400">Career</span>
          </h1>
          <p class="text-sm font-bold text-gray-400 uppercase tracking-[0.2em] mt-4">Join the future of professional job hunting</p>
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
        <form @submit.prevent="handleRegister" class="space-y-8">
          <div class="grid grid-cols-1 gap-6">
            <FormInput
              v-model="formData.fullName"
              type="text"
              label="Full Professional Name"
              placeholder="e.g. Alexander Pierce"
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

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormInput
                v-model="formData.password"
                type="password"
                label="Security Password"
                placeholder="••••••••"
                :error="errors.password"
                hint="Use letters & numbers"
                required
              />

              <FormInput
                v-model="formData.confirmPassword"
                type="password"
                label="Confirm Security"
                placeholder="••••••••"
                :error="errors.confirmPassword"
                required
              />
            </div>
          </div>

          <!-- Terms & Conditions -->
          <div class="space-y-4">
            <label class="flex items-start gap-4 cursor-pointer group p-4 rounded-2xl hover:bg-white/50 dark:hover:bg-white/5 transition-all">
              <input
                v-model="formData.agreeToTerms"
                type="checkbox"
                class="w-5 h-5 mt-0.5 rounded-lg border-gray-300 text-blue-600 focus:ring-blue-500/20 transition-all cursor-pointer"
              />
              <span class="text-[11px] font-bold text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors leading-relaxed uppercase tracking-widest">
                I acknowledge the 
                <a href="#" class="text-blue-600 hover:underline">Professional Service Terms</a>
                and
                <a href="#" class="text-blue-600 hover:underline">Privacy Protocol</a>
              </span>
            </label>
            <p v-if="errors.agreeToTerms" class="px-4 text-[10px] font-bold text-red-500 uppercase tracking-widest animate-pulse">
              {{ errors.agreeToTerms }}
            </p>
          </div>

          <FormButton
            label="Initialize Account"
            type="submit"
            variant="primary"
            class="w-full !py-5 shadow-2xl shadow-blue-500/30 text-xs font-black uppercase tracking-[0.2em]"
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
          />
        </form>

        <div class="mt-12 pt-10 border-t border-gray-200/50 dark:border-gray-800/50 text-center">
          <p class="text-[11px] font-bold text-gray-400 uppercase tracking-[0.2em]">
            Legacy Member?
            <RouterLink
              to="/auth/login"
              class="text-blue-600 hover:text-blue-500 transition-colors ml-2"
            >
              Authorize Here
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
