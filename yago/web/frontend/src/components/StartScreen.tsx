/**
 * YAGO v7.1 - Start Screen Component
 * Initial screen for project idea input
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TemplateSelector } from './TemplateSelector';
import type { TemplateInfo } from '../types/template';

interface StartScreenProps {
  onStart: (projectIdea: string, depth: 'minimal' | 'standard' | 'full', template?: TemplateInfo | null) => void;
  loading?: boolean;
}

export const StartScreen: React.FC<StartScreenProps> = ({ onStart, loading = false }) => {
  const [projectIdea, setProjectIdea] = useState('');
  const [depth, setDepth] = useState<'minimal' | 'standard' | 'full'>('standard');
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'custom' | 'template'>('template');
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateInfo | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // If template tab and template selected, use template's project idea
    if (activeTab === 'template' && selectedTemplate) {
      const templateIdea = `${selectedTemplate.name} - ${selectedTemplate.description || 'Professional template'}`;
      onStart(templateIdea, depth, selectedTemplate);
      return;
    }

    // Otherwise validate custom project idea
    if (projectIdea.trim().length < 10) {
      setError('Please provide at least 10 characters describing your project');
      return;
    }

    if (projectIdea.trim().length > 5000) {
      setError('Project description is too long (max 5000 characters)');
      return;
    }

    setError('');
    onStart(projectIdea.trim(), depth, null);
  };

  const depthOptions = [
    {
      value: 'minimal' as const,
      title: 'Minimal',
      description: '~10 questions, Quick start',
      icon: '⚡',
      time: '3-5 min',
    },
    {
      value: 'standard' as const,
      title: 'Standard',
      description: '~20 questions, Balanced',
      icon: '⚖️',
      time: '8-12 min',
    },
    {
      value: 'full' as const,
      title: 'Full',
      description: '~40+ questions, Comprehensive',
      icon: '🎯',
      time: '15-25 min',
    },
  ];

  const exampleIdeas = [
    'E-commerce platform with Stripe payments and admin dashboard',
    'REST API for task management with JWT authentication',
    'Real-time chat application with WebSocket support',
    'Data analytics dashboard with PostgreSQL and React',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-4xl"
      >
        {/* Hero Section */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-2xl mb-6"
          >
            <span className="text-4xl font-bold text-white">Y</span>
          </motion.div>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Welcome to YAGO v7.1
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            AI-powered development platform that builds production-ready code from your ideas.
            Let's start by understanding your project.
          </p>
        </div>

        {/* Main Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-200 dark:border-gray-700"
        >
          {/* Tab Navigation */}
          <div className="flex gap-2 mb-8 border-b border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={() => setActiveTab('template')}
              className={`px-6 py-3 font-semibold transition-all duration-200 border-b-2 ${
                activeTab === 'template'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              📦 Choose Template
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('custom')}
              className={`px-6 py-3 font-semibold transition-all duration-200 border-b-2 ${
                activeTab === 'custom'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              ✍️ Custom Project
            </button>
          </div>

          {/* Template Tab */}
          {activeTab === 'template' && (
            <div className="mb-8">
              <TemplateSelector
                onSelectTemplate={setSelectedTemplate}
                selectedTemplate={selectedTemplate}
              />
            </div>
          )}

          {/* Custom Project Tab */}
          {activeTab === 'custom' && (
            <form onSubmit={handleSubmit}>
              {/* Project Idea Input */}
            <div className="mb-6">
              <label
                htmlFor="project-idea"
                className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2"
              >
                What would you like to build? <span className="text-red-500">*</span>
              </label>
              <textarea
                id="project-idea"
                value={projectIdea}
                onChange={(e) => {
                  setProjectIdea(e.target.value);
                  setError('');
                }}
                placeholder="Describe your project idea in detail... The more specific you are, the better!"
                rows={6}
                disabled={loading}
                className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 dark:border-gray-600
                         bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                         focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all duration-200 resize-none"
              />
              <div className="flex items-center justify-between mt-2">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {projectIdea.length} / 5000 characters
                </p>
                {error && <p className="text-sm text-red-500">{error}</p>}
              </div>
            </div>

            {/* Example Ideas */}
            <div className="mb-6">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Need inspiration? Try these examples:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {exampleIdeas.map((idea, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setProjectIdea(idea)}
                    disabled={loading}
                    className="text-left px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700
                             hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20
                             text-sm text-gray-600 dark:text-gray-400 hover:text-primary-700 dark:hover:text-primary-300
                             transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    💡 {idea}
                  </button>
                ))}
              </div>
            </div>

            {/* Depth Selection */}
            <div className="mb-8">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                How detailed should the clarification be?
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {depthOptions.map((option) => (
                  <motion.button
                    key={option.value}
                    type="button"
                    onClick={() => setDepth(option.value)}
                    disabled={loading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                      ${
                        depth === option.value
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                      }`}
                  >
                    <div className="text-3xl mb-2">{option.icon}</div>
                    <div className="font-semibold text-gray-900 dark:text-white mb-1">
                      {option.title}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {option.description}
                    </div>
                    <div className="text-xs text-primary-600 dark:text-primary-400 font-medium">
                      {option.time}
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>

          </form>
          )}

          {/* Depth Selection - Common for both tabs */}
          <div className="mb-8 pt-8 border-t border-gray-200 dark:border-gray-700">
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              How detailed should the clarification be?
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {depthOptions.map((option) => (
                <motion.button
                  key={option.value}
                  type="button"
                  onClick={() => setDepth(option.value)}
                  disabled={loading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-4 rounded-xl border-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                    ${
                      depth === option.value
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                    }`}
                >
                  <div className="text-3xl mb-2">{option.icon}</div>
                  <div className="font-semibold text-gray-900 dark:text-white mb-1">
                    {option.title}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {option.description}
                  </div>
                  <div className="text-xs text-primary-600 dark:text-primary-400 font-medium">
                    {option.time}
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Submit Button - Common for both tabs */}
          <motion.button
            type="button"
            onClick={handleSubmit}
            disabled={
              loading ||
              (activeTab === 'custom' && projectIdea.trim().length < 10) ||
              (activeTab === 'template' && !selectedTemplate)
            }
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700
                     hover:from-primary-700 hover:to-primary-800 text-white font-semibold text-lg
                     shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-200 flex items-center justify-center gap-3"
          >
            {loading ? (
              <>
                <svg
                  className="animate-spin h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Starting Clarification...
              </>
            ) : (
              <>
                Start Clarification
                <svg
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </>
            )}
          </motion.button>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center"
        >
          <div className="p-4">
            <div className="text-3xl mb-2">🤖</div>
            <div className="font-semibold text-gray-900 dark:text-white mb-1">
              AI-Powered
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Multiple specialized AI agents work together
            </div>
          </div>

          <div className="p-4">
            <div className="text-3xl mb-2">⚡</div>
            <div className="font-semibold text-gray-900 dark:text-white mb-1">
              Fast Delivery
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Production-ready code in 15-30 minutes
            </div>
          </div>

          <div className="p-4">
            <div className="text-3xl mb-2">✨</div>
            <div className="font-semibold text-gray-900 dark:text-white mb-1">
              90% Success Rate
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              First-time-right delivery with quality
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default StartScreen;
