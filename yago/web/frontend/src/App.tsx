/**
 * YAGO v8.0 - Main Dashboard
 * Modern dashboard showcasing all v8.0 features + Interactive Project Creation
 */

import React, { useState, useEffect, Suspense } from 'react';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ClarificationFlow } from './components/ClarificationFlow';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import { AIModelsTab } from './components/AIModelsTab';
import './i18n/config';
import './index.css';

const App: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'error'>('checking');
  const [activeTab, setActiveTab] = useState<'overview' | 'create' | 'models' | 'analytics' | 'marketplace'>('overview');

  useEffect(() => {
    // Check backend health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(() => setBackendStatus('healthy'))
      .catch(() => setBackendStatus('error'));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-4xl">🚀</div>
              <div>
                <h1 className="text-2xl font-bold text-white">YAGO v8.0</h1>
                <p className="text-sm text-gray-400">Yet Another Genius Orchestrator</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`h-2 w-2 rounded-full ${
                  backendStatus === 'healthy' ? 'bg-green-500 animate-pulse' :
                  backendStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                }`} />
                <span className="text-sm text-gray-300">
                  {backendStatus === 'healthy' ? 'Backend Online' :
                   backendStatus === 'error' ? 'Backend Offline' : 'Checking...'}
                </span>
              </div>

              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition"
              >
                API Docs
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Language Switcher */}
      <div className="fixed top-4 right-4 z-50">
        <LanguageSwitcher />
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="flex space-x-2 bg-black/20 backdrop-blur-sm rounded-lg p-1">
          {[
            { id: 'overview', label: '📊 Overview' },
            { id: 'create', label: '✨ Create Project' },
            { id: 'models', label: '🤖 AI Models' },
            { id: 'analytics', label: '📈 Analytics' },
            { id: 'marketplace', label: '🛒 Marketplace' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 px-4 py-3 rounded-lg text-sm font-medium transition ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <Suspense fallback={<div className="text-white text-center">Loading...</div>}>
            {activeTab === 'overview' && <OverviewTab />}
            {activeTab === 'create' && <ClarificationFlow />}
            {activeTab === 'models' && <AIModelsTab />}
            {activeTab === 'analytics' && <AnalyticsTab />}
            {activeTab === 'marketplace' && <MarketplaceTab />}
          </Suspense>
        </ErrorBoundary>
      </main>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
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
  );
};

// Overview Tab Component
const OverviewTab: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'AI Models', value: '10', icon: '🤖', color: 'from-blue-500 to-cyan-500' },
          { label: 'Active Features', value: '5', icon: '✨', color: 'from-purple-500 to-pink-500' },
          { label: 'API Endpoints', value: '73', icon: '🔌', color: 'from-green-500 to-emerald-500' },
          { label: 'Status', value: 'Ready', icon: '✅', color: 'from-orange-500 to-red-500' },
        ].map((stat, idx) => (
          <div
            key={idx}
            className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:border-white/40 transition"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl">{stat.icon}</span>
              <div className={`text-3xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                {stat.value}
              </div>
            </div>
            <div className="text-gray-400 text-sm">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[
          {
            title: '🤖 AI Model Selection',
            description: '10 pre-configured models with 5 selection strategies',
            features: ['CHEAPEST', 'FASTEST', 'BEST_QUALITY', 'BALANCED', 'CUSTOM'],
          },
          {
            title: '🔄 Auto-Healing System',
            description: 'Automatic error recovery with intelligent strategies',
            features: ['Retry with backoff', 'Circuit breaker', 'Fallback', 'Rollback'],
          },
          {
            title: '📈 Advanced Analytics',
            description: 'Predictive analytics and cost forecasting',
            features: ['Cost prediction', 'Anomaly detection', 'Trend analysis', 'Forecasting'],
          },
          {
            title: '🛒 Marketplace',
            description: 'Community plugins and integrations',
            features: ['Slack', 'GitHub', 'LLM Pipeline', 'Custom Plugins'],
          },
        ].map((feature, idx) => (
          <div
            key={idx}
            className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:border-purple-500/50 transition"
          >
            <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
            <p className="text-gray-400 text-sm mb-4">{feature.description}</p>
            <div className="flex flex-wrap gap-2">
              {feature.features.map((item, i) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-purple-600/20 text-purple-300 text-xs rounded-full border border-purple-500/30"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-xl p-6 border border-purple-500/30">
        <h3 className="text-xl font-bold text-white mb-4">🚀 Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 bg-white/10 rounded-lg hover:bg-white/20 transition text-center"
          >
            <div className="text-2xl mb-2">📚</div>
            <div className="text-white font-medium">View API Docs</div>
            <div className="text-gray-400 text-xs mt-1">73 endpoints</div>
          </a>

          <a
            href="http://localhost:8000/health"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 bg-white/10 rounded-lg hover:bg-white/20 transition text-center"
          >
            <div className="text-2xl mb-2">🏥</div>
            <div className="text-white font-medium">Health Check</div>
            <div className="text-gray-400 text-xs mt-1">System status</div>
          </a>

          <button
            onClick={() => window.location.reload()}
            className="p-4 bg-white/10 rounded-lg hover:bg-white/20 transition text-center"
          >
            <div className="text-2xl mb-2">🔄</div>
            <div className="text-white font-medium">Refresh</div>
            <div className="text-gray-400 text-xs mt-1">Reload page</div>
          </button>
        </div>
      </div>
    </div>
  );
};

// Models Tab (placeholder)
const ModelsTab: React.FC = () => {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 text-center">
      <div className="text-6xl mb-4">🤖</div>
      <h2 className="text-2xl font-bold text-white mb-2">AI Models</h2>
      <p className="text-gray-400 mb-6">Coming soon: Model selection interface</p>
      <a
        href="http://localhost:8000/docs#/Models"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
      >
        View Models API
      </a>
    </div>
  );
};

// Analytics Tab (placeholder)
const AnalyticsTab: React.FC = () => {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 text-center">
      <div className="text-6xl mb-4">📈</div>
      <h2 className="text-2xl font-bold text-white mb-2">Analytics Dashboard</h2>
      <p className="text-gray-400 mb-6">Coming soon: Real-time analytics and metrics</p>
      <a
        href="http://localhost:8000/docs#/Analytics"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
      >
        View Analytics API
      </a>
    </div>
  );
};

// Marketplace Tab (placeholder)
const MarketplaceTab: React.FC = () => {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 text-center">
      <div className="text-6xl mb-4">🛒</div>
      <h2 className="text-2xl font-bold text-white mb-2">Marketplace</h2>
      <p className="text-gray-400 mb-6">Coming soon: Browse plugins and integrations</p>
      <a
        href="http://localhost:8000/docs#/Marketplace"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
      >
        View Marketplace API
      </a>
    </div>
  );
};

export default App;
