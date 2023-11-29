import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  plugins: [ vue() ],
  build: {
    outDir: "./dist",
    emptyOutDir: true,
  },
  base: "/",
  server: {
    host: "0.0.0.0",
    hmr: {
      clientPort: 3000,
    },
    port: 3000,
    watch: {
      usePolling: true,
    },
  },
})
