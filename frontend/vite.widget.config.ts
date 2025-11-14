import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// Configuración específica para build del widget standalone
export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/widget-entry.tsx'),
      name: 'ChatbotWidget',
      fileName: 'widget',
      formats: ['iife'], // IIFE para uso en browsers sin bundler
    },
    rollupOptions: {
      output: {
        // Inline todo en un solo archivo
        inlineDynamicImports: true,
        assetFileNames: 'widget.[ext]',
      },
    },
    outDir: 'dist-widget',
  },
  server: {
    port: 5176,
  },
  // Configurar public dir para servir demo.html
  publicDir: 'public',
});
