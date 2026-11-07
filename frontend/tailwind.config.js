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
          void: '#05070B',
          base: '#080B10',
          sidebar: '#06080D',
          card: '#0F1420',
          'card-hover': '#141A29',
          elevated: '#171F33',
          inset: '#0B0F17',
        },
        border: {
          subtle: 'rgba(255, 255, 255, 0.06)',
          light: 'rgba(255, 255, 255, 0.1)',
          focus: 'rgba(139, 92, 246, 0.5)',
        },
        violetAccent: {
          DEFAULT: '#8B5CF6',
          hover: '#7C3AED',
          light: '#A78BFA',
          glow: 'rgba(139, 92, 246, 0.25)',
        },
        blueAccent: {
          DEFAULT: '#38BDF8',
          hover: '#0EA5E9',
          light: '#7DD3FC',
          glow: 'rgba(56, 189, 248, 0.2)',
        },
        emeraldAccent: {
          DEFAULT: '#10B981',
          hover: '#059669',
          light: '#34D399',
        },
        amberAccent: {
          DEFAULT: '#F59E0B',
          hover: '#D97706',
          light: '#FBBF24',
        },
        roseAccent: {
          DEFAULT: '#F43F5E',
          hover: '#E11D48',
          light: '#FB7185',
        },
      },
      boxShadow: {
        'glow-violet': '0 0 25px -4px rgba(139, 92, 246, 0.35)',
        'glow-blue': '0 0 25px -4px rgba(56, 189, 248, 0.3)',
        'glow-emerald': '0 0 25px -4px rgba(16, 185, 129, 0.3)',
        'dark-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.4)',
        'dark-card': '0 4px 20px -2px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.07)',
        'dark-elevated': '0 10px 30px -5px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.09)',
        'dark-glass': '0 8px 32px 0 rgba(0, 0, 0, 0.6), inset 0 0 0 1px rgba(255, 255, 255, 0.08)',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
