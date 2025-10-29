/**
 * YAGO v8.0 - Cost Tracking Types
 * TypeScript definitions for cost tracking dashboard
 */

export interface CostSummary {
  project_id: string;
  total_tokens: number;
  total_api_calls: number;
  total_cost: number;
  start_date: string;
  end_date: string;
  cost_by_model: Record<string, number>;
  tokens_by_model: Record<string, number>;
  calls_by_model: Record<string, number>;
  cost_by_agent: Record<string, number>;
  tokens_by_agent: Record<string, number>;
  calls_by_agent: Record<string, number>;
  cost_by_phase: Record<string, number>;
  tokens_by_phase: Record<string, number>;
  avg_cost_per_call: number;
  avg_tokens_per_call: number;
  avg_duration_ms: number;
  cost_per_1k_tokens: number;
  calls_per_hour: number;
}

export interface AgentCosts {
  agent_id: string;
  agent_type: string;
  project_id: string;
  total_cost: number;
  total_tokens: number;
  total_calls: number;
  avg_cost_per_call: number;
  avg_tokens_per_call: number;
  models_used: string[];
  phases_active: string[];
  first_call: string;
  last_call: string;
  efficiency_score: number;
}

export interface Budget {
  id: string;
  project_id: string;
  budget_limit: number;
  alert_threshold: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface BudgetStatus {
  project_id: string;
  budget: Budget;
  has_budget: boolean;
  budget_limit: number;
  current_spend: number;
  current_spent: number;  // alias for current_spend
  remaining: number;
  percentage_used: number;
  is_over_budget: boolean;
  is_at_threshold: boolean;
  projected_final_cost: number | null;
  projected_final: number;  // alias for projected_final_cost
  days_remaining: number | null;
  threshold_reached: boolean;
  threshold_pct: number;
  time_remaining_pct: number;
}

export interface OptimizationSuggestion {
  id: string;
  project_id: string;
  title: string;
  description: string;
  category: 'model_selection' | 'caching' | 'parallelization' | 'context_reduction' | 'budget_alert';
  potential_savings_pct: number;
  potential_savings_amount: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  implementation_difficulty: 'easy' | 'medium' | 'hard';
  details: Record<string, any>;
  created_at: string;
}

export interface CostComparison {
  project_id: string;
  estimated_cost: number;
  actual_cost: number;
  variance: number;
  variance_pct: number;
  team_average_cost: number | null;
  cost_per_feature: number | null;
  efficiency_vs_average: number | null;
}

export interface CostHistoryPoint {
  timestamp: string;
  cumulative_cost: number;
  tokens_used: number;
  api_calls: number;
  phase?: string;
}

export interface ModelPricing {
  input_per_1m: number;
  output_per_1m: number;
  avg_per_1m: number;
}

export interface ModelPricingResponse {
  models: Record<string, ModelPricing>;
  currency: string;
  unit: string;
  last_updated: string;
}

// Chart data types
export interface CostChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string;
    borderWidth?: number;
    fill?: boolean;
  }>;
}

export interface AgentEfficiencyData {
  agent: string;
  efficiency: number;
  cost: number;
  calls: number;
  color: string;
}
