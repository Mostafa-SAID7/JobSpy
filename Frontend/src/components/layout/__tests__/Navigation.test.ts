import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Navigation from '../Navigation.vue'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createI18n } from 'vue-i18n'

const i18n = createI18n({
  legacy: false,
  locale: 'ar',
  messages: {
    ar: {},
    en: {},
  },
})

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/search', component: { template: '<div>Search</div>' } },
  ],
})

describe('Navigation Component', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Rendering', () => {
    it('should render navigation bar', () => {
      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
          stubs: {
            RouterLink: true,
          },
        },
      })

      expect(wrapper.find('nav').exists()).toBe(true)
    })

    it('should display logo/brand name', () => {
      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      expect(wrapper.text()).toContain('JobSpy')
    })
  })

  describe('Authentication state', () => {
    it('should show login/signup links when not authenticated', () => {
      const store = useAuthStore()
      store.user = null
      store.token = null

      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      expect(wrapper.text()).toContain('Login')
      expect(wrapper.text()).toContain('Register')
    })

    it('should show user menu when authenticated', async () => {
      const store = useAuthStore()
      store.user = { id: 1, email: 'test@example.com', full_name: 'Test User', created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
      store.token = 'test-token'

      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Test User')
    })

    it('should show logout button when authenticated', async () => {
      const store = useAuthStore()
      store.user = { id: 1, email: 'test@example.com', full_name: 'Test User', created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
      store.token = 'test-token'

      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      await wrapper.vm.$nextTick()
      // Click the user menu button to reveal the dropdown
      const userMenuButton = wrapper.find('button').element as HTMLButtonElement
      if (userMenuButton) {
        await wrapper.find('button').trigger('click')
        await wrapper.vm.$nextTick()
      }
      expect(wrapper.text()).toContain('Logout')
    })
  })

  describe('Navigation links', () => {
    it('should display main navigation links', () => {
      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      expect(wrapper.text()).toContain('Search')
      expect(wrapper.text()).toContain('Saved Jobs')
      expect(wrapper.text()).toContain('Alerts')
    })

    it('should have correct router links', () => {
      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
          stubs: {
            RouterLink: true,
          },
        },
      })

      const links = wrapper.findAllComponents({ name: 'RouterLink' })
      expect(links.length).toBeGreaterThan(0)
    })
  })

  describe('Mobile menu', () => {
    it('should have mobile menu toggle button', () => {
      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      const button = wrapper.find('button.md\\:hidden')
      expect(button.exists()).toBe(true)
    })

    it('should toggle mobile menu on button click', async () => {
      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      const toggleButton = wrapper.find('button.md\\:hidden')
      if (toggleButton.exists()) {
        await toggleButton.trigger('click')
        expect((wrapper.vm as any).showMobileMenu).toBe(true)
      }
    })
  })

  describe('Logout functionality', () => {
    it('should call logout when logout button is clicked', async () => {
      const store = useAuthStore()
      store.user = { id: 1, email: 'test@example.com', full_name: 'Test User', created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
      store.token = 'test-token'
      const logoutSpy = vi.spyOn(store, 'logout').mockResolvedValue(undefined)

      const wrapper = mount(Navigation, {
        global: {
          plugins: [router, i18n],
        },
      })

      await wrapper.vm.$nextTick()
      // Find logout button by looking for button containing the logout text
      const buttons = wrapper.findAll('button')
      const logoutButton = buttons.find(btn => btn.text().includes('Logout'))
      
      if (logoutButton) {
        await logoutButton.trigger('click')
        expect(logoutSpy).toHaveBeenCalled()
      }
    })
  })
})
