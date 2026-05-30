/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#05070D',
        'canvas-light': '#080B12',
        'canvas-lighter': '#0B1020',
        panel: 'rgba(15, 23, 42, 0.72)',
        'panel-solid': '#0F172A',
        'panel-hover': 'rgba(15, 23, 42, 0.92)',
        border: 'rgba(148, 163, 184, 0.16)',
        accent: {
          cyan: '#22D3EE',
          blue: '#3B82F6',
          violet: '#8B5CF6',
        },
        state: {
          success: '#22C55E',
          warning: '#F59E0B',
          danger: '#EF4444',
          info: '#38BDF8',
        },
        text: {
          primary: '#F8FAFC',
          secondary: '#CBD5E1',
          muted: '#94A3B8',
          dim: '#64748B',
        },
      },
      borderRadius: {
        card: '18px',
        'card-lg': '24px',
        button: '12px',
        'button-lg': '16px',
        pill: '999px',
      },
      boxShadow: {
        glass: '0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06)',
        'glass-lg': '0 8px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08)',
        glow: '0 0 20px rgba(34, 211, 238, 0.15)',
        'glow-violet': '0 0 20px rgba(139, 92, 246, 0.15)',
      },
    },
  },
  plugins: [],
}
