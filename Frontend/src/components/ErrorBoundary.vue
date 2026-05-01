<template>
  <div v-if="hasError" class="error-boundary">
    <div class="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            Application Error
          </h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ errorMessage }}</p>
            <p class="mt-2 text-xs text-red-600">
              This error may be caused by browser extensions. Try disabling extensions or using incognito mode.
            </p>
          </div>
          <div class="mt-4">
            <div class="flex space-x-2">
              <button
                @click="retry"
                class="bg-red-100 px-2 py-1 text-xs font-medium text-red-800 rounded hover:bg-red-200"
              >
                Retry
              </button>
              <button
                @click="reload"
                class="bg-red-100 px-2 py-1 text-xs font-medium text-red-800 rounded hover:bg-red-200"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured, onMounted } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')

// Capture Vue component errors
onErrorCaptured((error: Error) => {
  // Only show error boundary for extension-related errors
  if (
    error.message.includes('chrome-extension') ||
    error.message.includes('Cache') ||
    error.message.includes('sw.js') ||
    error.message.includes('content_script')
  ) {
    hasError.value = true
    errorMessage.value = 'Browser extension conflict detected'
    return false // Prevent error from propagating
  }
  
  // Let other errors propagate normally
  return true
})

// Handle global errors
onMounted(() => {
  const handleError = (event: ErrorEvent) => {
    if (
      event.error?.message?.includes('chrome-extension') ||
      event.error?.message?.includes('Cache') ||
      event.filename?.includes('sw.js') ||
      event.filename?.includes('content_script')
    ) {
      hasError.value = true
      errorMessage.value = 'Browser extension conflict detected'
      event.preventDefault()
    }
  }

  const handleRejection = (event: PromiseRejectionEvent) => {
    if (
      event.reason?.message?.includes('chrome-extension') ||
      event.reason?.message?.includes('Cache') ||
      event.reason?.toString?.()?.includes('sw.js')
    ) {
      hasError.value = true
      errorMessage.value = 'Browser extension conflict detected'
      event.preventDefault()
    }
  }

  window.addEventListener('error', handleError)
  window.addEventListener('unhandledrejection', handleRejection)

  // Cleanup
  return () => {
    window.removeEventListener('error', handleError)
    window.removeEventListener('unhandledrejection', handleRejection)
  }
})

const retry = () => {
  hasError.value = false
  errorMessage.value = ''
}

const reload = () => {
  window.location.reload()
}
</script>

<style scoped>
.error-boundary {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>