import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [
      react(),
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
        manifest: {
          name: 'AI Agent SDK Dashboard',
          short_name: 'Agent SDK',
          description: 'Developer dashboard for AI agent coordination',
          theme_color: '#3b82f6',
          background_color: '#ffffff',
          display: 'standalone',
          orientation: 'portrait',
          scope: '/',
          start_url: '/',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            }
          ]
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/api\.ai-agent-sdk\.com\/.*/i,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 * 24 // 24 hours
                }
              }
            }
          ]
        }
      })
    ],
    server: {
      port: 3000,
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        },
        '/ws': {
          target: env.VITE_WS_URL || 'ws://localhost:8080',
          ws: true,
          changeOrigin: true
        }
      }
    },
    build: {
      target: 'es2020',
      outDir: 'dist',
      sourcemap: mode === 'development',
      rollupOptions: {
        output: {
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
          manualChunks: {
            'react-vendor': ['react', 'react-dom'],
            'antd-vendor': ['antd', '@ant-design/icons'],
            'chart-vendor': ['@ant-design/charts'],
            'utils': ['lodash', 'dayjs', 'axios']
          }
        }
      },
      chunkSizeWarningLimit: 1500,
      assetsInlineLimit: 4096
    },
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString())
    },
    resolve: {
      alias: {
        '@': resolve(__dirname, './src'),
        '@components': resolve(__dirname, './src/components'),
        '@hooks': resolve(__dirname, './src/hooks'),
        '@utils': resolve(__dirname, './src/utils'),
        '@types': resolve(__dirname, './src/types'),
        '@stores': resolve(__dirname, './src/stores'),
        '@services': resolve(__dirname, './src/services'),
        '@styles': resolve(__dirname, './src/styles')
      }
    }
  };
});