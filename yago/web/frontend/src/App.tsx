/**
 * YAGO v7.1 - Root Application Component
 * Main entry point for the React application
 */

import React from 'react';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ClarificationFlow } from './components/ClarificationFlow';
import './index.css';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <div className="app">
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
    </ErrorBoundary>
  );
};

export default App;
