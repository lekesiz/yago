/**
 * YAGO v7.1 - Template Selector Component
 * Allows users to browse and select project templates
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { TemplateCard } from './TemplateCard';
import { templateApi } from '../services/templateApi';
import type { TemplateInfo, TemplateCategory } from '../types/template';

interface TemplateSelectorProps {
  onSelectTemplate: (template: TemplateInfo | null) => void;
  selectedTemplate: TemplateInfo | null;
}

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  onSelectTemplate,
  selectedTemplate,
}) => {
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showPopularOnly, setShowPopularOnly] = useState(false);

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, [selectedCategory, selectedDifficulty, showPopularOnly]);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const filters: any = {};
      if (selectedCategory !== 'all') filters.category = selectedCategory;
      if (selectedDifficulty !== 'all') filters.difficulty = selectedDifficulty;
      if (showPopularOnly) filters.popular_only = true;

      const response = await templateApi.getTemplates(filters);
      setTemplates(response.templates || []);

      // Load categories separately
      try {
        const cats = await templateApi.getCategories();
        setCategories(cats || []);
      } catch (err) {
        console.warn('Failed to load categories:', err);
        setCategories([]);
      }
    } catch (error) {
      console.error('Failed to load templates:', error);
      toast.error('Failed to load templates');
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter templates by search query
  const filteredTemplates = searchQuery
    ? templates.filter(
        (t) =>
          t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : templates;

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Choose a Project Template
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Start with a pre-configured template or skip to create a custom project
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 pl-11 border-2 border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        {/* Category & Difficulty Filters */}
        <div className="flex flex-wrap gap-3">
          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border-2 border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name} ({cat.count})
              </option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-4 py-2 border-2 border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="expert">Expert</option>
          </select>

          {/* Popular Toggle */}
          <button
            onClick={() => setShowPopularOnly(!showPopularOnly)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              showPopularOnly
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            ⭐ Popular Only
          </button>

          {/* Clear Selection */}
          {selectedTemplate && (
            <button
              onClick={() => onSelectTemplate(null)}
              className="px-4 py-2 rounded-lg font-medium bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-900/30 transition-colors"
            >
              Clear Selection
            </button>
          )}
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
        Showing {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''}
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filteredTemplates.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            No templates found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Try adjusting your filters or search query
          </p>
        </div>
      ) : (
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <AnimatePresence mode="wait">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onSelect={onSelectTemplate}
                selected={selectedTemplate?.id === template.id}
              />
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Skip Templates Option */}
      <div className="mt-8 text-center">
        <button
          onClick={() => onSelectTemplate(null)}
          className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 font-medium underline"
        >
          Skip templates and create custom project
        </button>
      </div>
    </div>
  );
};

export default TemplateSelector;
