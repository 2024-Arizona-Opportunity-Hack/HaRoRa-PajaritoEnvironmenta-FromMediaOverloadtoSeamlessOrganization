/** @type {import('tailwindcss').Config} */
    export default {
      content: ["./src/**/*.{html,js,jsx}"],
      theme: {
        extend: {
          fontFamily: {
            inter: ['"Inter"'], // Add your font here
            grotesk: ['"Schibsted Grotesk"'],
          },
        },
      },
      plugins: [require('daisyui')],
    }
