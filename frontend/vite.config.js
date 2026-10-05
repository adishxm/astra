import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function emitDistIndexPlugin() {
  return {
    name: 'emit-dist-index',
    closeBundle() {
      const distReactPath = path.resolve(__dirname, 'dist/react.html');
      const distIndexPath = path.resolve(__dirname, 'dist/index.html');
      if (fs.existsSync(distReactPath)) {
        fs.copyFileSync(distReactPath, distIndexPath);
        fs.unlinkSync(distReactPath);
      }
    },
  };
}

export default defineConfig({
  base: '/static/',
  plugins: [react(), emitDistIndexPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'react.html'),
      },
    },
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url || '';
        if (
          !url.includes('.') &&
          !url.startsWith('/api') &&
          !url.startsWith('/@') &&
          !url.startsWith('/node_modules')
        ) {
          req.url = '/react.html';
        }
        next();
      });
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    css: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/components/**', 'src/api/**', 'src/hooks/**', 'src/pages/**'],
      exclude: ['src/test/**', 'src/dev/**', 'src/**/*.test.{js,jsx}', 'src/**/*.spec.{js,jsx}'],
    },
  },
});
