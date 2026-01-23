import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "client", "src"),
      "@shared": path.resolve(__dirname, "shared"),
      "@assets": path.resolve(__dirname, "client", "public", "assets"),
    },
  },
  root: path.resolve(__dirname, "client"),
  server: {
    port: 3002,
    proxy: {
      '/api/v1': {
        target: process.env.VITE_API_URL || 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: path.resolve(__dirname, "dist"),
    emptyOutDir: true,
  },
});
