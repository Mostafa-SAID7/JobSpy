<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">إنشاء حساب جديد</h1>
          <p class="text-gray-600">انضم إلينا واكتشف فرص عمل رائعة</p>
        </div>

        <!-- Error Message -->
        <div
          v-if="authStore.error"
          class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-red-700 text-sm">{{ authStore.error }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleRegister" class="space-y-4">
          <!-- Full Name Input -->
          <FormInput
            v-model="formData.fullName"
            type="text"
            label="الاسم الكامل"
            placeholder="أحمد محمد"
            :error="errors.fullName"
            required
          />

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

          <!-- Terms & Conditions -->
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="formData.agreeToTerms"
              type="checkbox"
              class="w-4 h-4 mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700">
              أوافق على
              <a href="#" class="text-blue-600 hover:text-blue-700">شروط الخدمة</a>
              و
              <a href="#" class="text-blue-600 hover:text-blue-700">سياسة الخصوصية</a>
            </span>
          </label>
          <p v-if="errors.agreeToTerms" class="text-sm text-red-500">
            {{ errors.agreeToTerms }}
          </p>

          <!-- Submit Button -->
          <FormButton
            label="إنشاء الحساب"
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

        <!-- Login Link -->
        <p class="text-center text-gray-600">
          هل لديك حساب بالفعل؟
          <RouterLink
            to="/auth/login"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            تسجيل الدخول
          </RouterLink>
        </p>
      </div>
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
    errors.fullName = 'الاسم الكامل مطلوب'
  } else if (formData.fullName.length < 3) {
    errors.fullName = 'الاسم يجب أن يكون 3 أحرف على الأقل'
  }

  if (!formData.email) {
    errors.email = 'البريد الإلكتروني مطلوب'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'البريد الإلكتروني غير صحيح'
  }

  if (!formData.password) {
    errors.password = 'كلمة المرور مطلوبة'
  } else if (formData.password.length < 8) {
    errors.password = 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'
  } else if (!/[a-zA-Z]/.test(formData.password) || !/[0-9]/.test(formData.password)) {
    errors.password = 'كلمة المرور يجب أن تحتوي على أحرف وأرقام'
  }

  if (!formData.confirmPassword) {
    errors.confirmPassword = 'تأكيد كلمة المرور مطلوب'
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = 'كلمات المرور غير متطابقة'
  }

  if (!formData.agreeToTerms) {
    errors.agreeToTerms = 'يجب أن توافق على شروط الخدمة'
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
