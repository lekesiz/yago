/**
 * YAGO v8.0 - Analytics Tab Component
 */
import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

export const AnalyticsTab: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [modelsUsage, setModelsUsage] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/api/v1/analytics/metrics').then(r => r.json()),
      fetch('http://localhost:8000/api/v1/analytics/models-usage').then(r => r.json())
    ])
    .then(([metricsData, usageData]) => {
      setMetrics(metricsData);
      setModelsUsage(usageData.models || []);
    })
    .catch(() => toast.error('Failed to load analytics'))
    .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-white text-center py-8">Loading analytics...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Analytics</h2>
        <p className="text-gray-400">Performance metrics and usage statistics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { label: 'Total Requests', value: metrics?.total_requests?.toLocaleString(), icon: '📊', color: 'from-blue-500 to-cyan-500' },
          { label: 'Total Tokens', value: metrics?.total_tokens?.toLocaleString(), icon: '🔢', color: 'from-purple-500 to-pink-500' },
          { label: 'Total Cost', value: `$${metrics?.total_cost}`, icon: '💰', color: 'from-green-500 to-emerald-500' },
          { label: 'Avg Latency', value: `${metrics?.avg_latency_ms}ms`, icon: '⚡', color: 'from-yellow-500 to-orange-500' },
          { label: 'Success Rate', value: `${metrics?.success_rate}%`, icon: '✅', color: 'from-green-500 to-teal-500' },
          { label: 'Active Users', value: metrics?.active_users, icon: '👥', color: 'from-indigo-500 to-purple-500' }
        ].map((metric, idx) => (
          <div key={idx} className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl">{metric.icon}</span>
              <div className={`text-2xl font-bold bg-gradient-to-r ${metric.color} bg-clip-text text-transparent`}>
                {metric.value}
              </div>
            </div>
            <div className="text-gray-400 text-sm">{metric.label}</div>
          </div>
        ))}
      </div>

      {/* Models Usage */}
      <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
        <h3 className="text-xl font-bold text-white mb-4">Usage by Model</h3>
        <div className="space-y-3">
          {modelsUsage.map((model) => (
            <div key={model.model_id} className="bg-black/20 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">{model.model_name}</span>
                <span className="text-sm text-gray-400">{model.percentage}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" style={{width: `${model.percentage}%`}}></div>
              </div>
              <div className="grid grid-cols-3 gap-4 text-xs text-gray-400">
                <div>Requests: <span className="text-white">{model.requests.toLocaleString()}</span></div>
                <div>Tokens: <span className="text-white">{model.tokens.toLocaleString()}</span></div>
                <div>Cost: <span className="text-white">${model.cost}</span></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
