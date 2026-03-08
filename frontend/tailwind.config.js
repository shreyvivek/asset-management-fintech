/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        display: ['Instrument Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
        'tick-up': 'tick-up 0.4s ease-out',
        'tick-down': 'tick-down 0.4s ease-out',
      },
      keyframes: {
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.85' },
        },
        'tick-up': {
          '0%': { transform: 'translateY(4px)', opacity: '0.6' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'tick-down': {
          '0%': { transform: 'translateY(-4px)', opacity: '0.6' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
