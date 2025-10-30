/**
 * YAGO v8.3 - Error Logs Dashboard with Self-Healing
 * Advanced error tracking, analysis, and auto-fix suggestions
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE = 'http://localhost:8000/api/v1';

interface ErrorLog {
  id: string;
  error_type: string;
  error_message: string;
  stack_trace: string;
  source: 'frontend' | 'backend';
  component: string;
  file_path: string;
  line_number: number;
  severity: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  resolved: boolean;
  created_at: string;
  url: string;
}

interface ErrorStats {
  total_errors: number;
  frontend_errors: number;
  backend_errors: number;
  critical_errors: number;
  unresolved_errors: number;
  common_error_types: Array<{ error_type: string; count: number }>;
}

interface AutoFixSuggestion {
  error_type: string;
  solution: string;
  code_example?: string;
  confidence: 'low' | 'medium' | 'high';
}

export const ErrorLogsDashboard: React.FC = () => {
  const [errors, setErrors] = useState<ErrorLog[]>([]);
  const [stats, setStats] = useState<ErrorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedError, setSelectedError] = useState<ErrorLog | null>(null);
  const [autoFixSuggestions, setAutoFixSuggestions] = useState<AutoFixSuggestion[]>([]);

  // Filters
  const [filterSource, setFilterSource] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterResolved, setFilterResolved] = useState<string>('all');

  useEffect(() => {
    fetchErrors();
    fetchStats();
  }, [filterSource, filterSeverity, filterResolved]);

  const fetchErrors = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filterSource !== 'all') params.source = filterSource;
      if (filterSeverity !== 'all') params.severity = filterSeverity;
      if (filterResolved !== 'all') params.resolved = filterResolved === 'true';

      const response = await axios.get(`${API_BASE}/errors`, { params });
      setErrors(response.data.errors || []);
    } catch (error) {
      toast.error('Failed to fetch errors');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/errors/stats`, {
        params: { hours: 24 }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const resolveError = async (errorId: string) => {
    try {
      await axios.put(`${API_BASE}/errors/${errorId}/resolve`);
      toast.success('Error marked as resolved');
      fetchErrors();
      fetchStats();
    } catch (error) {
      toast.error('Failed to resolve error');
    }
  };

  const analyzeError = (error: ErrorLog): AutoFixSuggestion[] => {
    const suggestions: AutoFixSuggestion[] = [];

    // TypeError analysis
    if (error.error_type === 'TypeError') {
      if (error.error_message.includes('Cannot read propert')) {
        suggestions.push({
          error_type: 'TypeError - Undefined Property',
          solution: 'Add optional chaining (?.) or null check before accessing property',
          code_example: `// Before:\nobj.property\n\n// After:\nobj?.property || defaultValue`,
          confidence: 'high'
        });
      }
      if (error.error_message.includes('undefined or null to object')) {
        suggestions.push({
          error_type: 'TypeError - Object Conversion',
          solution: 'Add safeRender() helper or typeof check',
          code_example: `const safeRender = (val: any) => {\n  if (typeof val === 'string') return val;\n  return JSON.stringify(val);\n}`,
          confidence: 'high'
        });
      }
    }

    // ReferenceError analysis
    if (error.error_type === 'ReferenceError') {
      suggestions.push({
        error_type: 'ReferenceError',
        solution: 'Import missing dependency or define variable',
        code_example: `// Check imports:\nimport { MissingComponent } from './components';`,
        confidence: 'medium'
      });
    }

    // Network errors
    if (error.error_message.includes('Network Error') || error.error_message.includes('CORS')) {
      suggestions.push({
        error_type: 'Network/CORS Error',
        solution: 'Check backend CORS configuration and ensure backend is running',
        code_example: `// Backend (main.py):\napp.add_middleware(\n  CORSMiddleware,\n  allow_origins=["*"]\n)`,
        confidence: 'high'
      });
    }

    // React errors
    if (error.component) {
      suggestions.push({
        error_type: 'Component Error',
        solution: `Check ${error.component} component for rendering issues`,
        code_example: `// Add error boundary:\n<ErrorBoundary>\n  <${error.component} />\n</ErrorBoundary>`,
        confidence: 'medium'
      });
    }

    return suggestions;
  };

  const handleErrorClick = (error: ErrorLog) => {
    setSelectedError(error);
    setAutoFixSuggestions(analyzeError(error));
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'error': return 'text-orange-600 bg-orange-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'info': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">Error Logs & Self-Healing</h2>
          <p className="text-gray-400 mt-1">Monitor, analyze, and auto-fix errors</p>
        </div>
        <button
          onClick={() => { fetchErrors(); fetchStats(); }}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
        >
          Refresh
        </button>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/30 backdrop-blur-sm rounded-xl p-4 border border-blue-500/30">
            <div className="text-blue-400 text-sm mb-1">Total Errors (24h)</div>
            <div className="text-3xl font-bold text-white">{stats.total_errors}</div>
          </div>
          <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/30 backdrop-blur-sm rounded-xl p-4 border border-purple-500/30">
            <div className="text-purple-400 text-sm mb-1">Frontend</div>
            <div className="text-3xl font-bold text-white">{stats.frontend_errors}</div>
          </div>
          <div className="bg-gradient-to-br from-green-900/30 to-green-800/30 backdrop-blur-sm rounded-xl p-4 border border-green-500/30">
            <div className="text-green-400 text-sm mb-1">Backend</div>
            <div className="text-3xl font-bold text-white">{stats.backend_errors}</div>
          </div>
          <div className="bg-gradient-to-br from-red-900/30 to-red-800/30 backdrop-blur-sm rounded-xl p-4 border border-red-500/30">
            <div className="text-red-400 text-sm mb-1">Critical</div>
            <div className="text-3xl font-bold text-white">{stats.critical_errors}</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 backdrop-blur-sm rounded-xl p-4 border border-yellow-500/30">
            <div className="text-yellow-400 text-sm mb-1">Unresolved</div>
            <div className="text-3xl font-bold text-white">{stats.unresolved_errors}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-4 flex-wrap">
        <select
          value={filterSource}
          onChange={(e) => setFilterSource(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
        >
          <option value="all">All Sources</option>
          <option value="frontend">Frontend</option>
          <option value="backend">Backend</option>
        </select>

        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="error">Error</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>

        <select
          value={filterResolved}
          onChange={(e) => setFilterResolved(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
        >
          <option value="all">All Status</option>
          <option value="false">Unresolved</option>
          <option value="true">Resolved</option>
        </select>
      </div>

      {/* Error List & Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Error List */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Error Logs</h3>
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {loading ? (
              <div className="text-gray-400 text-center py-8">Loading...</div>
            ) : errors.length === 0 ? (
              <div className="text-gray-400 text-center py-8">No errors found</div>
            ) : (
              errors.map((error) => (
                <div
                  key={error.id}
                  onClick={() => handleErrorClick(error)}
                  className={`p-4 rounded-lg border cursor-pointer transition ${
                    selectedError?.id === error.id
                      ? 'border-purple-500 bg-purple-900/20'
                      : 'border-gray-700 bg-gray-900/50 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${getSeverityColor(error.severity)}`}>
                          {error.severity.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{error.source}</span>
                        {error.resolved && (
                          <span className="text-xs text-green-500">✓ Resolved</span>
                        )}
                      </div>
                      <div className="text-white font-medium text-sm">{error.error_type}</div>
                      <div className="text-gray-400 text-xs mt-1 truncate">{error.error_message}</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{error.component || 'Unknown component'}</span>
                    <span>{new Date(error.created_at).toLocaleString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Error Details & Auto-Fix */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Error Details & Auto-Fix</h3>

          {selectedError ? (
            <div className="space-y-4">
              {/* Error Info */}
              <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-white font-bold">{selectedError.error_type}</h4>
                  {!selectedError.resolved && (
                    <button
                      onClick={() => resolveError(selectedError.id)}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition"
                    >
                      Mark Resolved
                    </button>
                  )}
                </div>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-400">Message:</span>
                    <p className="text-white mt-1">{selectedError.error_message}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Location:</span>
                    <p className="text-white mt-1">
                      {selectedError.file_path}
                      {selectedError.line_number && `:${selectedError.line_number}`}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400">Component:</span>
                    <p className="text-white mt-1">{selectedError.component || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">URL:</span>
                    <p className="text-white mt-1 text-xs truncate">{selectedError.url}</p>
                  </div>
                </div>

                {/* Stack Trace */}
                {selectedError.stack_trace && (
                  <details className="mt-3">
                    <summary className="text-gray-400 cursor-pointer text-sm">Stack Trace</summary>
                    <pre className="mt-2 text-xs text-gray-300 bg-black/30 p-3 rounded overflow-x-auto">
                      {selectedError.stack_trace}
                    </pre>
                  </details>
                )}
              </div>

              {/* Auto-Fix Suggestions */}
              {autoFixSuggestions.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-white font-bold flex items-center gap-2">
                    <span>🤖</span>
                    Auto-Fix Suggestions
                  </h4>
                  {autoFixSuggestions.map((suggestion, idx) => (
                    <div
                      key={idx}
                      className={`rounded-lg p-4 border ${
                        suggestion.confidence === 'high'
                          ? 'border-green-500/50 bg-green-900/20'
                          : suggestion.confidence === 'medium'
                          ? 'border-yellow-500/50 bg-yellow-900/20'
                          : 'border-gray-500/50 bg-gray-900/20'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium text-sm">{suggestion.error_type}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          suggestion.confidence === 'high'
                            ? 'bg-green-600 text-white'
                            : suggestion.confidence === 'medium'
                            ? 'bg-yellow-600 text-white'
                            : 'bg-gray-600 text-white'
                        }`}>
                          {suggestion.confidence} confidence
                        </span>
                      </div>
                      <p className="text-gray-300 text-sm mb-2">{suggestion.solution}</p>
                      {suggestion.code_example && (
                        <pre className="text-xs text-gray-300 bg-black/30 p-3 rounded overflow-x-auto">
                          {suggestion.code_example}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-400 text-center py-12">
              Select an error to view details and auto-fix suggestions
            </div>
          )}
        </div>
      </div>

      {/* Common Error Types */}
      {stats && stats.common_error_types.length > 0 && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Most Common Errors</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {stats.common_error_types.slice(0, 6).map((type, idx) => (
              <div key={idx} className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
                <div className="text-white font-medium text-sm mb-1">{type.error_type}</div>
                <div className="text-2xl font-bold text-purple-400">{type.count}</div>
                <div className="text-gray-500 text-xs mt-1">occurrences</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
