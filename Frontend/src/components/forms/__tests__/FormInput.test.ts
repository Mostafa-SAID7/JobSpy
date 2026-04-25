import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FormInput from '../FormInput.vue'

describe('FormInput Component', () => {
  describe('Rendering', () => {
    it('should render input field with label', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Email',
          modelValue: '',
          type: 'email',
        },
      })

      expect(wrapper.find('label').text()).toBe('Email')
      expect(wrapper.find('input').exists()).toBe(true)
    })

    it('should render with correct input type', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Password',
          modelValue: '',
          type: 'password',
        },
      })

      expect(wrapper.find('input').attributes('type')).toBe('password')
    })

    it('should display placeholder text', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Username',
          modelValue: '',
          placeholder: 'Enter your username',
        },
      })

      expect(wrapper.find('input').attributes('placeholder')).toBe('Enter your username')
    })

    it('should display error message when provided', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Email',
          modelValue: '',
          error: 'Invalid email format',
        },
      })

      expect(wrapper.text()).toContain('Invalid email format')
    })
  })

  describe('v-model binding', () => {
    it('should update modelValue on input', async () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Test',
          modelValue: '',
        },
      })

      await wrapper.find('input').setValue('test value')
      const emitted = wrapper.emitted('update:modelValue')
      expect(emitted).toBeTruthy()
      expect(emitted?.[0]).toEqual(['test value'])
    })

    it('should display initial modelValue', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Test',
          modelValue: 'initial value',
        },
      })

      const inputElement = wrapper.find('input').element as HTMLInputElement
      expect(inputElement.value).toBe('initial value')
    })
  })

  describe('Disabled state', () => {
    it('should disable input when disabled prop is true', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Test',
          modelValue: '',
          disabled: true,
        },
      })

      expect(wrapper.find('input').attributes('disabled')).toBeDefined()
    })

    it('should not emit events when disabled', async () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Test',
          modelValue: '',
          disabled: true,
        },
      })

      await wrapper.find('input').setValue('test')
      expect(wrapper.emitted('update:modelValue')).toBeFalsy()
    })
  })

  describe('Required field indicator', () => {
    it('should show required indicator when required prop is true', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Email',
          modelValue: '',
          required: true,
        },
      })

      expect(wrapper.text()).toContain('*')
    })

    it('should not show required indicator when required prop is false', () => {
      const wrapper = mount(FormInput, {
        props: {
          label: 'Email',
          modelValue: '',
          required: false,
        },
      })

      expect(wrapper.text()).not.toContain('*')
    })
  })
})
