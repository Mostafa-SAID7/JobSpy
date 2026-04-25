/**
 * UI Store - Pinia Store
 * UI store for global state
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { setLocalStorage, getLocalStorage } from '@/utils/useLocalStorage'

export interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

export interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  notificationsEnabled: boolean
}

export const useUIStore = defineStore('ui', () => {
  // State
  const toasts = ref<Toast[]>([])
  const sidebarOpen = ref<boolean>(
    getLocalStorage<boolean>('sidebarOpen') ?? false
  )
  const theme = ref<'light' | 'dark'>(
    (getLocalStorage<'light' | 'dark'>('theme')) || 'light'
  )
  const notificationsEnabled = ref<boolean>(
    getLocalStorage<boolean>('notificationsEnabled') ?? true
  )

  // Methods
  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', duration = 3000) => {
    const id = Date.now().toString()
    const toast: Toast = { id, message, type, duration }

    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  const removeToast = (id: string) => {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
    setLocalStorage('sidebarOpen', sidebarOpen.value)
  }

  const closeSidebar = () => {
    sidebarOpen.value = false
    setLocalStorage('sidebarOpen', sidebarOpen.value)
  }

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    setLocalStorage('theme', newTheme)

    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const setNotificationsEnabled = (enabled: boolean) => {
    notificationsEnabled.value = enabled
    setLocalStorage('notificationsEnabled', enabled)
  }

  return {
    toasts,
    sidebarOpen,
    theme,
    notificationsEnabled,
    showToast,
    removeToast,
    toggleSidebar,
    closeSidebar,
    setTheme,
    setNotificationsEnabled,
  }
})
