/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,ts}",
  ],
  theme: {
    extend: {
      colors: {
        "main": "#41B9D6",
        "header": "#b7e1eb",
        "background": {
          "main": "#f2feff",
        },
      },
    },
  },
  plugins: [],
}

