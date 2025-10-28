/**
 * YAGO v7.1 - Cost Tracking API Service
 * API client for cost tracking endpoints
 */

import axios from 'axios';
import type {
  CostSummary,
  AgentCosts,
  BudgetStatus,
  OptimizationSuggestion,
  CostComparison,
  CostHistoryPoint,
  ModelPricingResponse,
} from '../types/cost';

const API_BASE = 'http://localhost:8000/api/v1/costs';

export const costApi = {
  // ========== Cost Tracking ==========

  async getCostSummary(
    projectId: string,
    startDate?: string,
    endDate?: string
  ): Promise<CostSummary> {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const { data } = await axios.get<CostSummary>(
      `${API_BASE}/summary/${projectId}`,
      { params }
    );
    return data;
  },

  async getAgentCosts(projectId: string, agentType: string): Promise<AgentCosts> {
    const { data } = await axios.get<AgentCosts>(
      `${API_BASE}/agent/${projectId}/${agentType}`
    );
    return data;
  },

  // ========== Budget Management ==========

  async setBudget(
    projectId: string,
    budgetLimit: number,
    alertThreshold: number = 0.75
  ): Promise<{ success: boolean }> {
    const { data } = await axios.post(
      `${API_BASE}/budget/${projectId}`,
      null,
      {
        params: {
          budget_limit: budgetLimit,
          alert_threshold: alertThreshold,
        },
      }
    );
    return data;
  },

  async getBudgetStatus(projectId: string): Promise<BudgetStatus> {
    const { data } = await axios.get<BudgetStatus>(
      `${API_BASE}/budget/${projectId}`
    );
    return data;
  },

  // ========== Optimization ==========

  async getOptimizations(projectId: string): Promise<OptimizationSuggestion[]> {
    const { data } = await axios.get<OptimizationSuggestion[]>(
      `${API_BASE}/optimizations/${projectId}`
    );
    return data;
  },

  // ========== Comparison & Analysis ==========

  async setEstimate(projectId: string, estimatedCost: number): Promise<{ success: boolean }> {
    const { data } = await axios.post(
      `${API_BASE}/estimate/${projectId}`,
      null,
      { params: { estimated_cost: estimatedCost } }
    );
    return data;
  },

  async getComparison(projectId: string): Promise<CostComparison> {
    const { data } = await axios.get<CostComparison>(
      `${API_BASE}/comparison/${projectId}`
    );
    return data;
  },

  async getCostHistory(
    projectId: string,
    intervalMinutes: number = 60
  ): Promise<CostHistoryPoint[]> {
    const { data } = await axios.get<CostHistoryPoint[]>(
      `${API_BASE}/history/${projectId}`,
      { params: { interval_minutes: intervalMinutes } }
    );
    return data;
  },

  // ========== Model Pricing ==========

  async getModelPricing(): Promise<ModelPricingResponse> {
    const { data } = await axios.get<ModelPricingResponse>(
      `${API_BASE}/models/pricing`
    );
    return data;
  },

  // ========== Health ==========

  async getHealth(): Promise<{
    status: string;
    total_projects: number;
    total_api_calls: number;
    total_cost_tracked: number;
    active_budgets: number;
    models_supported: number;
  }> {
    const { data } = await axios.get(`${API_BASE}/health`);
    return data;
  },
};
