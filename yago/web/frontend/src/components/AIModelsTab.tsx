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

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/models/list')
      .then(res => res.json())
      .then(data => setModels(data.models || []))
      .catch(() => toast.error('Failed to load models'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-white text-center py-8">Loading models...</div>;

  const getProviderIcon = (provider: string) => ({ openai: '🤖', anthropic: '🧠', google: '🔮' }[provider] || '⚡');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">AI Models</h2>
        <p className="text-gray-400">{models.length} models available</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {models.map((model) => (
          <div key={model.id} className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10 hover:border-purple-500 transition">
            <div className="flex items-center space-x-3 mb-4">
              <div className="text-3xl">{getProviderIcon(model.provider)}</div>
              <div>
                <h3 className="font-bold text-white">{model.name}</h3>
                <p className="text-xs text-gray-400 capitalize">{model.provider}</p>
              </div>
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
