import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable Fast Refresh
      fastRefresh: true,
    }),
    // Gzip compression
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240, // Only compress files > 10KB
      algorithm: 'gzip',
      ext: '.gz',
    }),
    // Brotli compression
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240,
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
    // Bundle analyzer (only in analyze mode)
    process.env.ANALYZE &&
      visualizer({
        open: true,
        gzipSize: true,
        brotliSize: true,
        filename: 'dist/stats.html',
      }),
  ].filter(Boolean),
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
        // Manual chunks for better caching and loading
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            // React core
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor';
            }
            // UI libraries
            if (id.includes('framer-motion')) {
              return 'animation-vendor';
            }
            if (id.includes('react-hot-toast')) {
              return 'ui-vendor';
            }
            if (id.includes('axios')) {
              return 'http-vendor';
            }
            if (id.includes('recharts')) {
              return 'charts-vendor';
            }
            if (id.includes('i18next')) {
              return 'i18n-vendor';
            }
            // All other node_modules
            return 'vendor';
          }

          // Component chunks
          if (id.includes('/src/components/')) {
            if (id.includes('Cost') || id.includes('Budget')) {
              return 'cost-features';
            }
            if (id.includes('Collaboration') || id.includes('Message') || id.includes('Agent')) {
              return 'collaboration-features';
            }
            if (id.includes('Benchmark') || id.includes('Performance')) {
              return 'benchmark-features';
            }
            if (id.includes('Analytics') || id.includes('Chart')) {
              return 'analytics-features';
            }
            if (id.includes('Marketplace')) {
              return 'marketplace-features';
            }
          }
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Source maps for production debugging (hidden from browser)
    sourcemap: 'hidden',
    // Minify with terser
    minify: 'terser',
    terserOptions: {
      compress: {
        // Remove console.log and debugger in production
        drop_console: true,
        drop_debugger: true,
        // Remove unused code
        dead_code: true,
        // Evaluate constant expressions
        evaluate: true,
        // Join consecutive var statements
        join_vars: true,
        // Optimize loops
        loops: true,
        // Remove unreachable code
        unused: true,
      },
      mangle: {
        // Mangle variable names for smaller size
        safari10: true,
      },
      format: {
        // Remove comments
        comments: false,
      },
    },
    // Optimize CSS
    cssCodeSplit: true,
    cssMinify: true,
    // Target modern browsers for smaller bundle
    target: 'es2015',
    // Optimize assets
    assetsInlineLimit: 4096, // Inline assets < 4KB
    // Report compressed size
    reportCompressedSize: true,
  },
  // Performance optimizations
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'framer-motion',
      'axios',
      'react-hot-toast',
      'recharts',
      'i18next',
      'react-i18next',
    ],
    // Exclude large deps that don't need pre-bundling
    exclude: [],
  },
  // Resolve aliases for shorter imports
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@utils': '/src/utils',
      '@services': '/src/services',
      '@types': '/src/types',
    },
  },
  // Preview server config
  preview: {
    port: 3000,
  },
})
