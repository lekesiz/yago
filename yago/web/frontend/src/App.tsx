/**
 * YAGO v7.1 - Root Application Component
 * Main entry point for the React application
 */

import React from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ClarificationFlow } from './components/ClarificationFlow';
import './index.css';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <div className="app">
        <ClarificationFlow />
      </div>
    </ErrorBoundary>
  );
};

export default App;
