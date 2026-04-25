/**
 * Main JobSpy Application
 * Main entry point for JobSpy Vue application
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/index.css'
import { useAuthStore } from './stores/auth'
import { useUIStore } from './stores/ui'
import { usePreferencesStore } from './stores/preferences'

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
