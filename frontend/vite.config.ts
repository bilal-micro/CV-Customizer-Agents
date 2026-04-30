import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/cv-ats/',
  server: {
    proxy: {
      '/cv-ats/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/cv-ats/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/cv-ats/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
