/**
 * Main JobSpy Application
 * Main entry point for JobSpy Vue application
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './app/App.vue'
import router from './app/router'
import './assets/styles/index.css'
import { useAuthStore } from './features/auth/stores/auth'
import { useUIStore } from './stores/ui'
import { usePreferencesStore } from './features/profile/stores/preferences'

// Global error handler for browser extension conflicts
window.addEventListener('error', (event) => {
  // Suppress service worker and cache-related errors from extensions
  if (
    event.error?.message?.includes('chrome-extension') ||
    event.error?.message?.includes('Cache') ||
    event.filename?.includes('sw.js') ||
    event.filename?.includes('content_script')
  ) {
    console.warn('Browser extension error suppressed:', event.error?.message)
    event.preventDefault()
    return false
  }
})

// Handle unhandled promise rejections from extensions
window.addEventListener('unhandledrejection', (event) => {
  if (
    event.reason?.message?.includes('chrome-extension') ||
    event.reason?.message?.includes('Cache') ||
    event.reason?.toString?.()?.includes('sw.js')
  ) {
    console.warn('Browser extension promise rejection suppressed:', event.reason)
    event.preventDefault()
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize stores from localStorage on app startup
const initializeStores = () => {
  const authStore = useAuthStore()
  const uiStore = useUIStore()
  const preferencesStore = usePreferencesStore()

  // Load user preferences
  authStore.loadPreferences()

  // Load all preferences
  preferencesStore.loadAllPreferences()

  // Apply theme from UI store
  if (uiStore.theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }

  // Check authentication on app startup
  if (authStore.token) {
    authStore.checkAuth()
  }
}

// Initialize stores before mounting
initializeStores()

app.mount('#app')
