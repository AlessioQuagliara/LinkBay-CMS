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
    port: 3003
  }
})