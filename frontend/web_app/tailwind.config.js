// tailwind.config.js
import daisyui from 'daisyui';

export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: { extend: {} },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        // Formal Light Theme
        formalLight: {
          "primary": "#1D3557",        // Dark blue for primary actions
          "secondary": "#457B9D",      // Muted blue for secondary actions
          "accent": "#E63946",         // Red accent for emphasis
          "neutral": "#F1FAEE",        // Light gray for backgrounds
          "base-100": "#FFFFFF",       // White background
          "base-200": "#F8F9FA",       // Slightly off-white
          "base-300": "#E9ECEF",       // Light gray for borders
          "info": "#17A2B8",           // Info color
          "success": "#28A745",        // Success color
          "warning": "#FFC107",        // Warning color
          "error": "#DC3545",          // Error color
        },
      },
      {
        // Formal Dark Theme
        formalDark: {
          "primary": "#ADB5BD",        // Light gray for primary actions
          "secondary": "#6C757D",      // Medium gray for secondary actions
          "accent": "#E63946",         // Red accent for emphasis
          "neutral": "#212529",        // Dark gray for backgrounds
          "base-100": "#343A40",       // Dark background
          "base-200": "#212529",       // Even darker background
          "base-300": "#121416",       // Darkest background
          "info": "#0DCAF0",           // Info color
          "success": "#198754",        // Success color
          "warning": "#FFC107",        // Warning color
          "error": "#DC3545",          // Error color
        },
      },
      // Keep existing themes if needed
      'nord',
      'coffee',
    ],
  },
};
