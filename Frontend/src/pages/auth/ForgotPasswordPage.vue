<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">Reset Password</h1>
          <p class="text-gray-600">Enter your email to reset your password</p>
        </div>

        <!-- Success Message -->
        <div
          v-if="successMessage"
          class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <p class="text-green-700 text-sm">{{ successMessage }}</p>
        </div>

        <!-- Error Message -->
        <div
          v-if="errorMessage"
          class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-red-700 text-sm">{{ errorMessage }}</p>
        </div>

        <!-- Step 1: Email Input -->
        <div v-if="currentStep === 'email'" class="space-y-4">
          <form @submit.prevent="handleSendReset" class="space-y-4">
            <!-- Email Input -->
            <FormInput
              v-model="formData.email"
              type="email"
              label="Email"
              placeholder="example@email.com"
              :error="errors.email"
              required
            />

            <!-- Submit Button -->
            <FormButton
              label="Send Reset Link"
              type="submit"
              :loading="isLoading"
              :disabled="isLoading"
              class="w-full"
            />
          </form>
        </div>

        <!-- Step 2: Reset Code Input -->
        <div v-if="currentStep === 'code'" class="space-y-4">
          <p class="text-sm text-gray-600 mb-4">
            Verification code sent to your email. Enter it below.
          </p>

          <form @submit.prevent="handleVerifyCode" class="space-y-4">
            <!-- Code Input -->
            <FormInput
              v-model="formData.code"
              type="text"
              label="Verification Code"
              placeholder="000000"
              :error="errors.code"
              hint="Enter the 6-digit code"
              required
            />

            <!-- Submit Button -->
            <FormButton
              label="Verify Code"
              type="submit"
              :loading="isLoading"
              :disabled="isLoading"
              class="w-full"
            />
          </form>

          <!-- Resend Code -->
          <p class="text-center text-sm text-gray-600">
            Didn't receive the code?
            <button
              @click="handleResendCode"
              :disabled="isLoading || resendCountdown > 0"
              class="text-blue-600 hover:text-blue-700 font-medium disabled:text-gray-400"
            >
              {{ resendCountdown > 0 ? `Resend after ${resendCountdown}s` : 'Resend' }}
            </button>
          </p>
        </div>

        <!-- Step 3: New Password Input -->
        <div v-if="currentStep === 'password'" class="space-y-4">
          <p class="text-sm text-gray-600 mb-4">
            Enter your new password.
          </p>

          <form @submit.prevent="handleResetPassword" class="space-y-4">
            <!-- New Password Input -->
            <FormInput
              v-model="formData.newPassword"
              type="password"
              label="New Password"
              placeholder="••••••••"
              :error="errors.newPassword"
              hint="Must be at least 8 characters and contain letters and numbers"
              required
            />

            <!-- Confirm Password Input -->
            <FormInput
              v-model="formData.confirmPassword"
              type="password"
              label="Confirm Password"
              placeholder="••••••••"
              :error="errors.confirmPassword"
              required
            />

            <!-- Submit Button -->
            <FormButton
              label="Update Password"
              type="submit"
              :loading="isLoading"
              :disabled="isLoading"
              class="w-full"
            />
          </form>
        </div>

        <!-- Divider -->
        <div class="my-6 flex items-center gap-4">
          <div class="flex-1 h-px bg-gray-300"></div>
          <span class="text-gray-500 text-sm">or</span>
          <div class="flex-1 h-px bg-gray-300"></div>
        </div>

        <!-- Back to Login -->
        <p class="text-center text-gray-600">
          Remembered your password?
          <RouterLink
            to="/auth/login"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Back to Login
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import FormInput from '@/components/forms/FormInput.vue'
import FormButton from '@/components/forms/FormButton.vue'
import { apiClient } from '@/services/api'

const router = useRouter()

type Step = 'email' | 'code' | 'password'

const currentStep = ref<Step>('email')
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const resendCountdown = ref(0)
let resendTimer: NodeJS.Timeout | null = null

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
