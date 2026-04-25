import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

vi.mock('@/services/api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    defaults: {
      headers: {
        common: {},
      },
    },
  },
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial state', () => {
    it('should have correct initial state', () => {
      const store = useAuthStore()

      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('Login action', () => {
    it('should login user successfully', async () => {
      const { apiClient } = await import('@/services/api')
      const mockResponse = {
        data: {
          access_token: 'test-token',
          user: { id: '1', email: 'test@example.com', full_name: 'Test User' },
        },
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const store = useAuthStore()
      await store.login('test@example.com', 'password123')

      expect(store.isAuthenticated).toBe(true)
      expect(store.user).toEqual(mockResponse.data.user)
      expect(store.token).toBe('test-token')
      expect(store.error).toBeNull()
    })

    it('should handle login error', async () => {
      const { apiClient } = await import('@/services/api')
      const error = new Error('Invalid credentials')
      error.response = { data: { detail: 'Invalid credentials' } }

      vi.mocked(apiClient.post).mockRejectedValue(error)

      const store = useAuthStore()
      await store.login('test@example.com', 'wrongpassword')

      expect(store.isAuthenticated).toBe(false)
      expect(store.error).toBeTruthy()
    })

    it('should set loading state during login', async () => {
      const { apiClient } = await import('@/services/api')
      vi.mocked(apiClient.post).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(
              () =>
                resolve({
                  data: { access_token: 'token', user: { id: '1', email: 'test@example.com' } },
                }),
              100
            )
          })
      )

      const store = useAuthStore()
      const loginPromise = store.login('test@example.com', 'password')
      expect(store.isLoading).toBe(true)

      await loginPromise
      expect(store.isLoading).toBe(false)
    })
  })

  describe('Register action', () => {
    it('should register user successfully', async () => {
      const { apiClient } = await import('@/services/api')
      const mockResponse = {
        data: {
          access_token: 'test-token',
          user: { id: '1', email: 'newuser@example.com', full_name: 'New User' },
        },
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const store = useAuthStore()
      await store.register('newuser@example.com', 'password123', 'New User')

      expect(store.isAuthenticated).toBe(true)
      expect(store.user).toEqual(mockResponse.data.user)
      expect(store.token).toBe('test-token')
    })

    it('should handle registration error', async () => {
      const { apiClient } = await import('@/services/api')
      const error = new Error('Email already exists')
      error.response = { data: { detail: 'Email already exists' } }

      vi.mocked(apiClient.post).mockRejectedValue(error)

      const store = useAuthStore()
      await store.register('existing@example.com', 'password', 'User')

      expect(store.isAuthenticated).toBe(false)
      expect(store.error).toBeTruthy()
    })
  })

  describe('Logout action', () => {
    it('should logout user', async () => {
      const { apiClient } = await import('@/services/api')
      vi.mocked(apiClient.post).mockResolvedValue({})

      const store = useAuthStore()
      store.user = { id: '1', email: 'test@example.com', full_name: 'Test User' }
      store.token = 'test-token'

      await store.logout()

      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
    })
  })

  describe('Token management', () => {
    it('should check auth', async () => {
      const { apiClient } = await import('@/services/api')
      const mockUser = { id: '1', email: 'test@example.com', full_name: 'Test User' }

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockUser })

      const store = useAuthStore()
      store.token = 'existing-token'
      await store.checkAuth()

      expect(store.user).toEqual(mockUser)
    })

    it('should clear session if token is invalid', async () => {
      const { apiClient } = await import('@/services/api')
      const error = new Error('Unauthorized')

      vi.mocked(apiClient.get).mockRejectedValue(error)

      const store = useAuthStore()
      store.token = 'invalid-token'
      await store.checkAuth()

      expect(store.isAuthenticated).toBe(false)
      expect(store.token).toBeNull()
    })
  })

  describe('Error handling', () => {
    it('should clear error on successful action', async () => {
      const { apiClient } = await import('@/services/api')
      const mockResponse = {
        data: {
          access_token: 'test-token',
          user: { id: '1', email: 'test@example.com', full_name: 'Test User' },
        },
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const store = useAuthStore()
      store.error = 'Previous error'

      await store.login('test@example.com', 'password')

      expect(store.error).toBeNull()
    })
  })
})
