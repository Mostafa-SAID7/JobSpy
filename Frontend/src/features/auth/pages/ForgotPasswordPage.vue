<template>
  <div class="flex items-center justify-center">
    <div class="w-full max-w-md">
      <!-- Content -->
      <div class="p-0">
        <div class="text-center mb-10">
          <h1 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight">Recover Account</h1>
          <p class="text-sm font-bold text-gray-400 uppercase tracking-widest mt-3">Follow the steps to reset your security</p>
        </div>

        <!-- Feedback Messages -->
        <transition name="fade">
          <div
            v-if="successMessage"
            class="mb-8 p-4 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/20 rounded-xl flex items-center gap-3"
          >
            <svg class="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <p class="text-green-800 dark:text-green-400 text-xs font-bold">{{ successMessage }}</p>
          </div>
        </transition>

        <transition name="fade">
          <div
            v-if="errorMessage"
            class="mb-8 p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 rounded-xl flex items-center gap-3"
          >
            <svg class="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-red-700 dark:text-red-400 text-xs font-bold">{{ errorMessage }}</p>
          </div>
        </transition>

        <!-- Step 1: Email Input -->
        <div v-if="currentStep === 'email'" class="space-y-6">
          <form @submit.prevent="handleSendReset" class="space-y-6">
            <FormInput
              v-model="formData.email"
              type="email"
              label="Professional Email"
              placeholder="name@company.com"
              :error="errors.email"
              required
            />

            <FormButton
              label="Initiate Recovery"
              type="submit"
              variant="primary"
              class="w-full !py-4 shadow-lg shadow-blue-500/20"
              :loading="isLoading"
              :disabled="isLoading"
            />
          </form>
        </div>

        <!-- Step 2: Reset Code Input -->
        <div v-if="currentStep === 'code'" class="space-y-6">
          <div class="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl mb-6">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest text-center leading-relaxed">
              A security code has been dispatched to 
              <span class="text-[#0078d4]">{{ formData.email }}</span>
            </p>
          </div>

          <form @submit.prevent="handleVerifyCode" class="space-y-6">
            <FormInput
              v-model="formData.code"
              type="text"
              label="Security Verification Code"
              placeholder="000 000"
              :error="errors.code"
              hint="Enter the 6-digit verification sequence"
              required
            />

            <FormButton
              label="Verify Identity"
              type="submit"
              variant="primary"
              class="w-full !py-4"
              :loading="isLoading"
              :disabled="isLoading"
            />
          </form>

          <div class="text-center">
            <button
              @click="handleResendCode"
              :disabled="isLoading || resendCountdown > 0"
              class="text-xs font-bold uppercase tracking-widest transition-colors"
              :class="resendCountdown > 0 ? 'text-gray-400' : 'text-[#0078d4] hover:underline'"
            >
              {{ resendCountdown > 0 ? `Retry in ${resendCountdown}s` : 'Resend Security Code' }}
            </button>
          </div>
        </div>

        <!-- Step 3: New Password Input -->
        <div v-if="currentStep === 'password'" class="space-y-6">
          <div class="p-4 bg-blue-50 dark:bg-blue-900/10 rounded-xl mb-6">
            <p class="text-xs font-bold text-[#0078d4] uppercase tracking-widest text-center">
              Identity Confirmed. Establish New Credentials.
            </p>
          </div>

          <form @submit.prevent="handleResetPassword" class="space-y-6">
            <FormInput
              v-model="formData.newPassword"
              type="password"
              label="New Security Password"
              placeholder="••••••••"
              :error="errors.newPassword"
              hint="Min 8 characters, letters & numbers"
              required
            />

            <FormInput
              v-model="formData.confirmPassword"
              type="password"
              label="Confirm Credentials"
              placeholder="••••••••"
              :error="errors.confirmPassword"
              required
            />

            <FormButton
              label="Secure Account"
              type="submit"
              variant="primary"
              class="w-full !py-4 shadow-lg shadow-blue-500/20"
              :loading="isLoading"
              :disabled="isLoading"
            />
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import FormInput from '@/shared/components/ui/FormInput.vue'
import FormButton from '@/shared/components/ui/FormButton.vue'
import { apiClient } from '@/shared/services/api'

const router = useRouter()

type Step = 'email' | 'code' | 'password'

const currentStep = ref<Step>('email')
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const resendCountdown = ref(0)
let resendTimer: ReturnType<typeof setTimeout> | null = null

const formData = reactive({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})

const errors = reactive({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})

const validateEmail = (): boolean => {
  errors.email = ''

  if (!formData.email) {
    errors.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Invalid email address'
  }

  return !errors.email
}

const validateCode = (): boolean => {
  errors.code = ''

  if (!formData.code) {
    errors.code = 'Verification code is required'
  } else if (!/^\d{6}$/.test(formData.code)) {
    errors.code = 'Code must be 6 digits'
  }

  return !errors.code
}

const validatePassword = (): boolean => {
  errors.newPassword = ''
  errors.confirmPassword = ''

  if (!formData.newPassword) {
    errors.newPassword = 'New password is required'
  } else if (formData.newPassword.length < 8) {
    errors.newPassword = 'Password must be at least 8 characters'
  } else if (!/[a-zA-Z]/.test(formData.newPassword) || !/[0-9]/.test(formData.newPassword)) {
    errors.newPassword = 'Password must contain letters and numbers'
  }

  if (!formData.confirmPassword) {
    errors.confirmPassword = 'Confirm password is required'
  } else if (formData.newPassword !== formData.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
  }

  return !errors.newPassword && !errors.confirmPassword
}

const handleSendReset = async () => {
  if (!validateEmail()) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await apiClient.post('/auth/forgot-password', {
      email: formData.email
    })

    successMessage.value = 'Verification code sent to your email'
    currentStep.value = 'code'
    startResendCountdown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to send code'
  } finally {
    isLoading.value = false
  }
}

const handleVerifyCode = async () => {
  if (!validateCode()) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await apiClient.post('/auth/verify-reset-code', {
      email: formData.email,
      code: formData.code
    })

    successMessage.value = 'Code verified successfully'
    currentStep.value = 'password'
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Invalid code'
  } finally {
    isLoading.value = false
  }
}

const handleResetPassword = async () => {
  if (!validatePassword()) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await apiClient.post('/auth/reset-password', {
      email: formData.email,
      code: formData.code,
      new_password: formData.newPassword
    })

    successMessage.value = 'Password updated successfully'
    setTimeout(() => {
      router.push('/auth/login')
    }, 2000)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to update password'
  } finally {
    isLoading.value = false
  }
}

const handleResendCode = async () => {
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await apiClient.post('/auth/resend-reset-code', {
      email: formData.email
    })

    successMessage.value = 'Code resent'
    startResendCountdown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to resend'
  } finally {
    isLoading.value = false
  }
}

const startResendCountdown = () => {
  resendCountdown.value = 60

  if (resendTimer) {
    clearInterval(resendTimer)
  }

  resendTimer = setInterval(() => {
    resendCountdown.value--
    if (resendCountdown.value <= 0) {
      if (resendTimer) {
        clearInterval(resendTimer)
      }
    }
  }, 1000)
}

onUnmounted(() => {
  if (resendTimer) {
    clearInterval(resendTimer)
  }
})
</script>
