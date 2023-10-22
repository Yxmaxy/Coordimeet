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
          "100": "#d9f1f6",
          "200": "#b3e3ee",
          "300": "#8dd5e6",
          "400": "#66c7de",
          "500": "#41b9d6",
          "600": "#3494ab",
          "700": "#276f80",
          "800": "#1a4a55",
          "900": "#0d252a",
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

