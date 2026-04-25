<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">Create a new account</h1>
          <p class="text-gray-600">Join us and discover great job opportunities</p>
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
            label="Full Name"
            placeholder="John Doe"
            :error="errors.fullName"
            required
          />

          <!-- Email Input -->
          <FormInput
            v-model="formData.email"
            type="email"
            label="Email"
            placeholder="example@email.com"
            :error="errors.email"
            required
          />

          <!-- Password Input -->
          <FormInput
            v-model="formData.password"
            type="password"
            label="Password"
            placeholder="••••••••"
            :error="errors.password"
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

          <!-- Terms & Conditions -->
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="formData.agreeToTerms"
              type="checkbox"
              class="w-4 h-4 mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700">
              I agree to
              <a href="#" class="text-blue-600 hover:text-blue-700">Terms of Service</a>
              and
              <a href="#" class="text-blue-600 hover:text-blue-700">Privacy Policy</a>
            </span>
          </label>
          <p v-if="errors.agreeToTerms" class="text-sm text-red-500">
            {{ errors.agreeToTerms }}
          </p>

          <!-- Submit Button -->
          <FormButton
            label="Create Account"
            type="submit"
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
            class="w-full"
          />
        </form>

        <!-- Divider -->
        <div class="my-6 flex items-center gap-4">
          <div class="flex-1 h-px bg-gray-300"></div>
          <span class="text-gray-500 text-sm">or</span>
          <div class="flex-1 h-px bg-gray-300"></div>
        </div>

        <!-- Login Link -->
        <p class="text-center text-gray-600">
          Already have an account?
          <RouterLink
            to="/auth/login"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Log in
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
