/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Segoe UI', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        /* Microsoft Fluent Palette */
        brand: {
          DEFAULT: '#0078d4',
          hover: '#106ebe',
          active: '#005a9e',
          light: '#2b88d8',
          dim: 'rgba(0, 120, 212, 0.1)',
        },
        gray: {
          950: '#0b0b0a', // Deep black for Fluent dark mode
          900: '#11100f', // Standard Fluent dark background
          800: '#1b1a19',
          700: '#252423',
          600: '#323130',
          500: '#605e5c',
          400: '#a19f9d',
          300: '#c8c6c4',
          200: '#edebe9',
          100: '#f3f2f1',
          50: '#faf9f8',
        },
        /* Semantic */
        success: '#107c10',
        error: '#a4262c',
        warning: '#ffb900',
        info: '#0078d4',
      },
      boxShadow: {
        'fluent-sm': '0 2px 8px rgba(0, 0, 0, 0.04)',
        'fluent-md': '0 8px 20px rgba(0, 0, 0, 0.06)',
        'fluent-lg': '0 12px 32px rgba(0, 0, 0, 0.1)',
        'fluent-xl': '0 24px 64px rgba(0, 0, 0, 0.14)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
      },
      borderRadius: {
        'none': '0',
        'xs': '0.25rem',
        'sm': '0.5rem',
        'DEFAULT': '1rem', // 16px
        'md': '1.25rem',
        'lg': '1.5rem',
        'xl': '2rem',
        '2xl': '2.5rem',
        '3xl': '3rem',
        'full': '9999px',
        'fluent': '8px',
        'fluent-lg': '16px',
        'fluent-xl': '24px',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    function ({ addComponents, theme }) {
      addComponents({
        /* Centralized Fluent Form Styles */
        '.fluent-input': {
          width: '100%',
          padding: '0.625rem 1rem',
          backgroundColor: theme('colors.white'),
          border: `1px solid ${theme('colors.gray.300')}`,
          borderRadius: theme('borderRadius.DEFAULT'),
          fontSize: '0.875rem',
          lineHeight: '1.25rem',
          transition: 'all 0.15s ease-in-out',
          outline: 'none',
          '&:hover': {
            borderColor: theme('colors.gray.400'),
          },
          '&:focus': {
            borderColor: theme('colors.brand.DEFAULT'),
            boxShadow: `0 0 0 1px ${theme('colors.brand.DEFAULT')}`,
          },
          '&:disabled': {
            backgroundColor: theme('colors.gray.100'),
            color: theme('colors.gray.500'),
            cursor: 'not-allowed',
          },
          '.dark &': {
            backgroundColor: theme('colors.gray.800'),
            borderColor: theme('colors.gray.700'),
            color: theme('colors.white'),
            '&:hover': {
              borderColor: theme('colors.gray.600'),
            },
            '&:focus': {
              borderColor: theme('colors.brand.DEFAULT'),
              boxShadow: `0 0 0 1px ${theme('colors.brand.DEFAULT')}`,
            },
            '&:disabled': {
              backgroundColor: theme('colors.gray.900'),
              color: theme('colors.gray.600'),
            },
          },
        },
        '.fluent-select': {
          width: '100%',
          padding: '0.625rem 2.5rem 0.625rem 1rem',
          backgroundColor: theme('colors.white'),
          border: `1px solid ${theme('colors.gray.300')}`,
          borderRadius: theme('borderRadius.DEFAULT'),
          fontSize: '0.875rem',
          lineHeight: '1.25rem',
          transition: 'all 0.15s ease-in-out',
          outline: 'none',
          appearance: 'none',
          cursor: 'pointer',
          '&:hover:not(:disabled)': {
            borderColor: theme('colors.gray.400'),
          },
          '&:focus': {
            borderColor: theme('colors.brand.DEFAULT'),
            boxShadow: `0 0 0 1px ${theme('colors.brand.DEFAULT')}`,
          },
          '&:disabled': {
            backgroundColor: theme('colors.gray.100'),
            color: theme('colors.gray.500'),
            cursor: 'not-allowed',
            opacity: '0.6',
          },
          '.dark &': {
            backgroundColor: theme('colors.gray.800'),
            borderColor: theme('colors.gray.700'),
            color: theme('colors.white'),
            '&:hover:not(:disabled)': {
              borderColor: theme('colors.gray.600'),
            },
            '&:focus': {
              borderColor: theme('colors.brand.DEFAULT'),
              boxShadow: `0 0 0 1px ${theme('colors.brand.DEFAULT')}`,
            },
            '&:disabled': {
              backgroundColor: theme('colors.gray.900'),
              color: theme('colors.gray.600'),
            },
          },
        },
        '.fluent-button': {
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0.5rem 1.25rem',
          borderRadius: theme('borderRadius.DEFAULT'),
          fontSize: '0.875rem',
          fontWeight: '600',
          transition: 'all 0.15s ease-in-out',
          cursor: 'pointer',
          '&:disabled': {
            opacity: '0.6',
            cursor: 'not-allowed',
          },
          '&:active:not(:disabled)': {
            transform: 'scale(0.98)',
          },
        },
        '.fluent-button-primary': {
          backgroundColor: theme('colors.brand.DEFAULT'),
          color: theme('colors.white'),
          '&:hover:not(:disabled)': {
            backgroundColor: theme('colors.brand.hover'),
          },
          '&:active:not(:disabled)': {
            backgroundColor: theme('colors.brand.active'),
          },
        },
        '.fluent-card': {
          backgroundColor: theme('colors.white'),
          border: `1px solid ${theme('colors.gray.200')}`,
          borderRadius: theme('borderRadius.fluent-lg'),
          boxShadow: theme('boxShadow.fluent-sm'),
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: theme('boxShadow.fluent-md'),
          },
          '.dark &': {
            backgroundColor: theme('colors.gray.900'),
            borderColor: theme('colors.gray.800'),
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.4)',
            '&:hover': {
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.6)',
            },
          },
        },
      });
    },
  ],
};
