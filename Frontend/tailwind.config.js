/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      /* ── Typography ──────────────────────────────────────────────────── */
      fontFamily: {
        sans: ['Rationale', 'Segoe UI', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        xs: ['0.6875rem', { lineHeight: '1rem' }],      // 11px
        sm: ['0.8125rem', { lineHeight: '1.25rem' }],   // 13px
        md: ['0.9375rem', { lineHeight: '1.5rem' }],    // 15px
        lg: ['1.0625rem', { lineHeight: '1.5rem' }],    // 17px
        xl: ['1.25rem', { lineHeight: '1.75rem' }],     // 20px
        '2xl': ['1.75rem', { lineHeight: '2.25rem' }],  // 28px
        '3xl': ['2.25rem', { lineHeight: '2.75rem' }],  // 36px
      },

      /* ── Spacing (4px base) ──────────────────────────────────────────── */
      spacing: {
        1: '0.25rem',   // 4px
        2: '0.5rem',    // 8px
        3: '0.75rem',   // 12px
        4: '1rem',      // 16px
        5: '1.25rem',   // 20px
        6: '1.5rem',    // 24px
        8: '2rem',      // 32px
        10: '2.5rem',   // 40px
        12: '3rem',     // 48px
        16: '4rem',     // 64px
      },

      /* ── Border Radius ───────────────────────────────────────────────── */
      borderRadius: {
        sm: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px',
        full: '9999px',
      },

      /* ── Colors (Dark theme as default) ──────────────────────────────── */
      colors: {
        /* Backgrounds */
        'bg-app': '#0e0e0e',
        'bg-panel': '#161616',
        'bg-input': '#1e1e1e',
        'bg-hover': '#252525',
        'bg-active': '#2a2a2a',
        'bg-card': '#161616',
        'bg-main': '#0e0e0e',
        'bg-surface': '#1e1e1e',

        /* Borders */
        'bd-subtle': 'rgba(255,255,255,0.06)',
        'bd-moderate': 'rgba(255,255,255,0.12)',
        'bd-strong': 'rgba(255,255,255,0.20)',
        'bd-1': 'rgba(255,255,255,0.09)',
        'br-muted': 'rgba(255,255,255,0.06)',

        /* Accent (Microsoft Blue) */
        'accent': '#0078d4',
        'accent-light': '#2899f5',
        'accent-dim': 'rgba(0,120,212,0.18)',
        'accent-glow': 'rgba(0,120,212,0.30)',

        /* Semantic Colors */
        'success': '#4ec94e',
        'error': '#f1707a',
        'warn': '#fcba19',
        'info': '#60cdff',

        'success-bg': 'rgba(78,201,78,0.10)',
        'error-bg': 'rgba(241,112,122,0.10)',
        'info-bg': 'rgba(96,205,255,0.10)',

        'success-bd': 'rgba(78,201,78,0.28)',
        'error-bd': 'rgba(241,112,122,0.28)',
        'info-bd': 'rgba(96,205,255,0.28)',

        /* Text */
        'tx-1': '#f0f0f0',
        'tx-2': '#c8c8c8',
        'tx-3': '#8a8a8a',
        'tx-4': '#555555',
        'tx-text': '#c8c8c8',

        /* Tag Colors */
        'tag-fe-bg': '#0e1f3d',
        'tag-fe-tx': '#60a5fa',
        'tag-be-bg': '#0a1e22',
        'tag-be-tx': '#34d399',
        'tag-fs-bg': '#1a1033',
        'tag-fs-tx': '#a78bfa',
        'tag-asp-bg': '#1c0a2a',
        'tag-asp-tx': '#c084fc',
        'tag-oth-bg': '#1a1a1a',
        'tag-oth-tx': '#9ca3af',

        /* Platform Colors */
        'clr-wuzzuf': '#2969ff',
        'clr-bayt': '#ff501e',
        'clr-linkedin': '#00a3e0',

        /* Feedback & Motion */
        'skeleton-shimmer': 'rgba(255,255,255,0.05)',
        'overlay-bg': 'rgba(0,0,0,0.75)',
        'panel-bg': '#161616',
      },

      /* ── Box Shadows ─────────────────────────────────────────────────── */
      boxShadow: {
        sm: '0 1px 4px rgba(0,0,0,0.55)',
        md: '0 4px 20px rgba(0,0,0,0.65)',
        lg: '0 8px 40px rgba(0,0,0,0.75)',
      },

      /* ── Animation & Transitions ─────────────────────────────────────── */
      transitionDuration: {
        fast: '120ms',
        base: '200ms',
      },
      transitionTimingFunction: {
        'ease-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      animation: {
        spin: 'spin 1s linear infinite',
        'fade-in': 'fadeIn 200ms ease-out forwards',
        'fade-in-up': 'fadeInUp 220ms cubic-bezier(0.16, 1, 0.3, 1) both',
        'slide-in-up': 'slideInUp 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-dot': 'pulseDot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        spin: {
          to: { transform: 'rotate(360deg)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        slideInUp: {
          from: { transform: 'translateY(10px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
        pulse: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.5', transform: 'scale(1.2)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.5', transform: 'scale(0.75)' },
        },
      },

      /* ── Responsive Breakpoints ──────────────────────────────────────── */
      screens: {
        sm: '480px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [
    /* ── Component Layer Plugin ──────────────────────────────────────── */
    function ({ addComponents, theme }) {
      const components = {
        /* Form Controls */
        '.form-row': {
          display: 'grid',
          gridTemplateColumns: '2fr 2fr 1fr',
          gap: theme('spacing.4'),
          alignItems: 'end',
          '@media (max-width: 1024px)': {
            gridTemplateColumns: '1fr 1fr',
          },
          '@media (max-width: 768px)': {
            gridTemplateColumns: '1fr',
          },
        },
        '.form-field': {
          display: 'flex',
          flexDirection: 'column',
          gap: theme('spacing.2'),
        },
        '.form-label': {
          fontSize: theme('fontSize.sm[0]'),
          fontWeight: '500',
          color: theme('colors.tx-3'),
          display: 'flex',
          alignItems: 'center',
          gap: theme('spacing.2'),
          userSelect: 'none',
        },
        '.form-label i': {
          color: theme('colors.accent-light'),
          fontSize: theme('fontSize.xs[0]'),
        },
        '.form-control': {
          width: '100%',
          padding: `10px ${theme('spacing.4')}`,
          background: theme('colors.bg-input'),
          border: `1px solid ${theme('colors.bd-moderate')}`,
          borderRadius: theme('borderRadius.md'),
          color: theme('colors.tx-1'),
          fontFamily: theme('fontFamily.sans'),
          fontSize: theme('fontSize.sm[0]'),
          transition: `border-color ${theme('transitionDuration.fast')}, box-shadow ${theme('transitionDuration.fast')}`,
          outline: 'none',
          '&:hover': {
            borderColor: theme('colors.bd-strong'),
          },
          '&:focus': {
            borderColor: theme('colors.accent'),
            boxShadow: `0 0 0 3px ${theme('colors.accent-dim')}`,
          },
        },

        /* Custom Select */
        '.custom-select': {
          position: 'relative',
          width: '100%',
          userSelect: 'none',
        },
        '.select-trigger': {
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: `10px ${theme('spacing.4')}`,
          background: theme('colors.bg-input'),
          border: `1px solid ${theme('colors.bd-moderate')}`,
          borderRadius: theme('borderRadius.md'),
          color: theme('colors.tx-1'),
          fontSize: theme('fontSize.sm[0]'),
          cursor: 'pointer',
          transition: `border-color ${theme('transitionDuration.fast')}, box-shadow ${theme('transitionDuration.fast')}`,
          '&:hover': {
            borderColor: theme('colors.bd-strong'),
          },
          '&.active': {
            borderColor: theme('colors.accent'),
            boxShadow: `0 0 0 3px ${theme('colors.accent-dim')}`,
          },
        },
        '.select-options': {
          position: 'absolute',
          top: 'calc(100% + 4px)',
          left: '0',
          right: '0',
          background: theme('colors.bg-input'),
          border: `1px solid ${theme('colors.bd-strong')}`,
          borderRadius: theme('borderRadius.md'),
          boxShadow: theme('boxShadow.lg'),
          zIndex: '1000',
          maxHeight: '250px',
          overflowY: 'auto',
          display: 'none',
          '&.show': {
            display: 'block',
          },
        },
        '.select-option': {
          padding: `10px ${theme('spacing.4')}`,
          color: theme('colors.tx-2'),
          fontSize: theme('fontSize.sm[0]'),
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: theme('spacing.2'),
          '&:hover': {
            background: theme('colors.bg-hover'),
            color: theme('colors.tx-1'),
          },
          '&.selected': {
            background: theme('colors.accent-dim'),
            color: theme('colors.accent-light'),
          },
        },

        /* Buttons */
        '.btn': {
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px',
          padding: `11px ${theme('spacing.4')}`,
          border: '1px solid transparent',
          borderRadius: theme('borderRadius.md'),
          fontFamily: theme('fontFamily.sans'),
          fontSize: theme('fontSize.sm[0]'),
          fontWeight: '600',
          cursor: 'pointer',
          whiteSpace: 'nowrap',
          transition: `all ${theme('transitionDuration.fast')} ${theme('transitionTimingFunction.ease-out')}`,
          position: 'relative',
          overflow: 'hidden',
          width: '100%',
          '&:disabled': {
            opacity: '0.6',
            cursor: 'not-allowed',
          },
        },
        '.btn-primary': {
          background: theme('colors.accent'),
          color: '#fff',
          borderColor: theme('colors.accent'),
          '&:hover:not(:disabled)': {
            background: theme('colors.accent-light'),
            borderColor: theme('colors.accent-light'),
            boxShadow: `0 4px 16px ${theme('colors.accent-glow')}`,
            transform: 'translateY(-1px)',
          },
        },
        '.btn-secondary': {
          background: 'transparent',
          color: theme('colors.tx-3'),
          borderColor: theme('colors.bd-moderate'),
          '&:hover:not(:disabled)': {
            background: theme('colors.bg-hover'),
            color: theme('colors.tx-1'),
            borderColor: theme('colors.bd-strong'),
          },
        },
        '.btn-warning': {
          background: theme('colors.warn'),
          color: '#000',
          borderColor: theme('colors.warn'),
          '&:hover:not(:disabled)': {
            opacity: '0.9',
            boxShadow: `0 4px 16px rgba(252, 186, 25, 0.3)`,
            transform: 'translateY(-1px)',
          },
        },
        '.btn-success': {
          background: theme('colors.success'),
          color: '#000',
          borderColor: theme('colors.success'),
          '&:hover:not(:disabled)': {
            opacity: '0.9',
            boxShadow: `0 4px 16px rgba(78, 201, 78, 0.3)`,
            transform: 'translateY(-1px)',
          },
        },
        '.btn-sm': {
          padding: `7px ${theme('spacing.3')}`,
          fontSize: theme('fontSize.xs[0]'),
          gap: '6px',
        },

        /* Job Card Link */
        '.job-card__link': {
          fontSize: theme('fontSize.xs[0]'),
          color: theme('colors.tx-3'),
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          transition: `color ${theme('transitionDuration.fast')}`,
          '&:hover': {
            color: theme('colors.accent-light'),
            textDecoration: 'none',
          },
        },

        /* Empty State */
        '.empty-state': {
          gridColumn: '1 / -1',
          padding: `${theme('spacing.12')} ${theme('spacing.6')}`,
          textAlign: 'center',
          color: theme('colors.tx-4'),
          fontSize: theme('fontSize.sm[0]'),
          border: `1px dashed ${theme('colors.bd-moderate')}`,
          borderRadius: theme('borderRadius.xl'),
        },

        /* Form Actions */
        '.form-actions': {
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: theme('spacing.4'),
          marginTop: theme('spacing.8'),
          paddingTop: theme('spacing.8'),
          borderTop: `1px solid ${theme('colors.bd-subtle')}`,
          '@media (max-width: 1024px)': {
            gridTemplateColumns: 'repeat(2, 1fr)',
          },
          '@media (max-width: 480px)': {
            gridTemplateColumns: '1fr',
          },
        },

        /* Chips */
        '.chip-group': {
          display: 'flex',
          gap: theme('spacing.2'),
          flexWrap: 'wrap',
        },
        '.chip': {
          padding: `5px ${theme('spacing.3')}`,
          border: `1px solid ${theme('colors.bd-moderate')}`,
          borderRadius: theme('borderRadius.full'),
          fontSize: theme('fontSize.xs[0]'),
          fontWeight: '600',
          cursor: 'pointer',
          color: theme('colors.tx-3'),
          '&.active': {
            background: theme('colors.accent-dim'),
            borderColor: theme('colors.accent'),
            color: theme('colors.accent-light'),
          },
        },

        /* Filter Panel */
        '.filter-panel': {
          background: theme('colors.bg-panel'),
          border: `1px solid ${theme('colors.bd-subtle')}`,
          borderRadius: theme('borderRadius.xl'),
          padding: `${theme('spacing.4')} ${theme('spacing.6')}`,
          marginBottom: theme('spacing.6'),
          boxShadow: theme('boxShadow.sm'),
        },
        '.filter-inner': {
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: theme('spacing.6'),
          flexWrap: 'wrap',
          '@media (max-width: 768px)': {
            flexDirection: 'column',
            alignItems: 'stretch',
          },
        },
        '.filter-search': {
          position: 'relative',
          flex: '1',
          minWidth: '300px',
        },
        '.filter-search__icon': {
          position: 'absolute',
          left: theme('spacing.4'),
          top: '50%',
          transform: 'translateY(-50%)',
          color: theme('colors.tx-4'),
          pointerEvents: 'none',
        },
        '.filter-search .form-control': {
          paddingLeft: `calc(${theme('spacing.4')} + 20px)`,
        },

        /* Stats */
        '.stats-row': {
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: theme('spacing.4'),
          marginBottom: theme('spacing.6'),
          '@media (max-width: 1024px)': {
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: theme('spacing.3'),
          },
          '@media (max-width: 768px)': {
            gridTemplateColumns: '1fr',
          },
        },
        '.stat-tile': {
          background: theme('colors.bg-panel'),
          border: `1px solid ${theme('colors.bd-subtle')}`,
          borderRadius: theme('borderRadius.xl'),
          padding: theme('spacing.5'),
          display: 'flex',
          alignItems: 'center',
          gap: theme('spacing.4'),
          boxShadow: theme('boxShadow.sm'),
          transition: `transform ${theme('transitionDuration.fast')}, box-shadow ${theme('transitionDuration.fast')}`,
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: theme('boxShadow.md'),
            borderColor: theme('colors.bd-moderate'),
          },
        },
        '.stat-tile__icon': {
          display: 'grid',
          placeItems: 'center',
          width: '48px',
          height: '48px',
          borderRadius: theme('borderRadius.lg'),
          background: theme('colors.accent-dim'),
          color: theme('colors.accent-light'),
          fontSize: '1.25rem',
          flexShrink: '0',
        },
        '.stat-tile__body': {
          display: 'flex',
          flexDirection: 'column',
        },
        '.stat-tile__value': {
          fontSize: theme('fontSize.xl[0]'),
          fontWeight: '700',
          color: theme('colors.tx-1'),
          lineHeight: '1.2',
        },
        '.stat-tile__label': {
          fontSize: theme('fontSize.xs[0]'),
          color: theme('colors.tx-3'),
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          fontWeight: '600',
          marginTop: '2px',
        },

        /* Utility Classes */
        '.mt-1': { marginTop: theme('spacing.1') },
        '.mt-2': { marginTop: theme('spacing.2') },
        '.mt-3': { marginTop: theme('spacing.3') },
        '.mt-4': { marginTop: theme('spacing.4') },
      };

      addComponents(components);
    },

    /* ── Light Theme Plugin ──────────────────────────────────────────── */
    function ({ addBase, theme }) {
      addBase({
        'body.light-theme': {
          '--bg-app': '#f5f7fa',
          '--bg-panel': '#ffffff',
          '--bg-input': '#fcfcfc',
          '--bg-hover': '#f0f2f5',
          '--bg-active': '#e8eaed',

          '--bd-subtle': 'rgba(0,0,0,0.06)',
          '--bd-moderate': 'rgba(0,0,0,0.12)',
          '--bd-strong': 'rgba(0,0,0,0.20)',

          '--tx-1': '#1a1a1a',
          '--tx-2': '#333333',
          '--tx-3': '#666666',
          '--tx-4': '#999999',

          '--tag-fe-bg': '#dbeafe',
          '--tag-fe-tx': '#1e40af',
          '--tag-be-bg': '#d1fae5',
          '--tag-be-tx': '#065f46',
          '--tag-fs-bg': '#ede9fe',
          '--tag-fs-tx': '#5b21b6',
          '--tag-asp-bg': '#f3e8ff',
          '--tag-asp-tx': '#6b21a8',
          '--tag-oth-bg': '#f3f4f6',
          '--tag-oth-tx': '#374151',

          '--shadow-sm': '0 1px 4px rgba(0,0,0,0.05)',
          '--shadow-md': '0 4px 20px rgba(0,0,0,0.08)',
          '--shadow-lg': '0 8px 40px rgba(0,0,0,0.12)',

          '--bg-card': '#ffffff',
          '--bg-main': '#f5f7fa',
          '--bg-surface': '#fcfcfc',
          '--bd-1': 'rgba(0,0,0,0.09)',
          '--br-muted': 'rgba(0,0,0,0.06)',
          '--clr-text': '#333333',
          '--panel-bg': '#ffffff',

          '--clr-wuzzuf': '#1e40af',
          '--clr-bayt': '#c2410c',
          '--clr-linkedin': '#0369a1',

          '--skeleton-shimmer': 'rgba(0,0,0,0.05)',
          '--overlay-bg': 'rgba(255,255,255,0.75)',
        },
      });
    },
  ],
};
