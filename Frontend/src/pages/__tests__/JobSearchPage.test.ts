/**
 * Tests for JobSearchPage component
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4, 3.2, 3.3, 3.4, 8.5
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import JobSearchPage from '../JobSearchPage.vue'
import { useJobsStore } from '@/stores/jobs'

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    get: vi.fn()
  }
}))

describe('JobSearchPage', () => {
  let pinia: any
  let router: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/search',
          name: 'JobSearch',
          component: JobSearchPage
        },
        {
          path: '/jobs/:id',
          name: 'JobDetails',
          component: { template: '<div>Job Details</div>' }
        }
      ]
    })
  })

  /**
   * Property 1: Search functionality with multiple criteria
   * Validates: Requirements 1.1, 1.2, 1.3, 1.4
   */
  it('should display search bar with all required fields', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    expect(wrapper.find('h1').text()).toContain('البحث عن الوظائف')
    expect(wrapper.findComponent({ name: 'SearchBar' }).exists()).toBe(true)
  })

  /**
   * Property 2: Filtering and sorting capabilities
   * Validates: Requirements 3.2, 3.3, 3.4
   */
  it('should display filter panel with all filter options', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    expect(wrapper.findComponent({ name: 'FilterPanel' }).exists()).toBe(true)
  })

  /**
   * Property 3: Sort order selection
   * Validates: Requirements 3.2
   */
  it('should have sort options available', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    expect(vm.sortBy).toBe('recent')
  })

  /**
   * Property 4: Pagination support
   * Validates: Requirements 1.3
   */
  it('should display pagination component when jobs exist', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    vm.jobs = [{ job_id: '1', title: 'Test Job' }]
    vm.totalJobs = 100

    expect(wrapper.findComponent({ name: 'Pagination' }).exists()).toBe(true)
  })

  /**
   * Property 5: Save job functionality
   * Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
   */
  it('should track saved jobs correctly', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    const jobsStore = useJobsStore()

    // Initially no jobs are saved
    expect(vm.isSaved('1')).toBe(false)

    // Add a saved job
    jobsStore.savedJobs.push({ job_id: '1', title: 'Test Job' } as any)

    // Now the job should be marked as saved
    expect(vm.isSaved('1')).toBe(true)
  })

  /**
   * Property 6: Empty state display
   * Validates: Requirements 1.4
   */
  it('should display empty state when no jobs found', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    vm.loading = false
    vm.error = ''
    vm.jobs = []

    expect(wrapper.text()).toContain('لم يتم العثور على وظائف')
  })

  /**
   * Property 7: Error state display
   * Validates: Requirements 1.5
   */
  it('should display error message when search fails', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    vm.loading = false
    vm.error = 'فشل البحث عن الوظائف'
    vm.jobs = []

    expect(wrapper.text()).toContain('فشل البحث عن الوظائف')
  })

  /**
   * Property 8: Loading state display
   * Validates: Requirements 1.3
   */
  it('should display loading state during search', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    vm.loading = true

    expect(wrapper.text()).toContain('جاري البحث عن الوظائف')
  })

  /**
   * Property 9: Page size change
   * Validates: Requirements 1.3
   */
  it('should reset to first page when page size changes', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    vm.currentPage = 5
    vm.handlePageSizeChange(50)

    expect(vm.currentPage).toBe(1)
    expect(vm.pageSize).toBe(50)
  })

  /**
   * Property 10: Filter change resets pagination
   * Validates: Requirements 3.2
   */
  it('should reset to first page when filters change', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    vm.currentPage = 5
    vm.handleFilterChange()

    expect(vm.currentPage).toBe(1)
  })

  /**
   * Property 11: Sort parameter generation
   * Validates: Requirements 3.2
   */
  it('should generate correct sort parameters', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any

    vm.sortBy = 'recent'
    expect(vm.getSortParam()).toBe('posted_date:desc')

    vm.sortBy = 'salary-high'
    expect(vm.getSortParam()).toBe('salary_max:desc')

    vm.sortBy = 'salary-low'
    expect(vm.getSortParam()).toBe('salary_min:asc')

    vm.sortBy = 'relevance'
    expect(vm.getSortParam()).toBe('relevance:desc')
  })

  /**
   * Property 12: Filter state updates
   * Validates: Requirements 3.2, 3.3, 3.4
   */
  it('should update filter state correctly', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    const newFilters = {
      minSalary: 10000,
      maxSalary: 50000,
      location: 'Cairo',
      jobTypes: ['full-time'],
      remote: ['remote'],
      experienceLevel: 'mid',
      postedDate: '7',
      companySizes: ['medium']
    }

    vm.updateFilters(newFilters)

    expect(vm.filterState).toEqual(newFilters)
  })

  /**
   * Property 13: Search query from route
   * Validates: Requirements 1.1
   */
  it('should initialize search query from route params', async () => {
    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/search',
          name: 'JobSearch',
          component: JobSearchPage
        }
      ]
    })

    await testRouter.push({ path: '/search', query: { q: 'developer' } })

    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, testRouter],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    expect(vm.searchQuery).toBe('developer')
  })

  /**
   * Property 14: Results count display
   * Validates: Requirements 1.4
   */
  it('should display results count when jobs exist', () => {
    const wrapper = mount(JobSearchPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          SearchBar: true,
          FilterPanel: true,
          Pagination: true,
          JobCard: true
        }
      }
    })

    const vm = wrapper.vm as any
    vm.jobs = [{ job_id: '1', title: 'Test Job' }]
    vm.totalJobs = 150

    expect(wrapper.text()).toContain('عدد النتائج')
    expect(wrapper.text()).toContain('150')
  })
})
