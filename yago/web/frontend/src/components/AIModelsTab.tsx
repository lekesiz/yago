/**
 * YAGO v8.0 - AI Models Tab Component
 */
import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

interface AIModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  cost_per_1k_input: number;
  speed_score: number;
  quality_score: number;
  status: string;
}

export const AIModelsTab: React.FC = () => {
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([]);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [filterProvider, setFilterProvider] = useState<string>('all');

  useEffect(() => {
    loadModels();
  }, [filterProvider]);

  const loadModels = () => {
    const url = filterProvider === 'all'
      ? 'http://localhost:8000/api/v1/models/list'
      : `http://localhost:8000/api/v1/models/list?provider=${filterProvider}`;

    fetch(url)
      .then(res => res.json())
      .then(data => setModels(data.models || []))
      .catch(() => toast.error('Failed to load models'))
      .finally(() => setLoading(false));
  };

  const toggleModelSelection = (modelId: string) => {
    if (selectedForComparison.includes(modelId)) {
      setSelectedForComparison(selectedForComparison.filter(id => id !== modelId));
    } else if (selectedForComparison.length < 4) {
      setSelectedForComparison([...selectedForComparison, modelId]);
    } else {
      toast.error('Maximum 4 models can be compared');
    }
  };

  const getComparisonData = () => {
    return models.filter(m => selectedForComparison.includes(m.id));
  };

  if (loading) return <div className="text-white text-center py-8">Loading models...</div>;

  const getProviderIcon = (provider: string) => ({
    openai: '🟢',
    anthropic: '🔵',
    google: '🔴',
    cursor: '⚡'
  }[provider] || '🤖');

  const providers = ['all', ...Array.from(new Set(models.map(m => m.provider)))];

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">🤖 AI Models</h2>
          <p className="text-gray-400">{models.length} models available</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => {
              setComparisonMode(!comparisonMode);
              if (comparisonMode) setSelectedForComparison([]);
            }}
            className={`px-4 py-2 rounded-lg transition font-medium ${
              comparisonMode
                ? 'bg-purple-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            {comparisonMode ? `Compare (${selectedForComparison.length})` : '📊 Compare Models'}
          </button>
        </div>
      </div>

      {/* Provider Filter */}
      <div className="flex gap-2 overflow-x-auto">
        {providers.map(provider => (
          <button
            key={provider}
            onClick={() => setFilterProvider(provider)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap transition ${
              filterProvider === provider
                ? 'bg-purple-600 text-white'
                : 'bg-white/10 text-gray-400 hover:bg-white/20'
            }`}
          >
            {provider === 'all' ? 'All Providers' : provider.charAt(0).toUpperCase() + provider.slice(1)}
          </button>
        ))}
      </div>

      {/* Comparison View */}
      {comparisonMode && selectedForComparison.length > 0 && (
        <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-xl p-6 border border-purple-500/30">
          <h3 className="text-xl font-bold text-white mb-4">📊 Model Comparison</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {getComparisonData().map(model => (
              <div key={model.id} className="bg-white/10 rounded-lg p-4">
                <div className="text-2xl mb-2">{getProviderIcon(model.provider)}</div>
                <h4 className="font-bold text-white text-sm mb-3">{model.name}</h4>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Speed:</span>
                    <span className="text-white font-medium">{model.speed_score}/10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Quality:</span>
                    <span className="text-white font-medium">{model.quality_score}/10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Cost/1K:</span>
                    <span className="text-white font-medium">${model.cost_per_1k_input.toFixed(4)}</span>
                  </div>
                </div>
                <button
                  onClick={() => toggleModelSelection(model.id)}
                  className="w-full mt-3 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => {
                const best = getComparisonData().reduce((prev, curr) =>
                  curr.quality_score > prev.quality_score ? curr : prev
                );
                toast.success(`Best Quality: ${best.name}`);
              }}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition"
            >
              🏆 Best Quality
            </button>
            <button
              onClick={() => {
                const fastest = getComparisonData().reduce((prev, curr) =>
                  curr.speed_score > prev.speed_score ? curr : prev
                );
                toast.success(`Fastest: ${fastest.name}`);
              }}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition"
            >
              ⚡ Fastest
            </button>
            <button
              onClick={() => {
                const cheapest = getComparisonData().reduce((prev, curr) =>
                  curr.cost_per_1k_input < prev.cost_per_1k_input ? curr : prev
                );
                toast.success(`Cheapest: ${cheapest.name}`);
              }}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded-lg transition"
            >
              💰 Cheapest
            </button>
          </div>
        </div>
      )}

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {models.map((model) => (
          <div
            key={model.id}
            className={`bg-white/5 backdrop-blur-sm rounded-lg p-6 border transition cursor-pointer ${
              selectedForComparison.includes(model.id)
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-white/10 hover:border-purple-500'
            }`}
            onClick={() => comparisonMode && toggleModelSelection(model.id)}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="text-3xl">{getProviderIcon(model.provider)}</div>
                <div>
                  <h3 className="font-bold text-white">{model.name}</h3>
                  <p className="text-xs text-gray-400 capitalize">{model.provider}</p>
                </div>
              </div>
              {comparisonMode && (
                <input
                  type="checkbox"
                  checked={selectedForComparison.includes(model.id)}
                  onChange={() => toggleModelSelection(model.id)}
                  className="w-5 h-5 rounded border-gray-300"
                  onClick={(e) => e.stopPropagation()}
                />
              )}
            </div>
            <p className="text-sm text-gray-400 mb-4">{model.description}</p>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="bg-black/20 rounded p-2">
                <div className="text-xs text-gray-400">Speed</div>
                <div className="font-bold text-green-400">{model.speed_score}/10</div>
              </div>
              <div className="bg-black/20 rounded p-2">
                <div className="text-xs text-gray-400">Quality</div>
                <div className="font-bold text-blue-400">{model.quality_score}/10</div>
              </div>
            </div>
            <div className="mt-3 text-xs text-gray-400">
              Cost: <span className="text-white font-bold">${model.cost_per_1k_input.toFixed(4)}/1K</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
