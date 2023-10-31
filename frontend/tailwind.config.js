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
        "text": "#061215",
        "calendar": {
          "in-range": "#eaf1f7",
          "available": "#bff1bf",
          "unavailable": "#e4c0c0",
          "non-selected": "#f7fafc",
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

