import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve('./src'),
      '@shared': resolve('../shared')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3003,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'app.linkbay-cms.local',
      'demo.linkbay-cms.local',
      'lyarasrl.linkbay-cms.local',
      'linkbay-cms.local',
      'auth.linkbay-cms.local',
      'api.linkbay-cms.local'
    ],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3000',
        changeOrigin: true
      }
    }
  }
})