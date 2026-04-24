import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ProfilePage from '../ProfilePage.vue'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/services/api'

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    post: vi.fn(),
  },
}))

describe('ProfilePage.vue - Profile Update', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders profile page with header', () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    expect(wrapper.find('h1').text()).toContain('الملف الشخصي')
  })

  it('displays loading state initially', () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    expect(wrapper.vm.loading).toBe(true)
  })

  it('loads user data from auth store', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      phone: '+966501234567',
      bio: 'Test bio',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    expect(wrapper.vm.formData.full_name).toBe('Test User')
    expect(wrapper.vm.formData.email).toBe('test@example.com')
    expect(wrapper.vm.formData.phone).toBe('+966501234567')
    expect(wrapper.vm.formData.bio).toBe('Test bio')
  })

  it('toggles edit mode', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    expect(wrapper.vm.isEditing).toBe(false)

    wrapper.vm.startEdit()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isEditing).toBe(true)
  })

  /**
   * Property Test: Profile update validates full name
   * Validates: Requirements 7.6.2
   */
  it('validates full name field', async () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    // Test empty name
    wrapper.vm.formData.full_name = ''
    wrapper.vm.validateField('full_name')
    expect(wrapper.vm.fieldErrors.full_name).toContain('مطلوب')

    // Test valid name
    wrapper.vm.formData.full_name = 'Valid Name'
    wrapper.vm.validateField('full_name')
    expect(wrapper.vm.fieldErrors.full_name).toBe('')

    // Test name too long
    wrapper.vm.formData.full_name = 'a'.repeat(256)
    wrapper.vm.validateField('full_name')
    expect(wrapper.vm.fieldErrors.full_name).toContain('255')
  })

  /**
   * Property Test: Profile update validates phone field
   * Validates: Requirements 7.6.2
   */
  it('validates phone field format', async () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    // Test valid phone
    wrapper.vm.formData.phone = '+966501234567'
    wrapper.vm.validateField('phone')
    expect(wrapper.vm.fieldErrors.phone).toBe('')

    // Test valid phone with spaces
    wrapper.vm.formData.phone = '+966 50 123 4567'
    wrapper.vm.validateField('phone')
    expect(wrapper.vm.fieldErrors.phone).toBe('')

    // Test invalid phone
    wrapper.vm.formData.phone = 'invalid@phone'
    wrapper.vm.validateField('phone')
    expect(wrapper.vm.fieldErrors.phone).toContain('غير صحيح')

    // Test empty phone (should be valid)
    wrapper.vm.formData.phone = ''
    wrapper.vm.validateField('phone')
    expect(wrapper.vm.fieldErrors.phone).toBe('')
  })

  /**
   * Property Test: Profile update validates bio field
   * Validates: Requirements 7.6.2
   */
  it('validates bio field length', async () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    // Test valid bio
    wrapper.vm.formData.bio = 'This is a valid bio'
    wrapper.vm.validateField('bio')
    expect(wrapper.vm.fieldErrors.bio).toBe('')

    // Test bio too long
    wrapper.vm.formData.bio = 'a'.repeat(1001)
    wrapper.vm.validateField('bio')
    expect(wrapper.vm.fieldErrors.bio).toContain('1000')

    // Test empty bio (should be valid)
    wrapper.vm.formData.bio = ''
    wrapper.vm.validateField('bio')
    expect(wrapper.vm.fieldErrors.bio).toBe('')
  })

  /**
   * Property Test: Form is valid only when all fields pass validation
   * Validates: Requirements 7.6.2
   */
  it('determines form validity correctly', async () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    // Invalid: empty name
    wrapper.vm.formData.full_name = ''
    expect(wrapper.vm.isFormValid).toBe(false)

    // Valid: name only
    wrapper.vm.formData.full_name = 'Valid Name'
    expect(wrapper.vm.isFormValid).toBe(true)

    // Valid: name + phone
    wrapper.vm.formData.phone = '+966501234567'
    expect(wrapper.vm.isFormValid).toBe(true)

    // Valid: name + bio
    wrapper.vm.formData.phone = ''
    wrapper.vm.formData.bio = 'Valid bio'
    expect(wrapper.vm.isFormValid).toBe(true)

    // Invalid: name too long
    wrapper.vm.formData.full_name = 'a'.repeat(256)
    expect(wrapper.vm.isFormValid).toBe(false)

    // Invalid: bio too long
    wrapper.vm.formData.full_name = 'Valid Name'
    wrapper.vm.formData.bio = 'a'.repeat(1001)
    expect(wrapper.vm.isFormValid).toBe(false)
  })

  /**
   * Property Test: Save profile updates auth store and shows success message
   * Validates: Requirements 7.6.2
   */
  it('saves profile changes successfully', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      phone: '',
      bio: '',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Updated Name',
        phone: '+966501234567',
        bio: 'Updated bio',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.startEdit()
    wrapper.vm.formData.full_name = 'Updated Name'
    wrapper.vm.formData.phone = '+966501234567'
    wrapper.vm.formData.bio = 'Updated bio'

    await wrapper.vm.saveProfile()
    await flushPromises()

    expect(vi.mocked(apiClient.put)).toHaveBeenCalledWith('/users/me', {
      full_name: 'Updated Name',
      phone: '+966501234567',
      bio: 'Updated bio',
    })

    expect(wrapper.vm.isEditing).toBe(false)
    expect(wrapper.vm.profileSuccess).toContain('بنجاح')
    expect(authStore.user?.full_name).toBe('Updated Name')
  })

  /**
   * Property Test: Cancel edit restores original data
   * Validates: Requirements 7.6.2
   */
  it('cancels edit and restores original data', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      phone: '+966501234567',
      bio: 'Original bio',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.startEdit()
    wrapper.vm.formData.full_name = 'Modified Name'
    wrapper.vm.formData.phone = '+966509876543'
    wrapper.vm.formData.bio = 'Modified bio'

    await wrapper.vm.$nextTick()

    wrapper.vm.cancelEdit()

    expect(wrapper.vm.formData.full_name).toBe('Test User')
    expect(wrapper.vm.formData.phone).toBe('+966501234567')
    expect(wrapper.vm.formData.bio).toBe('Original bio')
    expect(wrapper.vm.isEditing).toBe(false)
  })

  /**
   * Property Test: Save profile shows error on API failure
   * Validates: Requirements 7.6.2
   */
  it('shows error message on save failure', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockRejectedValue({
      response: {
        data: {
          detail: 'Email already in use',
        },
      },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.startEdit()
    wrapper.vm.formData.full_name = 'Updated Name'

    await wrapper.vm.saveProfile()
    await flushPromises()

    expect(wrapper.vm.profileError).toContain('Email already in use')
    expect(wrapper.vm.isEditing).toBe(true)
  })

  /**
   * Property Test: Loading state during save
   * Validates: Requirements 7.6.2
   */
  it('shows loading state during save', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    let resolveUpdate: any
    const updatePromise = new Promise((resolve) => {
      resolveUpdate = resolve
    })

    vi.mocked(apiClient.put).mockReturnValue(updatePromise)

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.startEdit()
    wrapper.vm.formData.full_name = 'Updated Name'

    const savePromise = wrapper.vm.saveProfile()

    expect(wrapper.vm.savingProfile).toBe(true)

    resolveUpdate({
      data: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Updated Name',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    })

    await savePromise
    await flushPromises()

    expect(wrapper.vm.savingProfile).toBe(false)
  })

  it('validates password confirmation', async () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    wrapper.vm.passwordData.newPassword = 'newpassword123'
    wrapper.vm.passwordData.confirmPassword = 'differentpassword'

    await wrapper.vm.changePassword()

    expect(wrapper.vm.error).toContain('غير متطابقة')
  })

  it('validates password length', async () => {
    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    wrapper.vm.passwordData.newPassword = 'short'
    wrapper.vm.passwordData.confirmPassword = 'short'

    await wrapper.vm.changePassword()

    expect(wrapper.vm.error).toContain('8 أحرف')
  })

  it('displays member since date', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-15T00:00:00Z',
      updated_at: '2024-01-15T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    expect(wrapper.vm.memberSinceText).toBeTruthy()
  })
})


