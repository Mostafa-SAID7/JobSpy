<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Alerts</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Manage job alerts and receive notifications when new jobs matching your criteria are available</p>
      </div>
      <button
        @click="openCreateModal"
        class="px-6 py-2 rounded-lg font-medium transition-all duration-200 bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex items-center justify-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Alert
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && alerts.length === 0" class="text-center py-12">
      <div class="inline-block">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
      <p class="text-gray-600 dark:text-gray-400 mt-4">Loading alerts...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <div>
          <p class="text-red-800 dark:text-red-200 font-medium">خطأ</p>
          <p class="text-red-700 dark:text-red-300 text-sm mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="alerts.length === 0" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-12 text-center">
      <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">No alerts created yet</h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">Create alerts to receive notifications when new jobs matching your criteria are available</p>
      <button
        @click="openCreateModal"
        class="px-6 py-2 rounded-lg font-medium transition-all duration-200 bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Create Alert Now
      </button>
    </div>

    <!-- Statistics Cards -->
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatsCard
        label="Total Alerts"
        :value="totalAlerts"
        variant="primary"
        :icon="BellIcon"
      />
      <StatsCard
        label="Active Alerts"
        :value="activeAlerts"
        variant="success"
        :icon="CheckCircleIcon"
      />
      <StatsCard
        label="New Jobs"
        :value="totalNewJobs"
        variant="info"
        :icon="BriefcaseIcon"
      />
    </div>

    <!-- Alerts List -->
    <div v-if="alerts.length > 0" class="space-y-4">
      <AlertCard
        v-for="alert in alerts"
        :key="alert.id"
        :alert="alert"
        :is-operating="operatingAlertId === alert.id"
        @toggle-active="toggleAlert(alert.id)"
        @edit="editAlert(alert)"
        @delete="deleteAlert(alert.id)"
      />
    </div>

    <!-- Create/Edit Alert Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full shadow-xl">
        <!-- Modal Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ editingAlert ? 'Edit Alert' : 'Create New Alert' }}
          </h2>
          <button
            @click="closeModal"
            :disabled="isSubmitting"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 disabled:opacity-50"
            aria-label="Close"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <!-- Form Error Message -->
          <div v-if="formError" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <p class="text-red-800 dark:text-red-200 text-sm">{{ formError }}</p>
            </div>
          </div>

          <!-- Form Success Message -->
          <div v-if="formSuccess" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <p class="text-green-800 dark:text-green-200 text-sm">{{ formSuccess }}</p>
            </div>
          </div>

          <FormInput
            v-model="formData.name"
            type="text"
            label="Alert Name"
            placeholder="Example: Software Engineer in Cairo"
            required
            :disabled="isSubmitting"
            aria-label="Alert Name"
            @blur="validateField('name')"
          />
          <p v-if="fieldErrors.name" class="text-red-600 dark:text-red-400 text-sm mt-1">{{ fieldErrors.name }}</p>

          <FormInput
            v-model="formData.query"
            type="text"
            label="Search Query"
            placeholder="Example: Vue.js Developer"
            required
            :disabled="isSubmitting"
            aria-label="Search Query"
            @blur="validateField('query')"
          />
          <p v-if="fieldErrors.query" class="text-red-600 dark:text-red-400 text-sm mt-1">{{ fieldErrors.query }}</p>

          <FormSelect
            v-model="formData.frequency"
            label="Alert Frequency"
            :options="frequencyOptions"
            :disabled="isSubmitting"
            aria-label="Alert Frequency"
          />

          <FormSelect
            v-model="formData.notification_method"
            label="Notification Method"
            :options="notificationOptions"
            :disabled="isSubmitting"
            aria-label="Notification Method"
          />

          <!-- Modal Footer -->
          <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="submit"
              :disabled="isSubmitting || !isFormValid"
              class="flex-1 px-6 py-2 rounded-lg font-medium transition-all duration-200 bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isSubmitting" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
              <span v-else>{{ editingAlert ? 'Update Alert' : 'Create Alert' }}</span>
            </button>
            <button
              type="button"
              @click="closeModal"
              :disabled="isSubmitting"
              class="flex-1 px-6 py-2 rounded-lg font-medium transition-all duration-200 bg-gray-200 text-gray-800 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useJobsStore } from '@/stores/jobs'
import FormInput from '@/components/forms/FormInput.vue'
import FormSelect from '@/components/forms/FormSelect.vue'
import AlertCard from '@/components/cards/AlertCard.vue'
import StatsCard from '@/components/cards/StatsCard.vue'

// Icons
const BellIcon = 'svg'
const CheckCircleIcon = 'svg'
const BriefcaseIcon = 'svg'

const jobsStore = useJobsStore()

const isLoading = ref(false)
const isSubmitting = ref(false)
const error = ref('')
const formError = ref('')
const formSuccess = ref('')
const showModal = ref(false)
const editingAlert = ref<any>(null)
const operatingAlertId = ref<string | null>(null)

