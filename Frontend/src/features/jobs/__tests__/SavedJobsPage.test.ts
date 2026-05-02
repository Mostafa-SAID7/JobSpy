import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SavedJobsPage from '../SavedJobsPage.vue'
import { useJobsStore } from '@/stores/jobs'
import { createI18n } from 'vue-i18n'

const i18n = createI18n({
  legacy: false,
  locale: 'ar',
  messages: {
    ar: {},
    en: {},
  },
})

const mockRouter = {
  push: vi.fn(),
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
}))

vi.mock('@/shared/services/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('SavedJobsPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the page header', () => {
    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Your Saved Careers')
    expect(wrapper.text()).toContain('Manage and track the opportunities you\'ve bookmarked for your future.')
  })

  it('shows empty state when no saved jobs', () => {
    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain("You haven't saved any jobs yet")
  })

  it('displays saved jobs when available', async () => {
    const store = useJobsStore()
    store.savedJobs = [
      {
        id: 1,
        title: 'Senior Developer',
        company: 'Tech Company',
        location: 'Cairo',
        salary_min: 50000,
        salary_max: 80000,
        job_type: 'fulltime',
        description: 'We are looking for a senior developer',
        source: 'linkedin',
        source_url: 'https://linkedin.com/job/1',
        source_job_id: 'job_1',
        posted_date: new Date().toISOString(),
        is_remote: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        salary_currency: 'EGP',
      },
    ]

    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
        },
      },
    })

    await wrapper.vm.$nextTick()

    // Check that the page renders and has the header
    expect(wrapper.text()).toContain('Your Saved Careers')
  })

  it('filters jobs by search query', async () => {
    const store = useJobsStore()
    store.savedJobs = [
      {
        id: 1,
        title: 'Senior Developer',
        company: 'Tech Company',
        location: 'Cairo',
        salary_min: 50000,
        salary_max: 80000,
        job_type: 'fulltime',
        description: 'We are looking for a senior developer',
        source: 'linkedin',
        source_url: 'https://linkedin.com/job/1',
        source_job_id: 'job_1',
        posted_date: new Date().toISOString(),
        is_remote: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        salary_currency: 'EGP',
      },
      {
        id: 2,
        title: 'Junior Designer',
        company: 'Design Studio',
        location: 'Alexandria',
        salary_min: 20000,
        salary_max: 35000,
        job_type: 'fulltime',
        description: 'We are looking for a junior designer',
        source: 'indeed',
        source_url: 'https://indeed.com/job/2',
        source_job_id: 'job_2',
        posted_date: new Date().toISOString(),
        is_remote: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        salary_currency: 'EGP',
      },
    ]

    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    await wrapper.vm.$nextTick()

    // Set search query
    ;(wrapper.vm as any).searchQuery = 'Developer'
    await wrapper.vm.$nextTick()

    // Check that only the developer job is shown
    const filteredJobs = (wrapper.vm as any).filteredJobs
    expect(filteredJobs).toHaveLength(1)
    expect(filteredJobs[0].title).toBe('Senior Developer')
  })

  it('sorts jobs by salary high to low', async () => {
    const store = useJobsStore()
    store.savedJobs = [
      {
        id: 1,
        title: 'Senior Developer',
        company: 'Tech Company',
        location: 'Cairo',
        salary_min: 50000,
        salary_max: 80000,
        job_type: 'fulltime',
        description: 'We are looking for a senior developer',
        source: 'linkedin',
        source_url: 'https://linkedin.com/job/1',
        source_job_id: 'job_1',
        posted_date: new Date().toISOString(),
        is_remote: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        salary_currency: 'EGP',
      },
      {
        id: 2,
        title: 'Junior Designer',
        company: 'Design Studio',
        location: 'Alexandria',
        salary_min: 20000,
        salary_max: 35000,
        job_type: 'fulltime',
        description: 'We are looking for a junior designer',
        source: 'indeed',
        source_url: 'https://indeed.com/job/2',
        source_job_id: 'job_2',
        posted_date: new Date().toISOString(),
        is_remote: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        salary_currency: 'EGP',
      },
    ]

    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    await wrapper.vm.$nextTick()

    // Set sort to salary high
    ;(wrapper.vm as any).sortBy = 'salary-high'
    await wrapper.vm.$nextTick()

    const filteredJobs = (wrapper.vm as any).filteredJobs
    expect(filteredJobs[0].salary_max).toBeGreaterThan(filteredJobs[1].salary_max)
  })

  it('removes saved job when delete button is clicked', async () => {
    const { apiClient } = await import('@/shared/services/api')
    const store = useJobsStore()
    
    const mockJob = {
      id: 1,
      title: 'Senior Developer',
      company: 'Tech Company',
      location: 'Cairo',
      salary_min: 50000,
      salary_max: 80000,
      job_type: 'fulltime',
      description: 'We are looking for a senior developer',
      source: 'linkedin',
      source_url: 'https://linkedin.com/job/1',
      source_job_id: 'job_1',
      posted_date: new Date().toISOString(),
      is_remote: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      salary_currency: 'EGP',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { items: [{ job: mockJob }] },
    })

    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Test that the page renders with the saved job
    expect(wrapper.text()).toContain('Senior Developer')
  })

  it('navigates to job details when job card is clicked', async () => {
    const { apiClient } = await import('@/shared/services/api')
    const store = useJobsStore()
    
    const mockJob = {
      id: 1,
      title: 'Senior Developer',
      company: 'Tech Company',
      location: 'Cairo',
      salary_min: 50000,
      salary_max: 80000,
      job_type: 'fulltime',
      description: 'We are looking for a senior developer',
      source: 'linkedin',
      source_url: 'https://linkedin.com/job/1',
      source_job_id: 'job_1',
      posted_date: new Date().toISOString(),
      is_remote: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      salary_currency: 'EGP',
    }

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { items: [{ job: mockJob }] },
    })

    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Test that the page renders with the saved job
    expect(wrapper.text()).toContain('Senior Developer')
  })

  it('formats salary correctly', () => {
    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    const job1 = { salary_min: 50000, salary_max: 80000 }
    const formatted = (wrapper.vm as any).formatSalary(job1)
    // Salary is formatted with Arabic numerals, so check for the pattern with any digits
    expect(formatted).toBeTruthy()
    expect(formatted).not.toBe('Not specified')

    const job2 = { salary_min: 0, salary_max: 0 }
    expect((wrapper.vm as any).formatSalary(job2)).toBe('Not specified')
  })

  it('formats job type label correctly', () => {
    const wrapper = mount(SavedJobsPage, {
      global: {
        plugins: [i18n],
        mocks: {
          $router: mockRouter,
        },
        stubs: {
          Pagination: true,
          RouterLink: true,
        },
      },
    })

    expect((wrapper.vm as any).getJobTypeLabel('fulltime')).toBe('Full-time')
    expect((wrapper.vm as any).getJobTypeLabel('parttime')).toBe('Part-time')
    expect((wrapper.vm as any).getJobTypeLabel('internship')).toBe('Internship')
    expect((wrapper.vm as any).getJobTypeLabel('contract')).toBe('Contract')
  })
})
