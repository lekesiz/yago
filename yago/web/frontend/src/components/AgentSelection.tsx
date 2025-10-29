/**
 * YAGO v8.0 - Agent Selection Page
 * Allows users to select AI models and configure agents for their project
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import axios from 'axios';

interface AgentSelectionProps {
  brief: any;
  onComplete: (config: ProjectConfig) => void;
  onBack: () => void;
}

interface AIModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  cost_per_1k_input: number;
  cost_per_1k_output: number;
  context_window: number;
  speed_score: number;
  quality_score: number;
  capabilities: string[];
  enabled: boolean;
}

interface ProjectConfig {
  brief: any;
  primary_model: string;
  fallback_model: string;
  agent_role: string;
  temperature: number;
  max_tokens: number;
  strategy: string;
}

const agentRoles = [
  { id: 'full_stack', name: 'Full Stack Developer', icon: '💻', description: 'End-to-end development' },
  { id: 'backend', name: 'Backend Developer', icon: '⚙️', description: 'API & server-side logic' },
  { id: 'frontend', name: 'Frontend Developer', icon: '🎨', description: 'UI/UX implementation' },
  { id: 'architect', name: 'Software Architect', icon: '🏗️', description: 'System design & planning' },
  { id: 'devops', name: 'DevOps Engineer', icon: '🚀', description: 'Infrastructure & deployment' },
];

const strategies = [
  { id: 'balanced', name: 'Balanced', description: 'Good quality, reasonable cost' },
  { id: 'cheapest', name: 'Cost Optimized', description: 'Minimize costs' },
  { id: 'fastest', name: 'Speed Optimized', description: 'Fastest responses' },
  { id: 'best_quality', name: 'Quality First', description: 'Best possible results' },
];

export const AgentSelection: React.FC<AgentSelectionProps> = ({ brief, onComplete, onBack }) => {
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [fallbackModel, setFallbackModel] = useState<string>('');
  const [agentRole, setAgentRole] = useState<string>('full_stack');
  const [strategy, setStrategy] = useState<string>('balanced');
  const [temperature, setTemperature] = useState<number>(0.7);
  const [maxTokens, setMaxTokens] = useState<number>(4000);
  const [filterProvider, setFilterProvider] = useState<string>('all');

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/models/list');
      setModels(response.data.models || []);

      // Auto-select first model
      if (response.data.models.length > 0) {
        setSelectedModel(response.data.models[0].id);
        if (response.data.models.length > 1) {
          setFallbackModel(response.data.models[1].id);
        }
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to load models:', error);
      toast.error('Failed to load AI models');
      setLoading(false);
    }
  };

  const handleStartProject = () => {
    if (!selectedModel) {
      toast.error('Please select a primary AI model');
      return;
    }

    const config: ProjectConfig = {
      brief,
      primary_model: selectedModel,
      fallback_model: fallbackModel,
      agent_role: agentRole,
      temperature,
      max_tokens: maxTokens,
      strategy,
    };

    toast.success('🚀 Starting your project!');
    onComplete(config);
  };

  const filteredModels = filterProvider === 'all'
    ? models
    : models.filter(m => m.provider === filterProvider);

  const providers = ['all', ...Array.from(new Set(models.map(m => m.provider)))];

  const getSelectedModelInfo = () => {
    return models.find(m => m.id === selectedModel);
  };

  const estimatedCost = () => {
    const model = getSelectedModelInfo();
    if (!model) return 0;
    // Rough estimate: 10k input tokens, 5k output tokens
    return ((10 * model.cost_per_1k_input) + (5 * model.cost_per_1k_output)).toFixed(2);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                🤖 Agent Selection
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Choose your AI agents and configure your project
              </p>
            </div>
            <button
              onClick={onBack}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition"
            >
              ← Back
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Agent Role Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                👤 Select Agent Role
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agentRoles.map((role) => (
                  <button
                    key={role.id}
                    onClick={() => setAgentRole(role.id)}
                    className={`p-4 rounded-lg border-2 transition text-left ${
                      agentRole === role.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="text-3xl mb-2">{role.icon}</div>
                    <div className="font-semibold text-gray-900 dark:text-white">{role.name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{role.description}</div>
                  </button>
                ))}
              </div>
            </motion.div>

            {/* AI Model Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                🧠 Select AI Model
              </h2>

              {/* Provider Filter */}
              <div className="flex gap-2 mb-4 overflow-x-auto">
                {providers.map((provider) => (
                  <button
                    key={provider}
                    onClick={() => setFilterProvider(provider)}
                    className={`px-4 py-2 rounded-lg whitespace-nowrap transition ${
                      filterProvider === provider
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    {provider === 'all' ? 'All' : provider.charAt(0).toUpperCase() + provider.slice(1)}
                  </button>
                ))}
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
                  <p className="text-gray-600 dark:text-gray-400 mt-4">Loading models...</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {filteredModels.map((model) => (
                    <button
                      key={model.id}
                      onClick={() => setSelectedModel(model.id)}
                      className={`w-full p-4 rounded-lg border-2 transition text-left ${
                        selectedModel === model.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900 dark:text-white">{model.name}</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{model.description}</div>
                          <div className="flex gap-4 mt-2 text-xs text-gray-500 dark:text-gray-500">
                            <span>⚡ Speed: {model.speed_score}/10</span>
                            <span>⭐ Quality: {model.quality_score}/10</span>
                            <span>💰 ${model.cost_per_1k_input}/1K in</span>
                          </div>
                        </div>
                        {selectedModel === model.id && (
                          <div className="ml-4">
                            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </motion.div>

            {/* Strategy Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                ⚙️ Optimization Strategy
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {strategies.map((strat) => (
                  <button
                    key={strat.id}
                    onClick={() => setStrategy(strat.id)}
                    className={`p-4 rounded-lg border-2 transition text-left ${
                      strategy === strat.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="font-semibold text-gray-900 dark:text-white">{strat.name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{strat.description}</div>
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Advanced Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                🎛️ Advanced Settings
              </h2>

              {/* Temperature */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Temperature: {temperature.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-500 mt-1">
                  <span>Precise</span>
                  <span>Creative</span>
                </div>
              </div>

              {/* Max Tokens */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Tokens: {maxTokens}
                </label>
                <input
                  type="range"
                  min="1000"
                  max="8000"
                  step="500"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-500 mt-1">
                  <span>Short</span>
                  <span>Long</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Right: Summary & Actions */}
          <div className="space-y-6">
            {/* Project Summary */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 sticky top-4"
            >
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                📋 Project Summary
              </h3>

              <div className="space-y-3 text-sm">
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Project Idea</div>
                  <div className="text-gray-900 dark:text-white font-medium">{brief?.project_idea || 'N/A'}</div>
                </div>

                <div>
                  <div className="text-gray-500 dark:text-gray-400">Primary Model</div>
                  <div className="text-gray-900 dark:text-white font-medium">
                    {getSelectedModelInfo()?.name || 'Not selected'}
                  </div>
                </div>

                <div>
                  <div className="text-gray-500 dark:text-gray-400">Agent Role</div>
                  <div className="text-gray-900 dark:text-white font-medium">
                    {agentRoles.find(r => r.id === agentRole)?.name}
                  </div>
                </div>

                <div>
                  <div className="text-gray-500 dark:text-gray-400">Strategy</div>
                  <div className="text-gray-900 dark:text-white font-medium">
                    {strategies.find(s => s.id === strategy)?.name}
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-gray-500 dark:text-gray-400">Estimated Cost</div>
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    ${estimatedCost()}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">per session (estimated)</div>
                </div>
              </div>

              <button
                onClick={handleStartProject}
                disabled={!selectedModel}
                className="w-full mt-6 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🚀 Start Project
              </button>

              <button
                onClick={onBack}
                className="w-full mt-3 px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
              >
                ← Back to Brief
              </button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentSelection;
