/**
 * YAGO v8.0 - API Service for Clarification
 */

import axios from 'axios';
import type {
  StartClarificationRequest,
  ClarificationResponse,
  AnswerRequest,
  DraftUpdate,
  ClarificationProgress,
} from '../types/clarification';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('yago_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('yago_token');
    }
    return Promise.reject(error);
  }
);

export const clarificationApi = {
  /**
   * Start a new clarification session
   */
  async start(request: StartClarificationRequest): Promise<ClarificationResponse> {
    const response = await api.post<ClarificationResponse>('/clarifications/start', request);
    return response.data;
  },

  /**
   * Get current clarification state
   */
  async get(sessionId: string): Promise<ClarificationResponse> {
    const response = await api.get<ClarificationResponse>(`/clarifications/${sessionId}`);
    return response.data;
  },

  /**
   * Submit an answer
   */
  async submitAnswer(sessionId: string, request: AnswerRequest): Promise<ClarificationResponse> {
    const response = await api.post<ClarificationResponse>(
      `/clarifications/${sessionId}/answer`,
      request
    );
    return response.data;
  },

  /**
   * Update draft (auto-save)
   */
  async updateDraft(sessionId: string, draft: DraftUpdate): Promise<{ status: string; timestamp: string }> {
    const response = await api.put(`/clarifications/${sessionId}/draft`, draft);
    return response.data;
  },

  /**
   * Get progress
   */
  async getProgress(sessionId: string): Promise<ClarificationProgress> {
    const response = await api.get<ClarificationProgress>(`/clarifications/${sessionId}/progress`);
    return response.data;
  },

  /**
   * Complete clarification
   */
  async complete(sessionId: string): Promise<{ status: string; brief: any; message: string }> {
    const response = await api.post(`/clarifications/${sessionId}/complete`);
    return response.data;
  },

  /**
   * Navigate to next/previous question
   */
  async navigate(sessionId: string, direction: 'next' | 'previous'): Promise<ClarificationResponse> {
    const response = await api.post<ClarificationResponse>(
      `/clarifications/${sessionId}/navigate/${direction}`
    );
    return response.data;
  },

  /**
   * Health check
   */
  async health(): Promise<{ status: string; version: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  },
};

export default clarificationApi;
