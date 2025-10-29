/**
 * YAGO v8.0 - Benchmark Type Definitions
 * Types for performance benchmarking and testing
 */

export type BenchmarkStatus = 'pending' | 'running' | 'completed' | 'failed';
export type BenchmarkType = 'performance' | 'quality' | 'cost' | 'all';
export type MetricType = 'latency' | 'throughput' | 'accuracy' | 'cost' | 'memory' | 'cpu';

export interface BenchmarkConfig {
  benchmark_id: string;
  name: string;
  description: string;
  type: BenchmarkType;
  iterations: number;
  warmup_iterations: number;
  timeout_seconds: number;
  parallel_execution: boolean;
  metrics_to_track: MetricType[];
  created_at: string;
  created_by: string;
}

export interface BenchmarkResult {
  result_id: string;
  benchmark_id: string;
  project_id: string;
  status: BenchmarkStatus;
  started_at: string;
  completed_at?: string;
  duration_ms: number;
  iterations_completed: number;
  iterations_failed: number;
  metrics: BenchmarkMetrics;
  error?: string;
  metadata: Record<string, any>;
}

export interface BenchmarkMetrics {
  // Performance Metrics
  avg_latency_ms: number;
  min_latency_ms: number;
  max_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;

  // Throughput
  requests_per_second: number;
  tokens_per_second: number;

  // Quality Metrics
  accuracy_score: number;
  precision_score: number;
  recall_score: number;
  f1_score: number;

  // Resource Usage
  avg_memory_mb: number;
  max_memory_mb: number;
  avg_cpu_percent: number;
  max_cpu_percent: number;

  // Cost Metrics
  total_cost: number;
  cost_per_request: number;
  total_tokens: number;
  cost_per_1k_tokens: number;

  // Error Metrics
  error_rate: number;
  timeout_rate: number;
  retry_rate: number;
}

export interface BenchmarkComparison {
  comparison_id: string;
  name: string;
  benchmark_ids: string[];
  results: BenchmarkResult[];
  winner?: string; // benchmark_id of best performer
  improvements: Record<string, number>; // metric -> percentage improvement
  created_at: string;
}

export interface PerformanceTrend {
  metric: MetricType;
  data_points: TrendDataPoint[];
  trend_direction: 'improving' | 'declining' | 'stable';
  improvement_rate_pct: number;
}

export interface TrendDataPoint {
  timestamp: string;
  value: number;
  benchmark_id: string;
  label?: string;
}

export interface BenchmarkSummary {
  total_benchmarks: number;
  completed_benchmarks: number;
  failed_benchmarks: number;
  running_benchmarks: number;
  avg_duration_ms: number;
  total_iterations: number;
  overall_metrics: BenchmarkMetrics;
  best_performance: BenchmarkResult;
  worst_performance: BenchmarkResult;
  latest_result: BenchmarkResult;
}

export interface AgentBenchmark {
  agent_type: string;
  benchmarks_run: number;
  avg_latency_ms: number;
  success_rate: number;
  avg_accuracy: number;
  total_cost: number;
  performance_score: number; // 0-100
}

export interface ModelBenchmark {
  model_name: string;
  benchmarks_run: number;
  avg_latency_ms: number;
  avg_cost_per_request: number;
  avg_quality_score: number;
  total_tokens: number;
  cost_efficiency: number; // quality / cost ratio
}

// API Response Types
export interface RunBenchmarkResponse {
  benchmark_id: string;
  result_id: string;
  status: BenchmarkStatus;
  message: string;
}

export interface GetBenchmarkResultsResponse {
  project_id: string;
  total: number;
  results: BenchmarkResult[];
}

export interface GetBenchmarkSummaryResponse {
  project_id: string;
  summary: BenchmarkSummary;
  trends: PerformanceTrend[];
}

export interface CompareBenchmarksResponse {
  comparison: BenchmarkComparison;
  insights: string[];
  recommendations: string[];
}
