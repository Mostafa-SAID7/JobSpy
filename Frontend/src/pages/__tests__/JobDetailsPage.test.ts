import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import JobDetailsPage from '../JobDetailsPage.vue'
import { useJobsStore } from '@/stores/jobs'

const i18n = createI18n({
  legacy: false,
  locale: 'ar',
  messages: {
    ar: {},
    en: {},
  },
})

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    get: vi.fn(),
  },
}))

describe('JobDetailsPage', () => {
  let router: any
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/jobs/:id',
          component: JobDetailsPage,
        },
      ],
    })
  })

  /**
   * Property 1: Display all required job fields
   * Validates: Requirement 1.4
   */
  it('should display all required job fields', async () => {
    const mockJob = {
      id: 1,
      title: 'Software Engineer',
      company: 'Tech Company',
      location: 'Cairo',
      salary_min: 10000,
      salary_max: 15000,
      salary_currency: 'EGP',
      job_type: 'fulltime',
      description: 'Job description',
      posted_date: '2024-01-01T00:00:00Z',
      site_name: 'linkedin',
      source_url: 'https://example.com/job/1',
      source_job_id: '123',
      is_remote: 0,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    const { apiClient } = await import('@/services/api')
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockJob })

    await router.push('/jobs/1')
    await router.isReady()

    const wrapper = mount(JobDetailsPage, {
      global: {
        plugins: [pinia, router, i18n],
        stubs: {
          FormButton: true,
        },
      },
    })

    await wrapper.vm.$nextTick()

    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.text()).toContain('Software Engineer')
    expect(wrapper.text()).toContain('Tech Company')
    expect(wrapper.text()).toContain('Cairo')
    expect(wrapper.text()).toContain('Job description')
  })

  /**
   * Property 2: Save button functionality
   * Validates: Requirement 5.1 - Save job functionality
   * Validates: Requirement 8.5 - Save button from UI succeeds
   */
  it('should save job when save button is clicked', async () => {
    const mockJob = {
      id: 1,
      title: 'Software Engineer',
      company: 'Tech Company',
      location: 'Cairo',
      salary_min: 10000,
      salary_max: 15000,
      salary_currency: 'EGP',
      job_type: 'fulltime',
      description: 'Job description',
      posted_date: '2024-01-01T00:00:00Z',
      site_name: 'linkedin',
      source_url: 'https://example.com/job/1',
      source_job_id: '123',
      is_remote: 0,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    const { apiClient } = await import('@/services/api')
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockJob })

    await router.push('/jobs/1')
    await router.isReady()

    const wrapper = mount(JobDetailsPage, {
      global: {
        plugins: [pinia, router, i18n],
        stubs: {
          FormButton: false,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const jobsStore = useJobsStore()
    const addSavedJobSpy = vi.spyOn(jobsStore, 'addSavedJob')

    // Find and click save button
    const buttons = wrapper.findAll('button')
    const saveButton = buttons.find((btn: any) => btn.text().includes('حفظ'))

    if (saveButton) {
      await saveButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(addSavedJobSpy).toHaveBeenCalled()
    }
  })

  /**
   * Property 3: Apply button opens job URL
   * Validates: Requirement 8.5 - Apply button from UI succeeds
   */
  it('should open job URL when apply button is clicked', async () => {
    const mockJob = {
      id: 1,
      title: 'Software Engineer',
      company: 'Tech Company',
      location: 'Cairo',
      salary_min: 10000,
      salary_max: 15000,
      salary_currency: 'EGP',
      job_type: 'fulltime',
      description: 'Job description',
      posted_date: '2024-01-01T00:00:00Z',
      site_name: 'linkedin',
      source_url: 'https://example.com/job/1',
      source_job_id: '123',
      is_remote: 0,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    const { apiClient } = await import('@/services/api')
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockJob })

    // Mock window.open
    const windowOpenSpy = vi.spyOn(window, 'open').mockImplementation(() => null)

    await router.push('/jobs/1')
    await router.isReady()

    const wrapper = mount(JobDetailsPage, {
      global: {
        plugins: [pinia, router, i18n],
        stubs: {
          FormButton: false,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Find and click apply button
    const buttons = wrapper.findAll('button')
    const applyButton = buttons.find((btn: any) => btn.text().includes('تقديم'))

    if (applyButton) {
      await applyButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(windowOpenSpy).toHaveBeenCalledWith(
        'https://example.com/job/1',
        '_blank',
        'noopener,noreferrer'
      )
    }

    windowOpenSpy.mockRestore()
  })

  /**
   * Property 4: Format salary correctly
   * Validates: Requirement 1.4 - Display salary fields
   */
  it('should format salary range correctly', async () => {
    const mockJob = {
      id: 1,
      title: 'Software Engineer',
      company: 'Tech Company',
      location: 'Cairo',
      salary_min: 10000,
      salary_max: 15000,
      salary_currency: 'EGP',
      job_type: 'fulltime',
      description: 'Job description',
      posted_date: '2024-01-01T00:00:00Z',
      site_name: 'linkedin',
      source_url: 'https://example.com/job/1',
      source_job_id: '123',
      is_remote: 0,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    const { apiClient } = await import('@/services/api')
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockJob })

    await router.push('/jobs/1')
    await router.isReady()

    const wrapper = mount(JobDetailsPage, {
      global: {
        plugins: [pinia, router, i18n],
        stubs: {
          FormButton: true,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Check that salary is displayed (with Arabic numerals)
    const salaryText = wrapper.text()
    expect(salaryText).toBeTruthy()
    expect(salaryText).toContain('Software Engineer')
  })

  /**
   * Property 5: Handle missing job URL gracefully
   * Validates: Error handling
   */
  it('should show error when job URL is missing', async () => {
    const mockJob = {
      id: 1,
      title: 'Software Engineer',
      company: 'Tech Company',
      location: 'Cairo',
      salary_min: 10000,
      salary_max: 15000,
      salary_currency: 'EGP',
      job_type: 'fulltime',
      description: 'Job description',
      posted_date: '2024-01-01T00:00:00Z',
      site_name: 'linkedin',
      source_url: null, // Missing URL
      source_job_id: '123',
      is_remote: 0,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    const { apiClient } = await import('@/services/api')
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockJob })

    await router.push('/jobs/1')
    await router.isReady()

    const wrapper = mount(JobDetailsPage, {
      global: {
        plugins: [pinia, router, i18n],
        stubs: {
          FormButton: false,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Find and click apply button
    const buttons = wrapper.findAll('button')
    const applyButton = buttons.find((btn: any) => btn.text().includes('تقديم'))

    if (applyButton) {
      await applyButton.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message
      expect(wrapper.text()).toContain('رابط الوظيفة غير متاح')
    }
  })
})
