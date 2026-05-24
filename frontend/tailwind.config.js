/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#0b1724',
        panel: '#112337',
        accent: '#f59e0b',
      },
    },
  },
  plugins: [],
}
