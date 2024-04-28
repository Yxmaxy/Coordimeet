import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import mkcert from 'vite-plugin-mkcert'

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "@": "/src"
    }
  },
  plugins: [
    vue(),
    VitePWA({
      srcDir: "src",
      filename: "sw.ts",
      injectRegister: null,
      strategies: "injectManifest",
      registerType: "autoUpdate",
      injectManifest: {
        globPatterns: [
          "**/*.{js,css,html,png,svg}",
        ],
      },
      manifest: {
        name: "CoordiMeet",
        short_name: "CoordiMeet",
        theme_color: "#b3e3ee",
        display: "standalone",
        background_color: "#b3e3ee",
        icons: [
          {
            src: "/images/maskable_icon_x192.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "/images/maskable_icon_x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      devOptions: {
        enabled: true,
        type: "module",
      },
    }),
    // mkcert(),
  ],
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
