import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // Required for Docker - bind to all interfaces
    port: 5173,
    watch: {
      usePolling: true, // Required for Docker file watching
    },
    hmr: {
      clientPort: 5173, // Explicit port for HMR WebSocket
    },
    proxy: {
      // Proxy API requests to FastAPI backend (use Docker service name)
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        followRedirects: true,
        configure: (proxy, _options) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // Rewrite location header to use localhost instead of backend
            const location = proxyRes.headers['location'];
            if (location && location.includes('backend:8000')) {
              proxyRes.headers['location'] = location.replace('backend:8000', 'localhost:5173/api');
            }
          });
        },
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