const frequencyOptions = [
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
]

const notificationOptions = [
  { value: 'email', label: 'Email' },
  { value: 'in_app', label: 'In-App Notification' },
]

const formData = ref({
  name: '',
  query: '',
  frequency: 'daily',
  notification_method: 'email',
})

const fieldErrors = ref({
  name: '',
  query: '',
})

const alerts = computed(() => jobsStore.alerts)

/**
 * Calculate total alerts
 * Validates: Requirements 6.1
 */
const totalAlerts = computed(() => alerts.value.length)

/**
 * Calculate active alerts
 * Validates: Requirements 6.1, 6.5
 */
const activeAlerts = computed(() => alerts.value.filter(a => a.is_active).length)

/**
 * Calculate total new jobs from all alerts
 * Validates: Requirements 6.4
 */
const totalNewJobs = computed(() => {
  return alerts.value.reduce((sum, alert) => sum + (alert.new_jobs_count || 0), 0)
})

/**
 * Check if form is valid
 * Validates: Requirements 6.1
 */
const isFormValid = computed(() => {
  return formData.value.name.trim().length > 0 &&
         formData.value.query.trim().length > 0 &&
         formData.value.frequency &&
         formData.value.notification_method
})

/**
 * Validate individual form field
 * Validates: Requirements 6.1
 */
const validateField = (field: string) => {
  if (field === 'name') {
    if (formData.value.name.trim().length === 0) {
      fieldErrors.value.name = 'Alert name is required'
    } else if (formData.value.name.length > 255) {
      fieldErrors.value.name = 'Alert name must be less than 255 characters'
    } else {
      fieldErrors.value.name = ''
    }
  } else if (field === 'query') {
    if (formData.value.query.trim().length === 0) {
      fieldErrors.value.query = 'Search query is required'
    } else if (formData.value.query.length > 255) {
      fieldErrors.value.query = 'Search query must be less than 255 characters'
    } else {
      fieldErrors.value.query = ''
    }
  }
}

const openCreateModal = () => {
  editingAlert.value = null
  formData.value = {
    name: '',
    query: '',
    frequency: 'daily',
    notification_method: 'email',
  }
  fieldErrors.value = { name: '', query: '' }
  formError.value = ''
  formSuccess.value = ''
  showModal.value = true
}

const editAlert = (alert: any) => {
  editingAlert.value = alert
  formData.value = {
    name: alert.name,
    query: alert.query,
    frequency: alert.frequency,
    notification_method: alert.notification_method,
  }
  fieldErrors.value = { name: '', query: '' }
  formError.value = ''
  formSuccess.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingAlert.value = null
  formData.value = {
    name: '',
    query: '',
    frequency: 'daily',
    notification_method: 'email',
  }
  fieldErrors.value = { name: '', query: '' }
  formError.value = ''
  formSuccess.value = ''
}

/**
 * Handle form submission for creating/updating alerts
 * Validates: Requirements 6.1, 6.5
 */
const handleSubmit = async () => {
  formError.value = ''
  formSuccess.value = ''
  
  // Validate form
  validateField('name')
  validateField('query')
  
  if (!isFormValid.value) {
    formError.value = 'Please fix the errors in the form'
    return
  }

  isSubmitting.value = true

  try {
    if (editingAlert.value) {
      await jobsStore.updateAlert(editingAlert.value.id, formData.value)
      formSuccess.value = 'Alert updated successfully'
    } else {
      await jobsStore.createAlert(formData.value)
      formSuccess.value = 'Alert created successfully'
    }
    
    // Close modal after short delay to show success message
    setTimeout(() => {
      closeModal()
    }, 1000)
  } catch (err: any) {
    formError.value = err.response?.data?.detail || 'An error occurred while saving the alert'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * Toggle alert active/inactive status
 * Validates: Requirements 6.1, 6.5
 */
const toggleAlert = async (alertId: string) => {
  const alert = alerts.value.find(a => a.id === alertId)
  if (!alert) return

  error.value = ''
  operatingAlertId.value = alertId

  try {
    await jobsStore.updateAlert(alertId, {
      is_active: !alert.is_active,
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to update alert'
  } finally {
    operatingAlertId.value = null
  }
}

/**
 * Delete alert with confirmation
 * Validates: Requirements 6.5
 */
const deleteAlert = async (alertId: string) => {
  if (!confirm('Are you sure you want to delete this alert? This action cannot be undone.')) return

  error.value = ''
  operatingAlertId.value = alertId

  try {
    await jobsStore.deleteAlert(alertId)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to delete alert'
  } finally {
    operatingAlertId.value = null
  }
}

/**
 * Fetch all alerts for current user
 * Validates: Requirements 6.1
 */
const fetchAlerts = async () => {
  isLoading.value = true
  error.value = ''

  try {
    await jobsStore.fetchAlerts()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load alerts'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAlerts()
})
</script>
