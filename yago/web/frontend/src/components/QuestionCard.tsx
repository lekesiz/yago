/**
 * YAGO v7.1 - Question Card Component
 * Displays a question and handles user input based on question type
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import type { QuestionUI } from '../types/clarification';

interface QuestionCardProps {
  question: QuestionUI;
  onAnswer: (answer: any) => void;
  initialValue?: any;
  disabled?: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  onAnswer,
  initialValue,
  disabled = false,
}) => {
  const [value, setValue] = useState<any>(initialValue || question.default || '');

  useEffect(() => {
    setValue(initialValue || question.default || '');
  }, [question.id, initialValue, question.default]);

  const handleChange = (newValue: any) => {
    setValue(newValue);
    onAnswer(newValue);
  };

  const renderInput = () => {
    switch (question.type) {
      case 'text':
        return (
          <textarea
            value={value}
            onChange={(e) => handleChange(e.target.value)}
            placeholder={question.placeholder}
            disabled={disabled}
            rows={4}
            className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-200"
          />
        );

      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
            className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-200"
          >
            <option value="">{question.placeholder || 'Select an option'}</option>
            {question.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );

      case 'multiselect':
        return (
          <div className="space-y-2">
            {question.options?.map((option) => (
              <label
                key={option}
                className="flex items-center space-x-3 p-3 rounded-lg border-2 border-gray-200 dark:border-gray-700
                         hover:border-primary-300 dark:hover:border-primary-600 cursor-pointer
                         transition-all duration-200"
              >
                <input
                  type="checkbox"
                  checked={(value as string[])?.includes(option) || false}
                  onChange={(e) => {
                    const currentValues = (value as string[]) || [];
                    if (e.target.checked) {
                      handleChange([...currentValues, option]);
                    } else {
                      handleChange(currentValues.filter((v) => v !== option));
                    }
                  }}
                  disabled={disabled}
                  className="w-5 h-5 rounded text-primary-600 focus:ring-2 focus:ring-primary-500
                           disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <span className="text-gray-700 dark:text-gray-300">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'checkbox':
        return (
          <label className="flex items-center space-x-3 p-4 rounded-lg border-2 border-gray-200 dark:border-gray-700
                           hover:border-primary-300 dark:hover:border-primary-600 cursor-pointer
                           transition-all duration-200">
            <input
              type="checkbox"
              checked={value === true}
              onChange={(e) => handleChange(e.target.checked)}
              disabled={disabled}
              className="w-6 h-6 rounded text-primary-600 focus:ring-2 focus:ring-primary-500
                       disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <span className="text-gray-700 dark:text-gray-300">Yes</span>
          </label>
        );

      case 'slider':
        return (
          <div className="space-y-4">
            <input
              type="range"
              min={question.min_value || 0}
              max={question.max_value || 100}
              value={value || question.min_value || 0}
              onChange={(e) => handleChange(parseInt(e.target.value))}
              disabled={disabled}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer
                       accent-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
              <span>{question.min_value || 0}</span>
              <span className="text-lg font-semibold text-primary-600 dark:text-primary-400">
                {value || question.min_value || 0}
              </span>
              <span>{question.max_value || 100}</span>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      basic: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      technical: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      infrastructure: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      security: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      quality: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    };
    return colors[category as keyof typeof colors] || colors.basic;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700"
    >
      {/* Category Badge */}
      <div className="flex items-center justify-between mb-4">
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${getCategoryColor(
            question.category
          )}`}
        >
          {question.category}
        </span>
        {question.required && (
          <span className="text-red-500 text-sm font-medium">* Required</span>
        )}
      </div>

      {/* Question Text */}
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        {question.text}
      </h2>

      {/* Hint */}
      {question.hint && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-6 flex items-start gap-2">
          <svg
            className="w-5 h-5 mt-0.5 flex-shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          {question.hint}
        </p>
      )}

      {/* Input */}
      <div className="mb-6">{renderInput()}</div>

      {/* Example */}
      {question.example && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <span className="font-semibold">Example:</span> {question.example}
          </p>
        </div>
      )}
    </motion.div>
  );
};

export default QuestionCard;
