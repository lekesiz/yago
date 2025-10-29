/**
 * YAGO v8.0 - Root Application Component
 * Main entry point for the React application with i18n support
 */

import React, { Suspense } from 'react';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ClarificationFlow } from './components/ClarificationFlow';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import './i18n/config'; // Initialize i18n
import './index.css';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading...</div>}>
        <div className="app">
          {/* Language Switcher */}
          <div className="fixed top-4 right-4 z-50">
            <LanguageSwitcher />
          </div>

          <ClarificationFlow />
          <Toaster
            position="top-right"
            toastOptions={{
              // Default options
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              // Success
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              // Error
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </div>
      </Suspense>
    </ErrorBoundary>
  );
};

export default App;
