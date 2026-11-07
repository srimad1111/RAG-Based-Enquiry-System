/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          bg: '#0B1020',
          base: '#0B1020',
          sidebar: '#0E1526',
          card: '#141E33',
          'card-hover': '#1A2845',
          surface: '#192640',
          'surface-hover': '#213354',
          elevated: '#1D2C4A',
          void: '#070A14',
          border: 'rgba(255, 255, 255, 0.08)',
          'border-light': 'rgba(255, 255, 255, 0.15)',
        },
        accent: {
          blue: '#4F8CFF',
          'blue-hover': '#3D7AE8',
          'blue-light': '#7AA7FF',
          violet: '#9B7BFF',
          'violet-hover': '#8664F0',
          'violet-light': '#B69EFF',
          emerald: '#27C99A',
          'emerald-hover': '#1EB387',
          cyan: '#28C7E8',
          amber: '#F5B942',
          coral: '#F43F5E',
        },
        violetAccent: {
          DEFAULT: '#9B7BFF',
          hover: '#8664F0',
          light: '#B69EFF',
          glow: 'rgba(155, 123, 255, 0.25)',
        },
        blueAccent: {
          DEFAULT: '#4F8CFF',
          hover: '#3D7AE8',
          light: '#7AA7FF',
          glow: 'rgba(79, 140, 255, 0.25)',
        },
        emeraldAccent: {
          DEFAULT: '#27C99A',
          hover: '#1EB387',
          light: '#4DE0B5',
        },
        amberAccent: {
          DEFAULT: '#F5B942',
          hover: '#E0A331',
          light: '#F8C768',
        },
        roseAccent: {
          DEFAULT: '#F43F5E',
          hover: '#E11D48',
          light: '#FB7185',
        },
      },
      boxShadow: {
        'glow-blue': '0 0 20px -2px rgba(79, 140, 255, 0.35)',
        'glow-violet': '0 0 20px -2px rgba(155, 123, 255, 0.35)',
        'card': '0 4px 16px -2px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.07)',
        'modal': '0 20px 40px -8px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.1)',
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
