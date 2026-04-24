/**
 * متجر التفضيلات - Pinia Store
 * Preferences store for search and UI preferences
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SearchParams } from '@/types'
import { setLocalStorage, getLocalStorage, removeLocalStorage } from '@/utils/useLocalStorage'

export interface SavedSearch {
  id: string
  name: string
  params: SearchParams
  createdAt: string
}

export interface SearchPreferences {
  defaultLimit: number
  defaultSort: 'relevance' | 'date' | 'salary'
  savedSearches: SavedSearch[]
}

export interface UIPreferences {
  layoutMode: 'grid' | 'list'
  itemsPerPage: number
  showFilters: boolean
}

export interface NotificationSettings {
  emailNotifications: boolean
  pushNotifications: boolean
  alertFrequency: 'immediate' | 'daily' | 'weekly'
}

export const usePreferencesStore = defineStore('preferences', () => {
  // State
  const searchPreferences = ref<SearchPreferences>(
    getLocalStorage<SearchPreferences>('searchPreferences') || {
      defaultLimit: 20,
      defaultSort: 'relevance',
      savedSearches: [],
    }
  )

  const uiPreferences = ref<UIPreferences>(
    getLocalStorage<UIPreferences>('uiPreferences') || {
      layoutMode: 'grid',
      itemsPerPage: 20,
      showFilters: true,
    }
  )

  const notificationSettings = ref<NotificationSettings>(
    getLocalStorage<NotificationSettings>('notificationSettings') || {
      emailNotifications: true,
      pushNotifications: true,
      alertFrequency: 'daily',
    }
  )

  // Methods - Search Preferences
  const updateSearchPreferences = (updates: Partial<SearchPreferences>) => {
    searchPreferences.value = { ...searchPreferences.value, ...updates }
    setLocalStorage('searchPreferences', searchPreferences.value)
  }

  const addSavedSearch = (search: SavedSearch) => {
    searchPreferences.value.savedSearches.push(search)
    setLocalStorage('searchPreferences', searchPreferences.value)
  }

  const removeSavedSearch = (searchId: string) => {
    searchPreferences.value.savedSearches = searchPreferences.value.savedSearches.filter(
      (s) => s.id !== searchId
    )
    setLocalStorage('searchPreferences', searchPreferences.value)
  }

  const updateSavedSearch = (searchId: string, updates: Partial<SavedSearch>) => {
    const index = searchPreferences.value.savedSearches.findIndex((s) => s.id === searchId)
    if (index !== -1) {
      searchPreferences.value.savedSearches[index] = {
        ...searchPreferences.value.savedSearches[index],
        ...updates,
      }
      setLocalStorage('searchPreferences', searchPreferences.value)
    }
  }

  const getSavedSearch = (searchId: string): SavedSearch | undefined => {
    return searchPreferences.value.savedSearches.find((s) => s.id === searchId)
  }

  // Methods - UI Preferences
  const updateUIPreferences = (updates: Partial<UIPreferences>) => {
    uiPreferences.value = { ...uiPreferences.value, ...updates }
    setLocalStorage('uiPreferences', uiPreferences.value)
  }

  const setLayoutMode = (mode: 'grid' | 'list') => {
    uiPreferences.value.layoutMode = mode
    setLocalStorage('uiPreferences', uiPreferences.value)
  }

  const setItemsPerPage = (count: number) => {
    uiPreferences.value.itemsPerPage = count
    setLocalStorage('uiPreferences', uiPreferences.value)
  }

  const toggleShowFilters = () => {
    uiPreferences.value.showFilters = !uiPreferences.value.showFilters
    setLocalStorage('uiPreferences', uiPreferences.value)
  }

  // Methods - Notification Settings
  const updateNotificationSettings = (updates: Partial<NotificationSettings>) => {
    notificationSettings.value = { ...notificationSettings.value, ...updates }
    setLocalStorage('notificationSettings', notificationSettings.value)
  }

  const setEmailNotifications = (enabled: boolean) => {
    notificationSettings.value.emailNotifications = enabled
    setLocalStorage('notificationSettings', notificationSettings.value)
  }

  const setPushNotifications = (enabled: boolean) => {
    notificationSettings.value.pushNotifications = enabled
    setLocalStorage('notificationSettings', notificationSettings.value)
  }

  const setAlertFrequency = (frequency: 'immediate' | 'daily' | 'weekly') => {
    notificationSettings.value.alertFrequency = frequency
    setLocalStorage('notificationSettings', notificationSettings.value)
  }

  // Methods - General
  const loadAllPreferences = () => {
    const search = getLocalStorage<SearchPreferences>('searchPreferences')
    if (search) searchPreferences.value = search

    const ui = getLocalStorage<UIPreferences>('uiPreferences')
    if (ui) uiPreferences.value = ui

    const notifications = getLocalStorage<NotificationSettings>('notificationSettings')
    if (notifications) notificationSettings.value = notifications
  }

  const resetAllPreferences = () => {
    searchPreferences.value = {
      defaultLimit: 20,
      defaultSort: 'relevance',
      savedSearches: [],
    }
    uiPreferences.value = {
      layoutMode: 'grid',
      itemsPerPage: 20,
      showFilters: true,
    }
    notificationSettings.value = {
      emailNotifications: true,
      pushNotifications: true,
      alertFrequency: 'daily',
    }

    removeLocalStorage('searchPreferences')
    removeLocalStorage('uiPreferences')
    removeLocalStorage('notificationSettings')
  }

  return {
    // State
    searchPreferences,
    uiPreferences,
    notificationSettings,
    // Search Methods
    updateSearchPreferences,
    addSavedSearch,
    removeSavedSearch,
    updateSavedSearch,
    getSavedSearch,
    // UI Methods
    updateUIPreferences,
    setLayoutMode,
    setItemsPerPage,
    toggleShowFilters,
    // Notification Methods
    updateNotificationSettings,
    setEmailNotifications,
    setPushNotifications,
    setAlertFrequency,
    // General Methods
    loadAllPreferences,
    resetAllPreferences,
  }
})
