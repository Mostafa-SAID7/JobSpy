<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Profile</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">Manage your account information and settings</p>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <ErrorState v-else-if="error" :message="error" class="mb-6" />

    <!-- Profile Content -->
    <div v-else class="space-y-6">
      <!-- Stats Section -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatsCard
          label="Saved Jobs"
          :value="stats.savedJobsCount"
          variant="primary"
          :icon="BookmarkIcon"
        />
        <StatsCard
          label="Active Alerts"
          :value="stats.activeAlertsCount"
          variant="success"
          :icon="BellIcon"
        />
        <StatsCard
          label="Member Since"
          :value="memberSinceText"
          variant="info"
          :icon="CalendarIcon"
        />
      </div>

      <!-- User Info Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Account Information</h2>
        
        <!-- Success Message -->
        <div v-if="profileSuccess" class="mb-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <p class="text-green-800 dark:text-green-200 text-sm">{{ profileSuccess }}</p>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="profileError" class="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <p class="text-red-800 dark:text-red-200 text-sm">{{ profileError }}</p>
          </div>
        </div>
        
        <div class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormInput
              v-model="formData.full_name"
              type="text"
              label="Full Name"
              :disabled="!isEditing"
              :error="isEditing ? fieldErrors.full_name : ''"
              @blur="validateField('full_name')"
            />
            <FormInput
              v-model="formData.email"
              type="email"
              label="Email"
              disabled
              hint="Email cannot be changed"
            />
          </div>
          <FormInput
            v-if="isEditing"
            v-model="formData.phone"
            type="tel"
            label="Phone Number"
            placeholder="Example: +1234567890"
            :disabled="!isEditing"
            :error="fieldErrors.phone"
            @blur="validateField('phone')"
          />
          <div v-if="isEditing">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bio</label>
            <textarea
              v-model="formData.bio"
              placeholder="Tell us about yourself..."
              :disabled="!isEditing"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed"
              rows="4"
            ></textarea>
            <p v-if="fieldErrors.bio" class="text-red-600 dark:text-red-400 text-sm mt-1">{{ fieldErrors.bio }}</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3 mt-6">
          <FormButton
            v-if="!isEditing"
            variant="primary"
            label="Edit"
            @click="startEdit"
          />
          <template v-else>
            <FormButton
              variant="success"
              :disabled="savingProfile || !isFormValid"
              :loading="savingProfile"
              label="Save Changes"
              @click="saveProfile"
            />
            <FormButton
              variant="outline"
              label="Cancel"
              @click="cancelEdit"
              :disabled="savingProfile"
            />
          </template>
        </div>
      </div>

      <!-- Password Change Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Change Password</h2>
        
        <div class="space-y-4">
          <FormInput
            v-model="passwordData.currentPassword"
            type="password"
            label="Current Password"
          />

          <FormInput
            v-model="passwordData.newPassword"
            type="password"
            label="New Password"
          />

          <FormInput
            v-model="passwordData.confirmPassword"
            type="password"
            label="Confirm New Password"
          />
        </div>

        <FormButton
          variant="primary"
          :disabled="changingPassword"
          :loading="changingPassword"
          label="Update Password"
          @click="changePassword"
          class="mt-6"
        />
      </div>

      <!-- Preferences Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Preferences</h2>
        
        <!-- Success Message -->
        <div v-if="preferencesSuccess" class="mb-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <p class="text-green-800 dark:text-green-200 text-sm">{{ preferencesSuccess }}</p>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="preferencesError" class="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <p class="text-red-800 dark:text-red-200 text-sm">{{ preferencesError }}</p>
          </div>
        </div>
        
        <div class="space-y-4">
          <FormCheckbox
            v-model="preferences.emailNotifications"
            label="Receive Email Notifications"
            hint="Get notified when new jobs matching your criteria are available"
          />

          <FormCheckbox
            v-model="preferences.pushNotifications"
            label="Receive Web Notifications"
            hint="Get instant notifications in the browser"
          />

          <FormCheckbox
            v-model="preferences.weeklyDigest"
            label="Receive Weekly Digest"
            hint="Get a weekly digest of new jobs"
          />

          <FormCheckbox
            v-model="preferences.darkMode"
            label="Dark Mode"
            hint="Use dark mode to reduce eye strain"
          />
        </div>

        <FormButton
          variant="primary"
          :disabled="savingPreferences"
          :loading="savingPreferences"
          label="Save Preferences"
          @click="savePreferences"
          class="mt-6"
        />
      </div>

      <!-- Danger Zone -->
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
        <h2 class="text-xl font-semibold text-red-900 dark:text-red-200 mb-4">Danger Zone</h2>
        
        <p class="text-red-800 dark:text-red-300 mb-4">
          Deleting your account will delete all profile data, saved jobs, and alerts. This action cannot be undone.
        </p>

        <FormButton
          variant="danger"
          label="Delete Account"
          @click="deleteAccount"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { apiClient } from '@/services/api'
