/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,ts}",
  ],
  theme: {
    extend: {
      colors: {
        "main": {
          "000": "var(--main-000)",
          "100": "var(--main-100)",
          "200": "var(--main-200)",
          "300": "var(--main-300)",
          "400": "var(--main-400)",
          "500": "var(--main-500)",
          "600": "var(--main-600)",
          "700": "var(--main-700)",
          "800": "var(--main-800)",
          "900": "var(--main-900)",
        },
        "calendar": {
          "available": "var(--calendar-available)",  // green
          "unavailable": "var(--calendar-unavailable)",  // red
          "default": "var(--main-200)",  // default
          "disabled": "var(--main-100)", // disabled
        },
        "invalid": {
          "light": "#ecd2d2",
          "normal": "#e4c0c0",
          "dark": "#dcaeae",
        }
      },
      gridTemplateRows: {
        '24': 'repeat(24, minmax(0, 1fr))',
      },
    },
  },
  plugins: [],
}

