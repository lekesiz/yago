/**
 * YAGO v8.0 - Template API Service
 * API client for template management
 */

import axios from 'axios';
import type { TemplatesResponse, TemplateDetail, TemplatePreview, TemplateCategory, TemplateInfo } from '../types/template';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('yago_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const templateApi = {
  /**
   * Get all templates with optional filters
   */
  async getTemplates(filters?: {
    category?: string;
    difficulty?: string;
    popular_only?: boolean;
  }): Promise<TemplatesResponse> {
    const { data } = await api.get('/templates/', { params: filters });
    return data;
  },

  /**
   * Get template categories
   */
  async getCategories(): Promise<TemplateCategory[]> {
    const { data } = await api.get('/templates/categories');
    return data;
  },

  /**
   * Get popular templates only
   */
  async getPopularTemplates(): Promise<TemplateInfo[]> {
    const { data } = await api.get('/templates/popular');
    return data;
  },

  /**
   * Get detailed template information
   */
  async getTemplate(templateId: string): Promise<TemplateDetail> {
    const { data } = await api.get(`/templates/${templateId}`);
    return data;
  },

  /**
   * Get template preview
   */
  async getTemplatePreview(templateId: string): Promise<TemplatePreview> {
    const { data } = await api.get(`/templates/${templateId}/preview`);
    return data;
  },

  /**
   * Apply template to create new project
   */
  async applyTemplate(templateId: string, customizations?: Record<string, any>): Promise<any> {
    const { data } = await api.post(`/templates/${templateId}/apply`, customizations);
    return data;
  },

  /**
   * Search templates
   */
  async searchTemplates(query: string): Promise<TemplateInfo[]> {
    const { data } = await api.get('/templates/search', { params: { q: query } });
    return data;
  },

  /**
   * Health check for template system
   */
  async health(): Promise<any> {
    const { data } = await api.get('/templates/health');
    return data;
  },
};

export default templateApi;
