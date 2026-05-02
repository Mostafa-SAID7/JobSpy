/**
 * Authentication Store - Pinia Store
 * Authentication store for JobSpy
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { apiClient } from '@/shared/services/api'
import { setLocalStorage, getLocalStorage, removeLocalStorage } from '@/shared/utils/useLocalStorage'

export interface UserPreferences {
  theme: 'light' | 'dark'
  language: string
  notificationsEnabled: boolean
  emailNotifications: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const preferences = ref<UserPreferences>({
    theme: 'light',
    language: 'en',
    notificationsEnabled: true,
    emailNotifications: true,
  })

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Methods
  const login = async (email: string, password: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/auth/login', { email, password })
      token.value = response.data.access_token
      user.value = response.data.user

      if (token.value) {
        localStorage.setItem('token', token.value)
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      }

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login error'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (
    email: string,
    password: string,
    full_name: string
  ) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
        full_name,
      })
      token.value = response.data.access_token
      user.value = response.data.user

      if (token.value) {
        localStorage.setItem('token', token.value)
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      }

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration error'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
      removeLocalStorage('token')
      removeLocalStorage('userPreferences')
      delete apiClient.defaults.headers.common['Authorization']
    }
  }

  const setPreferences = (newPreferences: Partial<UserPreferences>) => {
    preferences.value = { ...preferences.value, ...newPreferences }
    setLocalStorage('userPreferences', preferences.value)
  }

  const loadPreferences = () => {
    const stored = getLocalStorage<UserPreferences>('userPreferences')
    if (stored) {
      preferences.value = stored
    }
  }

  const checkAuth = async () => {
    if (!token.value) return

    try {
      const response = await apiClient.get('/users/me')
      user.value = response.data
    } catch (err) {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    }
  }

  const refreshToken = async () => {
    try {
      const response = await apiClient.post('/auth/refresh')
      token.value = response.data.access_token
      if (token.value) {
        localStorage.setItem('token', token.value)
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      }
      return true
    } catch (err) {
      await logout()
      return false
    }
  }

  return {
    user,
    token,
    isLoading,
    error,
    preferences,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
    refreshToken,
    setPreferences,
    loadPreferences,
  }
})
