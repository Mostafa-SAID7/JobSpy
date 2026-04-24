<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">استعادة كلمة المرور</h1>
          <p class="text-gray-600">أدخل بريدك الإلكتروني لاستعادة كلمة المرور</p>
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
              label="البريد الإلكتروني"
              placeholder="example@email.com"
              :error="errors.email"
              required
            />

            <!-- Submit Button -->
            <FormButton
              label="إرسال رابط الاستعادة"
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
            تم إرسال رمز التحقق إلى بريدك الإلكتروني. أدخله أدناه.
          </p>

          <form @submit.prevent="handleVerifyCode" class="space-y-4">
            <!-- Code Input -->
            <FormInput
              v-model="formData.code"
              type="text"
              label="رمز التحقق"
              placeholder="000000"
              :error="errors.code"
              hint="أدخل الرمز المكون من 6 أرقام"
              required
            />

            <!-- Submit Button -->
            <FormButton
              label="التحقق من الرمز"
              type="submit"
              :loading="isLoading"
              :disabled="isLoading"
              class="w-full"
            />
          </form>

          <!-- Resend Code -->
          <p class="text-center text-sm text-gray-600">
            لم تستقبل الرمز؟
            <button
              @click="handleResendCode"
              :disabled="isLoading || resendCountdown > 0"
              class="text-blue-600 hover:text-blue-700 font-medium disabled:text-gray-400"
            >
              {{ resendCountdown > 0 ? `إعادة الإرسال بعد ${resendCountdown}s` : 'إعادة الإرسال' }}
            </button>
          </p>
        </div>

        <!-- Step 3: New Password Input -->
        <div v-if="currentStep === 'password'" class="space-y-4">
          <p class="text-sm text-gray-600 mb-4">
            أدخل كلمة المرور الجديدة الخاصة بك.
          </p>

          <form @submit.prevent="handleResetPassword" class="space-y-4">
            <!-- New Password Input -->
            <FormInput
              v-model="formData.newPassword"
              type="password"
              label="كلمة المرور الجديدة"
              placeholder="••••••••"
              :error="errors.newPassword"
              hint="يجب أن تكون 8 أحرف على الأقل وتحتوي على أحرف وأرقام"
              required
            />

            <!-- Confirm Password Input -->
            <FormInput
              v-model="formData.confirmPassword"
              type="password"
              label="تأكيد كلمة المرور"
              placeholder="••••••••"
              :error="errors.confirmPassword"
              required
            />

            <!-- Submit Button -->
            <FormButton
              label="تحديث كلمة المرور"
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
          <span class="text-gray-500 text-sm">أو</span>
          <div class="flex-1 h-px bg-gray-300"></div>
        </div>

        <!-- Back to Login -->
        <p class="text-center text-gray-600">
          تذكرت كلمة المرور؟
          <RouterLink
            to="/auth/login"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            العودة إلى تسجيل الدخول
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
    errors.email = 'البريد الإلكتروني مطلوب'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'البريد الإلكتروني غير صحيح'
  }

  return !errors.email
}

const validateCode = (): boolean => {
  errors.code = ''

  if (!formData.code) {
    errors.code = 'رمز التحقق مطلوب'
  } else if (!/^\d{6}$/.test(formData.code)) {
    errors.code = 'الرمز يجب أن يكون 6 أرقام'
  }

  return !errors.code
}

const validatePassword = (): boolean => {
  errors.newPassword = ''
  errors.confirmPassword = ''

  if (!formData.newPassword) {
    errors.newPassword = 'كلمة المرور الجديدة مطلوبة'
  } else if (formData.newPassword.length < 8) {
    errors.newPassword = 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'
  } else if (!/[a-zA-Z]/.test(formData.newPassword) || !/[0-9]/.test(formData.newPassword)) {
    errors.newPassword = 'كلمة المرور يجب أن تحتوي على أحرف وأرقام'
  }

  if (!formData.confirmPassword) {
    errors.confirmPassword = 'تأكيد كلمة المرور مطلوب'
  } else if (formData.newPassword !== formData.confirmPassword) {
    errors.confirmPassword = 'كلمات المرور غير متطابقة'
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

    successMessage.value = 'تم إرسال رمز التحقق إلى بريدك الإلكتروني'
    currentStep.value = 'code'
    startResendCountdown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'حدث خطأ في إرسال الرمز'
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

    successMessage.value = 'تم التحقق من الرمز بنجاح'
    currentStep.value = 'password'
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'الرمز غير صحيح'
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

    successMessage.value = 'تم تحديث كلمة المرور بنجاح'
    setTimeout(() => {
      router.push('/auth/login')
    }, 2000)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'حدث خطأ في تحديث كلمة المرور'
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

    successMessage.value = 'تم إعادة إرسال الرمز'
    startResendCountdown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'حدث خطأ في إعادة الإرسال'
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
