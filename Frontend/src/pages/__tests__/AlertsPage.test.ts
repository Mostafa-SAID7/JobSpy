import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AlertsPage from '../AlertsPage.vue'
import { createPinia, setActivePinia } from 'pinia'
import { useJobsStore } from '@/stores/jobs'

describe('AlertsPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Display list of user alerts', () => {
    it('should display loading state when fetching alerts', () => {
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

      expect(wrapper.find('.animate-spin').exists()).toBe(true)
      expect(wrapper.text()).toContain('Loading alerts...')
    })

    it('should display empty state when no alerts exist', async () => {
      const store = useJobsStore()
      store.alerts = []

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

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No alerts created yet')
      expect(wrapper.text()).toContain('Create alerts to receive notifications')
    })

    it('should display alerts list when alerts exist', async () => {
      const store = useJobsStore()
      store.alerts = [
        {
          id: '1',
          name: 'Python Developer',
          query: 'Python',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 5,
        },
        {
          id: '2',
          name: 'React Developer',
          query: 'React',
          frequency: 'weekly',
          notification_method: 'in_app',
          is_active: false,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
      ]

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

      await wrapper.vm.$nextTick()

      // Should display stats cards
      expect(wrapper.findComponent({ name: 'StatsCard' }).exists()).toBe(true)

      // Should display alert cards
      const alertCards = wrapper.findAllComponents({ name: 'AlertCard' })
      expect(alertCards).toHaveLength(2)
    })

    it('should display error message when fetch fails', async () => {
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

      // Simulate error
      wrapper.vm.error = 'Failed to load alerts'
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('خطأ')
      expect(wrapper.text()).toContain('Failed to load alerts')
    })
  })

  describe('Enable/disable toggle for alerts', () => {
    it('should toggle alert active status', async () => {
      const store = useJobsStore()
      store.alerts = [
        {
          id: '1',
          name: 'Test Alert',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
      ]

      const updateAlertSpy = vi.spyOn(store, 'updateAlert').mockResolvedValue({})

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

      await wrapper.vm.toggleAlert('1')

      expect(updateAlertSpy).toHaveBeenCalledWith('1', { is_active: false })
    })

    it('should show error when toggle fails', async () => {
      const store = useJobsStore()
      store.alerts = [
        {
          id: '1',
          name: 'Test Alert',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
      ]

      vi.spyOn(store, 'updateAlert').mockRejectedValue(
        new Error('Update failed')
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

      await wrapper.vm.toggleAlert('1')

      expect(wrapper.vm.error).toBe('Failed to update alert')
    })
  })

  describe('Delete alert functionality', () => {
    it('should delete alert with confirmation', async () => {
      const store = useJobsStore()
      store.alerts = [
        {
          id: '1',
          name: 'Test Alert',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
      ]

      const deleteAlertSpy = vi.spyOn(store, 'deleteAlert').mockResolvedValue({})
      vi.spyOn(window, 'confirm').mockReturnValue(true)

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

      await wrapper.vm.deleteAlert('1')

      expect(deleteAlertSpy).toHaveBeenCalledWith('1')
    })

    it('should not delete alert if confirmation is cancelled', async () => {
      const store = useJobsStore()
      const deleteAlertSpy = vi.spyOn(store, 'deleteAlert')
      vi.spyOn(window, 'confirm').mockReturnValue(false)

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

      await wrapper.vm.deleteAlert('1')

      expect(deleteAlertSpy).not.toHaveBeenCalled()
    })
  })

  describe('Edit alert frequency functionality', () => {
    it('should open edit modal with alert data', async () => {
      const alert = {
        id: '1',
        name: 'Test Alert',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
        is_active: true,
        created_at: new Date().toISOString(),
        new_jobs_count: 0,
      }

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

      wrapper.vm.editAlert(alert)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showModal).toBe(true)
      expect(wrapper.vm.editingAlert).toEqual(alert)
      expect(wrapper.vm.formData.name).toBe('Test Alert')
      expect(wrapper.vm.formData.frequency).toBe('daily')
    })

    it('should update alert with new frequency', async () => {
      const store = useJobsStore()
      const updateAlertSpy = vi.spyOn(store, 'updateAlert').mockResolvedValue({})

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

      wrapper.vm.editingAlert = { id: '1' }
      wrapper.vm.formData = {
        name: 'Updated Alert',
        query: 'Updated',
        frequency: 'weekly',
        notification_method: 'email',
      }

      await wrapper.vm.handleSubmit()

      expect(updateAlertSpy).toHaveBeenCalledWith('1', {
        name: 'Updated Alert',
        query: 'Updated',
        frequency: 'weekly',
        notification_method: 'email',
      })
    })
  })

  describe('Error handling and loading states', () => {
    it('should display form error when validation fails', async () => {
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

      wrapper.vm.formData = {
        name: '',
        query: '',
        frequency: 'daily',
        notification_method: 'email',
      }

      await wrapper.vm.handleSubmit()

      expect(wrapper.vm.formError).toBe('Please fix the errors in the form')
    })

    it('should show loading state during submission', async () => {
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

      wrapper.vm.formData = {
        name: 'Test',
        query: 'Test',
        frequency: 'daily',
        notification_method: 'email',
      }

      const submitPromise = wrapper.vm.handleSubmit()
      expect(wrapper.vm.isSubmitting).toBe(true)

      await submitPromise
      expect(wrapper.vm.isSubmitting).toBe(false)
    })

    it('should display operating state for individual alert actions', async () => {
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

      wrapper.vm.operatingAlertId = '1'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.operatingAlertId).toBe('1')
    })
  })

  describe('Statistics calculation', () => {
    it('should calculate total alerts correctly', async () => {
      const store = useJobsStore()
      store.alerts = [
        {
          id: '1',
          name: 'Alert 1',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
        {
          id: '2',
          name: 'Alert 2',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: false,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
      ]

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

      expect(wrapper.vm.totalAlerts).toBe(2)
    })

    it('should calculate active alerts correctly', async () => {
      const store = useJobsStore()
      store.alerts = [
        {
          id: '1',
          name: 'Alert 1',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
        {
          id: '2',
          name: 'Alert 2',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: false,
          created_at: new Date().toISOString(),
          new_jobs_count: 0,
        },
      ]

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

      expect(wrapper.vm.activeAlerts).toBe(1)
    })

    it('should calculate total new jobs correctly', async () => {
      const store = useJobsStore()
      store.alerts = [
        {
          id: '1',
          name: 'Alert 1',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 5,
        },
        {
          id: '2',
          name: 'Alert 2',
          query: 'Test',
          frequency: 'daily',
          notification_method: 'email',
          is_active: true,
          created_at: new Date().toISOString(),
          new_jobs_count: 3,
        },
      ]

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

      expect(wrapper.vm.totalNewJobs).toBe(8)
    })
  })
})
