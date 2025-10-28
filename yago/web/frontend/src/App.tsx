/**
 * YAGO v8.0 - Test Mode
 * Simplified version to debug white screen issue
 */

import React from 'react';
import './index.css';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="max-w-4xl mx-auto p-8">
        <div className="bg-white rounded-2xl shadow-2xl p-12 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🚀 YAGO v8.0
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Yet Another Genius Orchestrator
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="p-6 bg-blue-50 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                ✅ Backend Status
              </h3>
              <p className="text-blue-700">Running on port 8000</p>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 inline-block text-blue-600 hover:text-blue-800 underline"
              >
                View API Docs
              </a>
            </div>

            <div className="p-6 bg-green-50 rounded-lg">
              <h3 className="text-lg font-semibold text-green-900 mb-2">
                ✅ Frontend Status
              </h3>
              <p className="text-green-700">Running on port 3000</p>
              <p className="text-sm text-green-600 mt-1">React + TypeScript + Vite</p>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-yellow-800">
              <strong>Test Mode:</strong> This is a simplified version to verify the frontend is working.
            </p>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => alert('Button clicked! React is working!')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
            >
              Test React Interaction
            </button>

            <a
              href="http://localhost:8000/health"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 text-center"
            >
              Check Backend Health
            </a>
          </div>

          <div className="mt-8 text-sm text-gray-500">
            <p>All systems operational 🎉</p>
            <p className="mt-1">Full UI will be restored after testing</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
