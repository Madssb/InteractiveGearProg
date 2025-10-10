import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    fs: {
      // Allow serving files from one directory up
      allow: ['..']
    }
  },
  resolve: {
    alias: {
      // Optional: alias "data" for convenience
      data: path.resolve(__dirname, '../data'),
      styles: path.resolve(__dirname, '../styles'),
      scripts: path.resolve(__dirname, '../scripts'),
      pages: path.resolve(__dirname, '../src/pages'),
      components: path.resolve(__dirname, '../src/components')
    }
  }
})
