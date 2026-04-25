<template>
  <div class="space-y-8 pb-12">
    <!-- Page Header -->
    <div class="relative overflow-hidden py-12 px-6 rounded-2xl bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-950 border border-gray-100 dark:border-gray-800 shadow-sm mb-8 flex flex-col md:flex-row md:items-center gap-8">
      <!-- Profile Avatar Placeholder -->
      <div class="relative z-10 w-24 h-24 bg-[#0078d4]/10 rounded-2xl border-4 border-white dark:border-gray-800 shadow-xl flex items-center justify-center overflow-hidden flex-shrink-0">
        <span class="text-3xl font-extrabold text-[#0078d4]">{{ authStore.user?.full_name?.charAt(0) || 'U' }}</span>
        <div class="absolute inset-0 bg-gradient-to-tr from-[#0078d4]/20 to-transparent"></div>
      </div>

      <div class="relative z-10">
        <h1 class="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Hello, <span class="text-[#0078d4]">{{ authStore.user?.full_name || 'Professional' }}</span>
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-2 leading-relaxed">
          Manage your professional presence and account settings.
        </p>
      </div>
      <div class="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-[#0078d4]/5 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <ErrorState v-else-if="error" :message="error" class="mb-6" />

    <!-- Profile Content -->
    <div v-else class="max-w-5xl mx-auto space-y-8">
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard
          label="Saved Careers"
          :value="stats.savedJobsCount"
          variant="primary"
        />
        <StatsCard
          label="Active Alerts"
          :value="stats.activeAlertsCount"
          variant="success"
        />
        <StatsCard
          label="Membership"
          :value="memberSinceText"
          variant="info"
        />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Form Area -->
        <div class="lg:col-span-2 space-y-8">
          <!-- User Info Card -->
          <div class="fluent-card bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-8 shadow-sm">
            <div class="flex items-center justify-between mb-8">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">Account Information</h2>
              <FormButton
                v-if="!isEditing"
                variant="secondary"
                size="sm"
                @click="startEdit"
              >
                Edit Profile
              </FormButton>
            </div>
            
            <!-- Messages -->
            <transition name="fade">
              <div v-if="profileSuccess" class="mb-6 p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800 flex items-center gap-3">
                <svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <p class="text-sm font-bold text-green-700 dark:text-green-400">{{ profileSuccess }}</p>
              </div>
            </transition>

            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormInput
                  v-model="formData.full_name"
                  label="Full Name"
                  :disabled="!isEditing"
                  :error="isEditing ? fieldErrors.full_name : ''"
                  @blur="validateField('full_name')"
                />
                <FormInput
                  v-model="formData.email"
                  label="Email Address"
                  disabled
                  hint="Managed account email"
                />
              </div>
              
              <FormInput
                v-model="formData.phone"
                label="Phone Number"
                placeholder="+1 (555) 000-0000"
                :disabled="!isEditing"
                :error="fieldErrors.phone"
                @blur="validateField('phone')"
              />

              <div>
                <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-widest text-[10px]">Professional Bio</label>
                <textarea
                  v-model="formData.bio"
                  placeholder="Share a brief overview of your professional background..."
                  :disabled="!isEditing"
                  class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-transparent focus:border-[#0078d4] rounded-xl text-sm focus:ring-4 focus:ring-[#0078d4]/10 dark:text-white transition-all shadow-inner disabled:opacity-60 resize-none"
                  rows="4"
                ></textarea>
                <p v-if="fieldErrors.bio" class="text-red-500 text-xs mt-2 font-medium">{{ fieldErrors.bio }}</p>
              </div>
            </div>

            <!-- Action Buttons -->
            <transition name="fade">
              <div v-if="isEditing" class="flex gap-4 mt-8 pt-8 border-t border-gray-50 dark:border-gray-800">
                <FormButton
                  variant="primary"
                  class="flex-1"
                  :loading="savingProfile"
                  :disabled="!isFormValid"
                  @click="saveProfile"
                >
                  Save Changes
                </FormButton>
                <FormButton
                  variant="secondary"
                  class="flex-1"
                  @click="cancelEdit"
                  :disabled="savingProfile"
                >
                  Cancel
                </FormButton>
              </div>
            </transition>
          </div>

          <!-- Preferences Card -->
          <div class="fluent-card bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-8 shadow-sm">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-8">Communication Preferences</h2>
            
            <div class="space-y-6">
              <FormCheckbox
                v-model="preferences.emailNotifications"
                label="Instant Job Alerts"
                hint="Receive an email the moment a matching job is found"
              />

              <FormCheckbox
                v-model="preferences.pushNotifications"
                label="Browser Notifications"
                hint="Stay updated with real-time desktop alerts"
              />

              <FormCheckbox
                v-model="preferences.weeklyDigest"
                label="Weekly Career Digest"
                hint="A curated summary of opportunities every Monday"
              />
            </div>

            <div class="mt-8 pt-8 border-t border-gray-50 dark:border-gray-800">
              <FormButton
                variant="primary"
                :loading="savingPreferences"
                @click="savePreferences"
              >
                Update Preferences
              </FormButton>
            </div>
          </div>
        </div>

        <!-- Sidebar Area -->
        <div class="space-y-8">
          <!-- Password Change Card -->
          <div class="fluent-card bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-6">Security</h2>
            
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
                label="Confirm New"
              />
            </div>

            <FormButton
              variant="secondary"
              class="w-full mt-6"
              :loading="changingPassword"
              @click="changePassword"
            >
              Change Password
            </FormButton>
          </div>

          <!-- Danger Zone -->
          <div class="fluent-card bg-red-50/30 dark:bg-red-900/10 rounded-2xl border border-red-100 dark:border-red-900/30 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-red-700 dark:text-red-400 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Danger Zone
            </h2>
            
            <p class="text-xs text-red-600 dark:text-red-400/70 mb-6 leading-relaxed font-medium">
              Once you delete your account, there is no going back. Please be certain.
            </p>

            <FormButton
              variant="danger"
              class="w-full"
              @click="deleteAccount"
            >
              Delete My Account
            </FormButton>
          </div>
        </div>
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
