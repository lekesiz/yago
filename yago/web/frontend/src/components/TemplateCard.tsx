/**
 * YAGO v7.1 - Template Card Component
 * Displays individual template information
 */

import React from 'react';
import { motion } from 'framer-motion';
import type { TemplateInfo } from '../types/template';

interface TemplateCardProps {
  template: TemplateInfo;
  onSelect: (template: TemplateInfo) => void;
  selected?: boolean;
}

export const TemplateCard: React.FC<TemplateCardProps> = ({ template, onSelect, selected }) => {
  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      beginner: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
      intermediate: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
      advanced: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300',
      expert: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
    };
    return colors[difficulty as keyof typeof colors] || colors.intermediate;
  };

  const getDifficultyLabel = (difficulty: string) => {
    const labels = {
      beginner: 'Beginner',
      intermediate: 'Intermediate',
      advanced: 'Advanced',
      expert: 'Expert',
    };
    return labels[difficulty as keyof typeof labels] || difficulty;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(template)}
      className={`
        relative cursor-pointer rounded-xl p-6 transition-all duration-200
        ${
          selected
            ? 'bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-xl ring-4 ring-primary-500 ring-opacity-50'
            : 'bg-white dark:bg-gray-800 hover:shadow-lg border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500'
        }
      `}
    >
      {/* Popular Badge */}
      {template.popular && (
        <div className="absolute -top-2 -right-2">
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs font-bold rounded-full shadow-lg">
            ⭐ Popular
          </span>
        </div>
      )}

      {/* Icon & Title */}
      <div className="flex items-start gap-4 mb-4">
        <div className="text-4xl">{template.icon}</div>
        <div className="flex-1">
          <h3 className={`text-xl font-bold mb-1 ${selected ? 'text-white' : 'text-gray-900 dark:text-white'}`}>
            {template.name}
          </h3>
          <p className={`text-sm ${selected ? 'text-white/90' : 'text-gray-600 dark:text-gray-300'}`}>
            {template.description || 'Professional template for modern development'}
          </p>
        </div>
      </div>

      {/* Difficulty Badge */}
      <div className="mb-3">
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${selected ? 'bg-white/20 text-white' : getDifficultyColor(template.difficulty)}`}>
          {getDifficultyLabel(template.difficulty)}
        </span>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {template.tags.slice(0, 4).map((tag, index) => (
          <span
            key={index}
            className={`px-2 py-1 rounded-md text-xs font-medium ${
              selected
                ? 'bg-white/20 text-white'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
            }`}
          >
            {tag}
          </span>
        ))}
        {template.tags.length > 4 && (
          <span className={`px-2 py-1 text-xs ${selected ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'}`}>
            +{template.tags.length - 4} more
          </span>
        )}
      </div>

      {/* Stats */}
      <div className={`flex items-center justify-between text-sm ${selected ? 'text-white/90' : 'text-gray-600 dark:text-gray-400'}`}>
        <div className="flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{template.estimated_duration}</span>
        </div>
        <div className="flex items-center gap-1 font-medium">
          <span>~${template.estimated_cost.toFixed(2)}</span>
        </div>
      </div>

      {/* Selected Indicator */}
      {selected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute -bottom-2 -right-2 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center"
        >
          <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </motion.div>
      )}
    </motion.div>
  );
};

export default TemplateCard;