import FormInput from '@/components/forms/FormInput.vue'
import FormCheckbox from '@/components/forms/FormCheckbox.vue'
import FormButton from '@/components/forms/FormButton.vue'
import StatsCard from '@/components/cards/StatsCard.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorState from '@/components/common/ErrorState.vue'

// Icons (using simple SVG components)
const BookmarkIcon = {
  template: `<svg fill="currentColor" viewBox="0 0 24 24"><path d="M5 5a2 2 0 012-2h6a2 2 0 012 2v16l-8-4-8 4V5z"/></svg>`
}

const BellIcon = {
  template: `<svg fill="currentColor" viewBox="0 0 24 24"><path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0018 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>`
}

const CalendarIcon = {
  template: `<svg fill="currentColor" viewBox="0 0 24 24"><path d="M6 2a1 1 0 00-1 1v2H4a2 2 0 00-2 2v2h20V7a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v2H7V3a1 1 0 00-1-1zm0 5H4v12a2 2 0 002 2h12a2 2 0 002-2V7h-2v2a1 1 0 11-2 0V7H8v2a1 1 0 11-2 0V7z"/></svg>`
}

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const isEditing = ref(false)
const savingProfile = ref(false)
const changingPassword = ref(false)
const savingPreferences = ref(false)
const profileError = ref('')
const profileSuccess = ref('')

const formData = ref({
  full_name: '',
  email: '',
  phone: '',
  bio: '',
})

const fieldErrors = ref({
  full_name: '',
  email: '',
  phone: '',
  bio: '',
})

const passwordData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const preferences = ref({
  emailNotifications: true,
  pushNotifications: true,
  weeklyDigest: true,
  darkMode: false,
})

const preferencesError = ref('')
const preferencesSuccess = ref('')

const stats = ref({
  savedJobsCount: 0,
  activeAlertsCount: 0,
})

const originalFormData = ref({
  full_name: '',
  email: '',
  phone: '',
  bio: '',
})

const memberSinceText = computed(() => {
  if (!authStore.user?.created_at) return 'N/A'
  const date = new Date(authStore.user.created_at)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
})

/**
 * Check if form is valid
 * Validates: Requirements 7.6.2
 */
const isFormValid = computed(() => {
  return formData.value.full_name.trim().length > 0 &&
         formData.value.full_name.length <= 255 &&
         (!formData.value.phone || /^[\d\s\-\+\(\)]+$/.test(formData.value.phone)) &&
         (!formData.value.bio || formData.value.bio.length <= 1000)
})

onMounted(async () => {
  loading.value = true
  try {
    // Load user profile from store
    if (authStore.user) {
      formData.value = {
        full_name: authStore.user.full_name || '',
        email: authStore.user.email || '',
        phone: authStore.user.phone || '',
        bio: authStore.user.bio || '',
      }
      originalFormData.value = { ...formData.value }
    }

    // Load preferences from auth store
    loadPreferences()

    // Fetch stats
    await fetchStats()
  } catch (err) {
    error.value = 'Failed to load profile'
    console.error(err)
  } finally {
    loading.value = false
  }
})

const fetchStats = async () => {
  try {
    // Fetch saved jobs count
    const savedJobsResponse = await apiClient.get('/saved-jobs?limit=1')
    stats.value.savedJobsCount = savedJobsResponse.data.total || 0

    // Fetch alerts count
    const alertsResponse = await apiClient.get('/alerts')
    stats.value.activeAlertsCount = alertsResponse.data.items?.filter((a: any) => a.is_active).length || 0
  } catch (err) {
    console.error('Failed to fetch stats:', err)
  }
}

/**
 * Validate individual form field
 * Validates: Requirements 7.6.2
 */
