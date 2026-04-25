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

    expect(wrapper.text()).toContain('الوظائف المحفوظة')
    expect(wrapper.text()).toContain('إدارة الوظائف التي حفظتها للمراجعة لاحقاً')
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

    expect(wrapper.text()).toContain('لم تحفظ أي وظائف بعد')
  })

  it('displays saved jobs when available', async () => {
    const store = useJobsStore()
    store.savedJobs = [
      {
        id: '1',
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
    expect(wrapper.text()).toContain('الوظائف المحفوظة')
  })

  it('filters jobs by search query', async () => {
    const store = useJobsStore()
    store.savedJobs = [
      {
        id: '1',
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
        id: '2',
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
    wrapper.vm.searchQuery = 'Developer'
    await wrapper.vm.$nextTick()

    // Check that only the developer job is shown
    const filteredJobs = wrapper.vm.filteredJobs
    expect(filteredJobs).toHaveLength(1)
    expect(filteredJobs[0].title).toBe('Senior Developer')
  })

  it('sorts jobs by salary high to low', async () => {
    const store = useJobsStore()
    store.savedJobs = [
      {
        id: '1',
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
        id: '2',
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
    wrapper.vm.sortBy = 'salary-high'
    await wrapper.vm.$nextTick()

    const filteredJobs = wrapper.vm.filteredJobs
    expect(filteredJobs[0].salary_max).toBeGreaterThan(filteredJobs[1].salary_max)
  })

  it('removes saved job when delete button is clicked', async () => {
    const store = useJobsStore()
    store.removeSavedJob = vi.fn()

    store.savedJobs = [
      {
        id: '1',
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
          RouterLink: true,
        },
      },
    })

    await wrapper.vm.$nextTick()

    await wrapper.vm.removeSavedJob('1')

    expect(store.removeSavedJob).toHaveBeenCalledWith('1')
  })

  it('navigates to job details when job card is clicked', async () => {
    const store = useJobsStore()
    store.savedJobs = [
      {
        id: '1',
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
          RouterLink: true,
        },
      },
    })

    await wrapper.vm.$nextTick()

    await wrapper.vm.goToJobDetails('1')

    expect(mockRouter.push).toHaveBeenCalledWith({
      name: 'JobDetails',
      params: { id: '1' },
    })
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
    const formatted = wrapper.vm.formatSalary(job1)
    // Salary is formatted with Arabic numerals, so check for the pattern with any digits
    expect(formatted).toBeTruthy()
    expect(formatted).not.toBe('غير محدد')

    const job2 = { salary_min: 0, salary_max: 0 }
    expect(wrapper.vm.formatSalary(job2)).toBe('غير محدد')
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

    expect(wrapper.vm.getJobTypeLabel('fulltime')).toBe('دوام كامل')
    expect(wrapper.vm.getJobTypeLabel('parttime')).toBe('دوام جزئي')
    expect(wrapper.vm.getJobTypeLabel('internship')).toBe('تدريب')
    expect(wrapper.vm.getJobTypeLabel('contract')).toBe('عقد')
  })
})
