import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '')
  
  const port = parseInt(env.AI_MESSAGE_FRONTEND_PORT || '3000', 10)
  const useSSL = env.AI_MESSAGE_FRONTEND_SSL === 'true'
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port,
      https: useSSL ? {
        cert: env.AI_MESSAGE_SSL_CERT,
        key: env.AI_MESSAGE_SSL_KEY
      } : undefined,
      proxy: {
        '/api': {
          target: `http://${env.AI_MESSAGE_HOST || 'localhost'}:${env.AI_MESSAGE_PORT || '8000'}`,
          changeOrigin: true
        }
      }
    }
  }
})