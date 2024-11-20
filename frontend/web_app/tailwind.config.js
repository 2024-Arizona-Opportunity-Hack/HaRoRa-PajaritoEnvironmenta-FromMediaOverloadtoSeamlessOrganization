// tailwind.config.js
import daisyui from 'daisyui';

export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: { 
    // Easy Grotesk for the logo and headlines, as well as Inter for body text.
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
      {
        // Formal Dark Theme
        formalDark: {
          "primary": "#fcbf49",        // Light gray for primary actions
          "secondary": "#eae2b7",      // Medium gray for secondary actions
          "accent": "#f77f00",         // Red accent for emphasis
          "neutral": "#eae2b7",        // Dark gray for backgrounds
          "base-100": "#003049",       // Dark background
          "base-200": "#00283e",       // Even darker background
          "base-300": "#002134",       // Darkest background
          "info": "#00ffff",           // Info color
          "success": "#a3e635",        // Success color
          "warning": "#facc15",        // Warning color
          "error": "#d62828",          // Error color
        },
      },
      // Keep existing themes if needed
      'nord',
      'coffee',
    ],
  },
};
