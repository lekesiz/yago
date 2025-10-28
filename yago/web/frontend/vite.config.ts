import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    // Enable code splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks for better caching
          'react-vendor': ['react', 'react-dom'],
          'animation-vendor': ['framer-motion'],
          'ui-vendor': ['react-hot-toast'],
          'http-vendor': ['axios'],
          // Dashboard chunks for lazy loading
          'cost-dashboard': [
            './src/components/CostDashboard',
            './src/components/CostChart',
            './src/components/AgentCostBreakdown',
            './src/components/CostOptimizationSuggestions',
            './src/components/BudgetAlert',
          ],
          'collaboration-dashboard': [
            './src/components/CollaborationDashboard',
            './src/components/AgentStatusPanel',
            './src/components/MessageFlow',
            './src/components/SharedContextView',
            './src/components/ConflictResolver',
          ],
          'benchmark-dashboard': [
            './src/components/BenchmarkDashboard',
            './src/components/BenchmarkResults',
            './src/components/PerformanceTrends',
            './src/components/ComparisonView',
          ],
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Source maps for production debugging
    sourcemap: true,
    // Minify
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
  },
  // Performance optimizations
  optimizeDeps: {
    include: ['react', 'react-dom', 'framer-motion', 'axios', 'react-hot-toast'],
  },
})