const validateField = (field: string) => {
  if (field === 'full_name') {
    if (formData.value.full_name.trim().length === 0) {
      fieldErrors.value.full_name = 'Full name is required'
    } else if (formData.value.full_name.length > 255) {
      fieldErrors.value.full_name = 'Full name must be less than 255 characters'
    } else {
      fieldErrors.value.full_name = ''
    }
  } else if (field === 'phone') {
    if (formData.value.phone && !/^[\d\s\-\+\(\)]+$/.test(formData.value.phone)) {
      fieldErrors.value.phone = 'Invalid phone number'
    } else {
      fieldErrors.value.phone = ''
    }
  } else if (field === 'bio') {
    if (formData.value.bio && formData.value.bio.length > 1000) {
      fieldErrors.value.bio = 'Bio must be less than 1000 characters'
    } else {
      fieldErrors.value.bio = ''
    }
  }
}

/**
 * Start edit mode
 * Validates: Requirements 7.6.2
 */
const startEdit = () => {
  isEditing.value = true
  profileError.value = ''
  profileSuccess.value = ''
}

/**
 * Save profile changes to API
 * Validates: Requirements 7.6.2
 */
const saveProfile = async () => {
  profileError.value = ''
  profileSuccess.value = ''
  
  // Validate all fields
  validateField('full_name')
  validateField('phone')
  validateField('bio')
  
  if (!isFormValid.value) {
    profileError.value = 'Please correct the errors in the form'
    return
  }

  savingProfile.value = true

  try {
    const updateData: any = {
      full_name: formData.value.full_name,
    }
    
    // Only include optional fields if they have values
    if (formData.value.phone) {
      updateData.phone = formData.value.phone
    }
    if (formData.value.bio) {
      updateData.bio = formData.value.bio
    }

    const response = await apiClient.put('/users/me', updateData)
    
    // Update auth store with new user data
    if (authStore.user) {
      authStore.user.full_name = response.data.full_name
      if (response.data.phone) authStore.user.phone = response.data.phone
      if (response.data.bio) authStore.user.bio = response.data.bio
    }
    
    originalFormData.value = { ...formData.value }
    isEditing.value = false
    profileSuccess.value = 'Changes saved successfully'
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      profileSuccess.value = ''
    }, 3000)
  } catch (err: any) {
    profileError.value = err.response?.data?.detail || 'Failed to save changes'
    console.error('Profile update error:', err)
  } finally {
    savingProfile.value = false
  }
}

/**
 * Cancel edit mode and restore original data
 * Validates: Requirements 7.6.2
 */
const cancelEdit = () => {
  isEditing.value = false
  formData.value = { ...originalFormData.value }
  fieldErrors.value = {
    full_name: '',
    email: '',
    phone: '',
    bio: '',
  }
  profileError.value = ''
  profileSuccess.value = ''
}

const changePassword = async () => {
  if (passwordData.value.newPassword !== passwordData.value.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }

  if (passwordData.value.newPassword.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  changingPassword.value = true
  try {
    // Note: This endpoint would need to be implemented in the backend
    // For now, we'll show a placeholder
    error.value = 'Change password feature is in development'
    
    passwordData.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to change password'
  } finally {
    changingPassword.value = false
  }
}

const savePreferences = async () => {
  preferencesError.value = ''
  preferencesSuccess.value = ''
  savingPreferences.value = true

  try {
    // Save preferences to auth store
    authStore.setPreferences({
      notificationsEnabled: preferences.value.emailNotifications,
      emailNotifications: preferences.value.emailNotifications,
    })

    // Try to save to backend if endpoint exists
    try {
      await apiClient.put('/users/me/preferences', {
        email_notifications: preferences.value.emailNotifications,
        push_notifications: preferences.value.pushNotifications,
        weekly_digest: preferences.value.weeklyDigest,
        dark_mode: preferences.value.darkMode,
      })
    } catch (backendErr: any) {
      // If backend endpoint doesn't exist, just use local storage
      if (backendErr.response?.status !== 404) {
        throw backendErr
      }
    }

    preferencesSuccess.value = 'Preferences saved successfully'
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      preferencesSuccess.value = ''
    }, 3000)
  } catch (err: any) {
    preferencesError.value = err.response?.data?.detail || 'Failed to save preferences'
    console.error('Preferences save error:', err)
  } finally {
    savingPreferences.value = false
  }
}

/**
 * Load preferences from auth store
 * Validates: Requirements 7.6.3
 */
const loadPreferences = () => {
  authStore.loadPreferences()
  
  // Load from auth store preferences
  if (authStore.preferences) {
    preferences.value.emailNotifications = authStore.preferences.notificationsEnabled ?? true
    preferences.value.darkMode = authStore.preferences.theme === 'dark'
  }
}

const deleteAccount = async () => {
  if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    try {
      await apiClient.delete('/users/me')
      await authStore.logout()
      router.push({ name: 'Home' })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete account'
    }
  }
}
</script>
