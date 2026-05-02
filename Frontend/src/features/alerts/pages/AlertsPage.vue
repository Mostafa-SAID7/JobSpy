<template>
  <div class="space-y-8 pb-12">
    <!-- Page Header -->
    <div class="relative overflow-hidden py-12 px-6 rounded-2xl bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-950 border border-gray-100 dark:border-gray-800 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div class="relative z-10 max-w-2xl">
        <h1 class="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Job <span class="text-[#0078d4]">Alerts</span>
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-4 leading-relaxed">
          Stay ahead of the curve. Get notified the moment new jobs matching your interests are posted.
        </p>
      </div>
      <div class="relative z-10 flex-shrink-0">
        <FormButton
          variant="primary"
          @click="openCreateModal"
          class="shadow-lg shadow-[#0078d4]/20"
        >
          <template #icon>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </template>
          Create Alert
        </FormButton>
      </div>
      <div class="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-[#0078d4]/5 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Statistics Overview -->
    <div v-if="alerts.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <StatsCard
        label="Total Alerts"
        :value="totalAlerts"
        variant="primary"
      />
      <StatsCard
        label="Active Now"
        :value="activeAlerts"
        variant="success"
      />
      <StatsCard
        label="New Matches"
        :value="totalNewJobs"
        variant="info"
      />
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="isLoading && alerts.length === 0" text="Syncing alerts..." />

    <!-- Error State -->
    <ErrorState v-else-if="error" :message="error" />

    <!-- Content Area -->
    <div v-else class="max-w-4xl mx-auto w-full">
      <!-- Empty State -->
      <EmptyState
        v-if="alerts.length === 0"
        title="Never miss an opportunity"
        message="Create your first job alert and we'll let you know as soon as matching positions appear."
        action-text="Setup My First Alert"
        @action-click="openCreateModal"
      >
        <template #icon>
          <div class="w-20 h-20 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6 border border-gray-100 dark:border-gray-700">
            <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
        </template>
      </EmptyState>

      <!-- Alerts List -->
      <div v-if="alerts.length > 0" class="space-y-4">
        <transition-group name="list">
          <AlertCard
            v-for="alert in alerts"
            :key="alert.id"
            :alert="alert"
            :is-operating="operatingAlertId === alert.id"
            @toggle-active="toggleAlert(alert.id)"
            @edit="editAlert(alert)"
            @delete="deleteAlert(alert.id)"
          />
        </transition-group>
      </div>
    </div>

    <!-- Create/Edit Alert Modal -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center z-50 p-4">
      <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="closeModal"></div>
      
      <div class="bg-white dark:bg-gray-900 rounded-2xl max-w-md w-full shadow-2xl relative z-10 overflow-hidden border border-gray-100 dark:border-gray-800 transform transition-all scale-100">
        <!-- Modal Header -->
        <div class="p-6 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-gray-50/50 dark:bg-gray-800/50">
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">
              {{ editingAlert ? 'Edit Alert' : 'New Job Alert' }}
            </h2>
            <p class="text-xs text-gray-500 mt-1 font-medium">Define your search criteria</p>
          </div>
          <button
            @click="closeModal"
            class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
          <!-- Form Messages -->
          <transition name="fade">
            <div v-if="formError" class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 flex items-center gap-3">
              <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <p class="text-xs font-bold text-red-700 dark:text-red-400">{{ formError }}</p>
            </div>
          </transition>

          <div class="space-y-4">
            <FormInput
              v-model="formData.name"
              label="Alert Label"
              placeholder="e.g., Senior Vue Developer - Hybrid"
              required
              @blur="validateField('name')"
              :error="fieldErrors.name"
            />

            <FormInput
              v-model="formData.query"
              label="Search Terms"
              placeholder="e.g., frontend engineer, typescript"
              required
              @blur="validateField('query')"
              :error="fieldErrors.query"
            />

            <div class="grid grid-cols-2 gap-4">
              <FormSelect
                v-model="formData.frequency"
                label="Check Frequency"
                :options="frequencyOptions"
              />

              <FormSelect
                v-model="formData.notification_method"
                label="Delivery"
                :options="notificationOptions"
              />
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="flex gap-3 pt-4">
            <FormButton
              type="button"
              variant="secondary"
              class="flex-1"
              @click="closeModal"
            >
              Cancel
            </FormButton>
            <FormButton
              type="submit"
              variant="primary"
              class="flex-1"
              :loading="isSubmitting"
              :disabled="!isFormValid"
            >
              {{ editingAlert ? 'Update' : 'Activate' }}
            </FormButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useJobsStore } from '@/features/jobs/stores/jobs'
import FormInput from '@/shared/components/ui/FormInput.vue'
import FormSelect from '@/shared/components/ui/FormSelect.vue'
import FormButton from '@/shared/components/ui/FormButton.vue'
import AlertCard from '../components/AlertCard.vue'
import StatsCard from '@/shared/components/common/StatsCard.vue'
import LoadingSpinner from '@/shared/components/common/LoadingSpinner.vue'
import ErrorState from '@/shared/components/common/ErrorState.vue'
import EmptyState from '@/shared/components/common/EmptyState.vue'

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
  return !!(formData.value.name.trim().length > 0 &&
           formData.value.query.trim().length > 0 &&
           formData.value.frequency &&
           formData.value.notification_method)
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
