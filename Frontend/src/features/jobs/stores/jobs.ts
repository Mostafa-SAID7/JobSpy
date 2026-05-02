/**
 * Jobs Store - Pinia Store
 * Jobs store for JobSpy
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Job, SearchParams } from '@/types'
import { apiClient } from '@/shared/services/api'

export const useJobsStore = defineStore('jobs', () => {
  // State
  const jobs = ref<Job[]>([])
  const currentJob = ref<Job | null>(null)
  const totalCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchParams = ref<SearchParams>({
    query: '',
    skip: 0,
    limit: 20,
  })
  const savedJobs = ref<Job[]>([])
  const alerts = ref<any[]>([])

  // Computed
  const hasMore = computed(() => searchParams.value.skip + searchParams.value.limit < totalCount.value)

  // Methods
  const searchJobs = async (params: Partial<SearchParams> = {}) => {
    isLoading.value = true
    error.value = null

    try {
      searchParams.value = { ...searchParams.value, ...params }

      // Check if we need advanced search
      const advancedKeys = ['location', 'job_type', 'experience_level', 'salary_min', 'salary_max', 'is_remote']
      const hasAdvancedParams = Object.keys(searchParams.value).some(key => 
        advancedKeys.includes(key) && searchParams.value[key as keyof SearchParams] !== undefined && searchParams.value[key as keyof SearchParams] !== null && searchParams.value[key as keyof SearchParams] !== ''
      )

      const endpoint = hasAdvancedParams ? '/jobs/search/advanced' : '/jobs'
      const response = await apiClient.get(endpoint, {
        params: searchParams.value,
      })

      // Handle response mapping (backend returns same structure for both)
      jobs.value = response.data.items || response.data.results || []
      totalCount.value = response.data.total || response.data.total_count || 0
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error searching for jobs'
    } finally {
      isLoading.value = false
    }
  }

  const getJobDetails = async (jobId: number | string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get(`/jobs/${jobId}`)
      currentJob.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error loading job details'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const loadMore = async () => {
    searchParams.value.skip += searchParams.value.limit
    await searchJobs()
  }

  const resetSearch = () => {
    jobs.value = []
    currentJob.value = null
    totalCount.value = 0
    searchParams.value = {
      query: '',
      skip: 0,
      limit: 20,
    }
  }

  // Saved Jobs Methods
  const addSavedJob = async (jobId: number | string, notes?: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.post('/saved-jobs', {
        job_id: jobId,
        notes: notes || null,
      })
      
      // Add to local state
      if (response.data.job && !savedJobs.value.find(j => j.id === response.data.job.id)) {
        savedJobs.value.push(response.data.job)
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to save job'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const removeSavedJob = async (savedJobId: number | string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await apiClient.delete(`/saved-jobs/${savedJobId}`)
      
      // Remove from local state
      savedJobs.value = savedJobs.value.filter(j => j.id !== savedJobId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to remove saved job'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchSavedJobs = async (skip: number = 0, limit: number = 100) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.get('/saved-jobs', {
        params: {
          skip,
          limit,
        },
      })
      
      // Extract jobs from saved jobs response
      const jobs = response.data.items.map((item: any) => item.job)
      savedJobs.value = jobs
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load saved jobs'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const isSavedJob = (jobId: number | string): boolean => {
    return savedJobs.value.some(j => j.id === jobId)
  }

  // Alerts Methods
  const createAlert = async (alertData: any) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.post('/alerts', {
        name: alertData.name,
        query: alertData.query,
        frequency: alertData.frequency,
        notification_method: alertData.notification_method || 'email',
        filters: alertData.filters || {},
      })
      
      alerts.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create alert'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateAlert = async (alertId: string, alertData: any) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.put(`/alerts/${alertId}`, alertData)
      
      const index = alerts.value.findIndex(a => a.id === alertId)
      if (index !== -1) {
        alerts.value[index] = response.data
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update alert'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteAlert = async (alertId: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await apiClient.delete(`/alerts/${alertId}`)
      alerts.value = alerts.value.filter(a => a.id !== alertId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete alert'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchAlerts = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.get('/alerts')
      alerts.value = response.data.items || []
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load alerts'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchDashboardStats = async () => {
    try {
      const response = await apiClient.get('/stats/dashboard')
      return response.data.data
    } catch (err) {
      console.error('Failed to fetch dashboard stats:', err)
      return null
    }
  }

  const scrapeJobs = async (params: { 
    query: string; 
    location?: string; 
    site_names?: string[]; 
    max_results?: number;
    distance?: number;
    easy_apply?: boolean;
  }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/jobs/scrape', params)
      
      // Refresh the search after scraping to show new results
      await searchJobs({ query: params.query })
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error scraping jobs'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    jobs,
    currentJob,
    totalCount,
    isLoading,
    error,
    searchParams,
    hasMore,
    savedJobs,
    alerts,
    searchJobs,
    scrapeJobs,
    getJobDetails,
    loadMore,
    resetSearch,
    addSavedJob,
    removeSavedJob,
    fetchSavedJobs,
    isSavedJob,
    createAlert,
    updateAlert,
    deleteAlert,
    fetchAlerts,
    fetchDashboardStats,
  }
})
