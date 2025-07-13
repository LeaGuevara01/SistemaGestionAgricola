// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ command }) => {
  const config = {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  }

  if (command === 'serve') {
    return {
      ...config,
      base: '',
      server: {
        port: 5173,
        strictPort: true,
      },
    }
  } else {
    return {
      ...config,
      base: '/static/dist/',
      build: {
        outDir: '../sistema_gestion_agricola/static/dist',
        manifest: true,
        emptyOutDir: true,
        assetsDir: '.',
        rollupOptions: {
          input: '/src/main.jsx',
        },
      },
    }
  }
})
