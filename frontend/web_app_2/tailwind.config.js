/** @type {import('tailwindcss').Config} */
import daisyui from 'daisyui';

export default {
  content: ["index.html", "./src/**/*.{html,js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        inter: ['"Inter"'], // Add your font here
        grotesk: ['"Schibsted Grotesk"'],
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        // Formal Light Theme
        formalLight: {
          "primary": "#000000",         // Red accent for emphasis
          "secondary": "#7c7b80",        // Dark blue for primary actions
          "accent": "#ddff7c",      // Muted blue for secondary actions
          "neutral": "#ffffff",        // Light gray for backgrounds
          "base-100": "#f7f4f2",       // White background
          "base-200": "#8a878b",       // Slightly off-white
          "base-300": "#E9ECEF",       // Light gray for borders
          "info": "#17A2B8",           // Info color
          "success": "#28A745",        // Success color
          "warning": "#FFC107",        // Warning color
          "error": "#DC3545",          // Error color
        },
      },
    ]
  }
}
