/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          500: '#3b82f6',
          600: '#2563eb',
          900: '#1e3a8a',
        },
        status: {
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          idle: '#6b7280',
        },
        dark: {
          primary: '#0f172a',
          secondary: '#1e293b',
          tertiary: '#334155',
          text: {
            primary: '#f8fafc',
            secondary: '#cbd5e1',
          }
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'Segoe UI', 'Roboto', 'sans-serif'],
        serif: ['Crimson Text', 'Georgia', 'serif'],
      },
      spacing: {
        '1': '0.25rem',
        '2': '0.5rem',
        '3': '0.75rem',
        '4': '1rem',
        '5': '1.25rem',
        '6': '1.5rem',
        '8': '2rem',
        '10': '2.5rem',
        '12': '3rem',
        '16': '4rem',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}