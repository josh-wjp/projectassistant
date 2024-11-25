import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: resolve(__dirname, '../static'), // Set the absolute path
    emptyOutDir: true,
    sourcemap: true
  },
  server: {
    proxy: {
      '/ask': 'http://localhost:5000',
      '/chat': 'http://localhost:5000'
    }
  }
});