describe('ProfilePage.vue - Settings Management', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  /**
   * Property Test: Load preferences on page load
   * Validates: Requirements 7.6.3
   */
  it('loads preferences on page load', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    authStore.preferences = {
      theme: 'dark',
      language: 'en',
      notificationsEnabled: true,
      emailNotifications: true,
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    expect(wrapper.vm.preferences.emailNotifications).toBe(true)
    expect(wrapper.vm.preferences.darkMode).toBe(true)
  })

  /**
   * Property Test: Save email notification preferences
   * Validates: Requirements 7.6.3
   */
  it('saves email notification preferences', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: { success: true },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.emailNotifications = false
    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(vi.mocked(apiClient.put)).toHaveBeenCalledWith(
      '/users/me/preferences',
      expect.objectContaining({
        email_notifications: false,
      })
    )

    expect(wrapper.vm.preferencesSuccess).toContain('بنجاح')
  })

  /**
   * Property Test: Save push notification preferences
   * Validates: Requirements 7.6.3
   */
  it('saves push notification preferences', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: { success: true },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.pushNotifications = false
    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(vi.mocked(apiClient.put)).toHaveBeenCalledWith(
      '/users/me/preferences',
      expect.objectContaining({
        push_notifications: false,
      })
    )
  })

  /**
   * Property Test: Save weekly digest preferences
   * Validates: Requirements 7.6.3
   */
  it('saves weekly digest preferences', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: { success: true },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.weeklyDigest = false
    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(vi.mocked(apiClient.put)).toHaveBeenCalledWith(
      '/users/me/preferences',
      expect.objectContaining({
        weekly_digest: false,
      })
    )
  })

  /**
   * Property Test: Save dark mode preferences
   * Validates: Requirements 7.6.3
   */
  it('saves dark mode preferences', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: { success: true },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.darkMode = true
    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(vi.mocked(apiClient.put)).toHaveBeenCalledWith(
      '/users/me/preferences',
      expect.objectContaining({
        dark_mode: true,
      })
    )
  })

  /**
   * Property Test: Show loading state during preferences save
   * Validates: Requirements 7.6.3
   */
  it('shows loading state during preferences save', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    let resolvePreferences: any
    const preferencesPromise = new Promise((resolve) => {
      resolvePreferences = resolve
    })

    vi.mocked(apiClient.put).mockReturnValue(preferencesPromise)

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.emailNotifications = false

    const savePromise = wrapper.vm.savePreferences()

    expect(wrapper.vm.savingPreferences).toBe(true)

    resolvePreferences({
      data: { success: true },
    })

    await savePromise
    await flushPromises()

    expect(wrapper.vm.savingPreferences).toBe(false)
  })

  /**
   * Property Test: Show success message after saving preferences
   * Validates: Requirements 7.6.3
   */
  it('shows success message after saving preferences', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: { success: true },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    expect(wrapper.vm.preferencesSuccess).toBe('')

    wrapper.vm.preferences.emailNotifications = false
    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(wrapper.vm.preferencesSuccess).toContain('بنجاح')
  })

  /**
   * Property Test: Show error message on preferences save failure
   * Validates: Requirements 7.6.3
   */
  it('shows error message on preferences save failure', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockRejectedValue({
      response: {
        status: 500,
        data: {
          detail: 'Server error',
        },
      },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.emailNotifications = false
    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(wrapper.vm.preferencesError).toContain('Server error')
  })

  /**
   * Property Test: Handle missing backend endpoint gracefully
   * Validates: Requirements 7.6.3
   */
  it('handles missing backend endpoint gracefully', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockRejectedValue({
      response: {
        status: 404,
        data: {
          detail: 'Not found',
        },
      },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.emailNotifications = false
    await wrapper.vm.savePreferences()
    await flushPromises()

    // Should not show error for 404 (endpoint doesn't exist)
    expect(wrapper.vm.preferencesError).toBe('')
    expect(wrapper.vm.preferencesSuccess).toContain('بنجاح')
  })

  /**
   * Property Test: Save all preferences together
   * Validates: Requirements 7.6.3
   */
  it('saves all preferences together', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: { success: true },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.emailNotifications = false
    wrapper.vm.preferences.pushNotifications = true
    wrapper.vm.preferences.weeklyDigest = false
    wrapper.vm.preferences.darkMode = true

    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(vi.mocked(apiClient.put)).toHaveBeenCalledWith(
      '/users/me/preferences',
      {
        email_notifications: false,
        push_notifications: true,
        weekly_digest: false,
        dark_mode: true,
      }
    )
  })

  /**
   * Property Test: Clear success message after timeout
   * Validates: Requirements 7.6.3
   */
  it('clears success message after timeout', async () => {
    vi.useFakeTimers()

    const authStore = useAuthStore()
    authStore.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { total: 0, items: [] },
    })

    vi.mocked(apiClient.put).mockResolvedValue({
      data: { success: true },
    })

    const wrapper = mount(ProfilePage, {
      global: {
        stubs: {
          FormInput: true,
          FormCheckbox: true,
          FormButton: true,
          StatsCard: true,
        },
      },
    })

    await flushPromises()

    wrapper.vm.preferences.emailNotifications = false
    await wrapper.vm.savePreferences()
    await flushPromises()

    expect(wrapper.vm.preferencesSuccess).toContain('بنجاح')

    vi.advanceTimersByTime(3000)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.preferencesSuccess).toBe('')

    vi.useRealTimers()
  })
})
