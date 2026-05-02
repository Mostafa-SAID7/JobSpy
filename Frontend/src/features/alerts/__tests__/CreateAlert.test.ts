import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AlertsPage from '../AlertsPage.vue'
import { createPinia, setActivePinia } from 'pinia'
import { useJobsStore } from '@/features/jobs/stores/jobs'

/**
 * Test suite for Create New Alert functionality
 * Validates: Requirements 6.1 (Create alerts with criteria)
 */
describe('Create New Alert Modal', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Modal opening and closing', () => {
    it('should open create alert modal when "New Alert" button is clicked', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: false,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      expect((wrapper.vm as any).showModal).toBe(false)

      await (wrapper.vm as any).openCreateModal()
      await wrapper.vm.$nextTick()

      expect((wrapper.vm as any).showModal).toBe(true)
      expect((wrapper.vm as any).editingAlert).toBe(null)
    })

    it('should reset form data when opening create modal', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Old Alert',
        query: 'Old Query',
        frequency: 'weekly',
        notification_method: 'in_app',
      }

      await (wrapper.vm as any).openCreateModal()

      expect((wrapper.vm as any).formData.name).toBe('')
      expect((wrapper.vm as any).formData.query).toBe('')
      expect((wrapper.vm as any).formData.frequency).toBe('daily')
      expect((wrapper.vm as any).formData.notification_method).toBe('email')
    })

    it('should reset form data when opening create modal', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Old Alert',
        query: 'Old Query',
        frequency: 'weekly',
        notification_method: 'in_app',
      }

      await (wrapper.vm as any).openCreateModal()

      expect((wrapper.vm as any).formData.name).toBe('')
      expect((wrapper.vm as any).formData.query).toBe('')
      expect((wrapper.vm as any).formData.frequency).toBe('daily')
      expect((wrapper.vm as any).formData.notification_method).toBe('email')
    })

    it('should close modal when close button is clicked', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).showModal = true
      await wrapper.vm.$nextTick()

      await (wrapper.vm as any).closeModal()

      expect((wrapper.vm as any).showModal).toBe(false)
    })

    it('should clear form errors when closing modal', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formError = 'Some error'
      ;(wrapper.vm as any).fieldErrors.name = 'Name is required'

      await (wrapper.vm as any).closeModal()

      expect((wrapper.vm as any).formError).toBe('')
      expect((wrapper.vm as any).fieldErrors.name).toBe('')
    })
  })

  describe('Form validation', () => {
    it('should validate alert name is required', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.name = ''
      ;(wrapper.vm as any).validateField('name')

      expect((wrapper.vm as any).fieldErrors.name).toBe('Alert name is required')
    })

    it('should validate alert name max length', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.name = 'a'.repeat(256)
      ;(wrapper.vm as any).validateField('name')

      expect((wrapper.vm as any).fieldErrors.name).toBe('Alert name must be less than 255 characters')
    })

    it('should validate search query is required', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.query = ''
      ;(wrapper.vm as any).validateField('query')

      expect((wrapper.vm as any).fieldErrors.query).toBe('Search query is required')
    })

    it('should validate search query max length', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.query = 'a'.repeat(256)
      ;(wrapper.vm as any).validateField('query')

      expect((wrapper.vm as any).fieldErrors.query).toBe('Search query must be less than 255 characters')
    })

    it('should clear error when valid name is entered', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.name = 'Valid Alert Name'
      ;(wrapper.vm as any).validateField('name')

      expect((wrapper.vm as any).fieldErrors.name).toBe('')
    })

    it('should determine form is valid when all required fields are filled', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Test Alert',
        query: 'Test Query',
        frequency: 'daily',
        notification_method: 'email',
      }

      // Validate all fields
      ;(wrapper.vm as any).validateField('name')
      ;(wrapper.vm as any).validateField('query')
      
      expect((wrapper.vm as any).isFormValid).toBe(true)
    })

    it('should determine form is invalid when name is empty', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: '',
        query: 'Test Query',
        frequency: 'daily',
        notification_method: 'email',
      }

      expect((wrapper.vm as any).isFormValid).toBe(false)
    })

    it('should determine form is invalid when query is empty', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Test Alert',
        query: '',
        frequency: 'daily',
        notification_method: 'email',
      }

      expect((wrapper.vm as any).isFormValid).toBe(false)
    })
  })

  describe('Create alert submission', () => {
    it('should create alert with valid form data', async () => {
      const store = useJobsStore()
      const createAlertSpy = vi.spyOn(store, 'createAlert').mockResolvedValue({
        id: '1',
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      })

      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      }

      await (wrapper.vm as any).handleSubmit()

      expect(createAlertSpy).toHaveBeenCalledWith({
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      })
    })

    it('should show success message after creating alert', async () => {
      const store = useJobsStore()
      vi.spyOn(store, 'createAlert').mockResolvedValue({
        id: '1',
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      })

      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      }

      await (wrapper.vm as any).handleSubmit()

      expect((wrapper.vm as any).formSuccess).toBe('Alert created successfully')
    })

    it('should close modal after successful creation', async () => {
      const store = useJobsStore()
      vi.spyOn(store, 'createAlert').mockResolvedValue({
        id: '1',
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      })

      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).showModal = true
      ;(wrapper.vm as any).formData = {
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      }

      await (wrapper.vm as any).handleSubmit()
      // Wait for the setTimeout to close the modal
      await new Promise((resolve) => setTimeout(resolve, 1100))

      expect((wrapper.vm as any).showModal).toBe(false)
    })

    it('should show error message when creation fails', async () => {
      const store = useJobsStore()
      vi.spyOn(store, 'createAlert').mockRejectedValue({
        response: {
          data: {
            detail: 'Alert name already exists',
          },
        },
      })

      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      }

      await (wrapper.vm as any).handleSubmit()

      expect((wrapper.vm as any).formError).toBe('Alert name already exists')
    })

    it('should prevent submission when form is invalid', async () => {
      const store = useJobsStore()
      const createAlertSpy = vi.spyOn(store, 'createAlert')

      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: '',
        query: '',
        frequency: 'daily',
        notification_method: 'email',
      }

      await (wrapper.vm as any).handleSubmit()

      expect(createAlertSpy).not.toHaveBeenCalled()
      expect((wrapper.vm as any).formError).toBe('Please fix the errors in the form')
    })

    it('should set loading state during submission', async () => {
      const store = useJobsStore()
      vi.spyOn(store, 'createAlert').mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve({}), 100)
          })
      )

      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData = {
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      }

      const submitPromise = (wrapper.vm as any).handleSubmit()
      expect((wrapper.vm as any).isSubmitting).toBe(true)

      await submitPromise
      expect((wrapper.vm as any).isSubmitting).toBe(false)
    })
  })

  describe('Alert frequency options', () => {
    it('should have hourly frequency option', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      const hourlyOption = (wrapper.vm as any).frequencyOptions.find((o: any) => o.value === 'hourly')
      expect(hourlyOption).toBeDefined()
      expect(hourlyOption?.label).toBe('Hourly')
    })

    it('should have daily frequency option', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      const dailyOption = (wrapper.vm as any).frequencyOptions.find((o: any) => o.value === 'daily')
      expect(dailyOption).toBeDefined()
      expect(dailyOption?.label).toBe('Daily')
    })

    it('should have weekly frequency option', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      const weeklyOption = (wrapper.vm as any).frequencyOptions.find((o: any) => o.value === 'weekly')
      expect(weeklyOption).toBeDefined()
      expect(weeklyOption?.label).toBe('Weekly')
    })

    it('should default to daily frequency', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      await (wrapper.vm as any).openCreateModal()

      expect((wrapper.vm as any).formData.frequency).toBe('daily')
    })
  })

  describe('Notification method options', () => {
    it('should have email notification option', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      const emailOption = (wrapper.vm as any).notificationOptions.find((o: any) => o.value === 'email')
      expect(emailOption).toBeDefined()
      expect(emailOption?.label).toBe('Email')
    })

    it('should have in-app notification option', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      const inAppOption = (wrapper.vm as any).notificationOptions.find((o: any) => o.value === 'in_app')
      expect(inAppOption).toBeDefined()
      expect(inAppOption?.label).toBe('In-App Notification')
    })

    it('should default to email notification', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      await (wrapper.vm as any).openCreateModal()

      expect((wrapper.vm as any).formData.notification_method).toBe('email')
    })
  })

  describe('Alert criteria setting', () => {
    it('should allow setting alert name', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.name = 'Python Developer in Cairo'

      expect((wrapper.vm as any).formData.name).toBe('Python Developer in Cairo')
    })

    it('should allow setting search query', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.query = 'Python Developer'

      expect((wrapper.vm as any).formData.query).toBe('Python Developer')
    })

    it('should allow setting alert frequency', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.frequency = 'weekly'

      expect((wrapper.vm as any).formData.frequency).toBe('weekly')
    })

    it('should allow setting notification method', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formData.notification_method = 'in_app'

      expect((wrapper.vm as any).formData.notification_method).toBe('in_app')
    })
  })

  describe('Success and error message handling', () => {
    it('should clear success message when opening new modal', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formSuccess = 'Alert created successfully'

      await (wrapper.vm as any).openCreateModal()

      expect((wrapper.vm as any).formSuccess).toBe('')
    })

    it('should clear error message when opening new modal', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formError = 'Some error occurred'

      await (wrapper.vm as any).openCreateModal()

      expect((wrapper.vm as any).formError).toBe('')
    })

    it('should clear messages when closing modal', async () => {
      const wrapper = mount(AlertsPage, {
        global: {
          stubs: {
            FormButton: true,
            AlertCard: true,
            StatsCard: true,
            FormInput: true,
            FormSelect: true,
          },
        },
      })

      ;(wrapper.vm as any).formSuccess = 'Success'
      ;(wrapper.vm as any).formError = 'Error'

      await (wrapper.vm as any).closeModal()

      expect((wrapper.vm as any).formSuccess).toBe('')
      expect((wrapper.vm as any).formError).toBe('')
    })
  })
})
