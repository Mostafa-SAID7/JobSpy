import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useJobsStore } from '../jobs'

vi.mock('@/services/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('Jobs Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial state', () => {
    it('should have correct initial state', () => {
      const store = useJobsStore()

      expect(store.jobs).toEqual([])
      expect(store.savedJobs).toEqual([])
      expect(store.alerts).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('Search jobs', () => {
    it('should search jobs successfully', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      const mockJobs = [
        {
          id: 1,
          title: 'Developer',
          company: 'Tech Corp',
          location: 'Remote',
          salary_min: 100000,
          salary_max: 150000,
          salary_currency: 'USD',
          job_type: 'fulltime',
          description: 'Job description',
          source_url: 'https://example.com',
          source_job_id: 'job_1',
          posted_date: new Date().toISOString(),
          source: 'linkedin',
          is_remote: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]

      vi.mocked(apiClient.get).mockResolvedValue({
        data: { results: mockJobs, total: 1 },
      })

      await store.searchJobs({ query: 'developer' })

      expect(store.jobs).toEqual(mockJobs)
      expect(store.error).toBeNull()
    })

    it('should handle search error', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      const error = new Error('Search failed') as any
      error.response = { data: { detail: 'Search failed' } }

      vi.mocked(apiClient.get).mockRejectedValue(error)

      await store.searchJobs({ query: 'developer' })

      expect(store.jobs).toEqual([])
      expect(store.error).toBeTruthy()
    })

    it('should set loading state during search', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      vi.mocked(apiClient.get).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve({ data: { results: [], total: 0 } }), 100)
          })
      )

      const searchPromise = store.searchJobs({ query: 'developer' })
      expect(store.isLoading).toBe(true)

      await searchPromise
      expect(store.isLoading).toBe(false)
    })
  })

  describe('Save job', () => {
    it('should save job successfully', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      const mockJob = {
        id: 1,
        title: 'Developer',
        company: 'Tech Corp',
        location: 'Remote',
        salary_min: 100000,
        salary_max: 150000,
        salary_currency: 'USD',
        job_type: 'fulltime',
        description: 'Job description',
        source_url: 'https://example.com',
        source_job_id: 'job_1',
        posted_date: new Date().toISOString(),
        source: 'linkedin',
        is_remote: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      vi.mocked(apiClient.post).mockResolvedValue({
        data: { job: mockJob },
      })

      await store.addSavedJob(1)

      expect(store.savedJobs).toContainEqual(mockJob)
    })

    it('should handle save error', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      const error = new Error('Save failed') as any
      error.response = { data: { detail: 'Save failed' } }

      vi.mocked(apiClient.post).mockRejectedValue(error)

      try {
        await store.addSavedJob(1)
      } catch (e) {
        // Expected
      }

      expect(store.error).toBeTruthy()
    })
  })

  describe('Unsave job', () => {
    it('should remove job from saved jobs', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      store.savedJobs = [
        {
          id: 1,
          title: 'Developer',
          company: 'Tech Corp',
          location: 'Remote',
          salary_min: 100000,
          salary_max: 150000,
          salary_currency: 'USD',
          job_type: 'fulltime',
          description: 'Job description',
          source_url: 'https://example.com',
          source_job_id: 'job_1',
          posted_date: new Date().toISOString(),
          source: 'linkedin',
          is_remote: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]

      vi.mocked(apiClient.delete).mockResolvedValue({})

      await store.removeSavedJob(1)

      expect(store.savedJobs).toEqual([])
    })
  })

  describe('Alerts management', () => {
    it('should fetch alerts', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      const mockAlerts = [
        {
          id: 1,
          name: 'Python Developer',
          query: 'Python',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
        },
      ]

      vi.mocked(apiClient.get).mockResolvedValue({
        data: { items: mockAlerts },
      })

      await store.fetchAlerts()

      expect(store.alerts).toEqual(mockAlerts)
    })

    it('should create alert', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      const mockAlert = {
        id: 1,
        name: 'Python Developer',
        query: 'Python',
        frequency: 'daily',
        notification_method: 'email',
        is_active: true,
        created_at: new Date().toISOString(),
      }

      vi.mocked(apiClient.post).mockResolvedValue({
        data: mockAlert,
      })

      await store.createAlert({
        name: 'Python Developer',
        query: 'Python',
        frequency: 'daily',
        notification_method: 'email',
      })

      expect(store.alerts).toContainEqual(mockAlert)
    })

    it('should update alert', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      store.alerts = [
        {
          id: 1,
          name: 'Python Developer',
          query: 'Python',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
        },
      ]

      const updatedAlert = {
        ...store.alerts[0],
        frequency: 'weekly',
      }

      vi.mocked(apiClient.put).mockResolvedValue({
        data: updatedAlert,
      })

      await store.updateAlert('1', { frequency: 'weekly' })

      expect(apiClient.put).toHaveBeenCalledWith('/alerts/1', { frequency: 'weekly' })
    })

    it('should delete alert', async () => {
      const { apiClient } = await import('@/services/api')
      const store = useJobsStore()
      store.alerts = [
        {
          id: 1,
          name: 'Python Developer',
          query: 'Python',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
        },
      ]

      vi.mocked(apiClient.delete).mockResolvedValue({})

      await store.deleteAlert('1')

      expect(apiClient.delete).toHaveBeenCalledWith('/alerts/1')
    })
  })
})
