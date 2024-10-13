// tailwind.config.js
import daisyui from 'daisyui';

export default {
    content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
    theme: { extend: {} },
    plugins: [require('daisyui')],
    daisyui: {
        themes: ['nord', 'luxury'],
    },
};