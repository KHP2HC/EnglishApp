import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{ts,tsx}',
    './src/components/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          dark: '#0F0F0F',
          light: '#F8F9FA',
        },
        surface: {
          dark: '#1A1A2E',
          light: '#FFFFFF',
          DEFAULT: '#1A1A2E',
        },
        border: {
          dark: '#2A2A3E',
          light: '#E5E7EB',
          DEFAULT: '#2A2A3E',
        },
        accent: {
          DEFAULT: '#4A90E2',
          hover: '#3A7BD5',
        },
        success: '#27AE60',
        warning: '#F39C12',
        error: '#E74C3C',
        xp: '#F59E0B',
      },
      fontFamily: {
        heading: ['Outfit', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        xl: '12px',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
