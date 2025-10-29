/**
 * YAGO v8.0 - Benchmark API Service
 * API client for benchmark and performance testing endpoints
 */

import axios from 'axios';
import type {
  BenchmarkConfig,
  BenchmarkResult,
  BenchmarkComparison,
  RunBenchmarkResponse,
  GetBenchmarkResultsResponse,
  GetBenchmarkSummaryResponse,
  CompareBenchmarksResponse,
  BenchmarkType,
} from '../types/benchmark';

const API_BASE = 'http://localhost:8000/api/v1/benchmarks';

export const benchmarkApi = {
  /**
   * Run a new benchmark
   */
  async runBenchmark(
    projectId: string,
    config: Partial<BenchmarkConfig>
  ): Promise<RunBenchmarkResponse> {
    const { data } = await axios.post<RunBenchmarkResponse>(
      `${API_BASE}/run`,
      {
        project_id: projectId,
        ...config,
      }
    );
    return data;
  },

  /**
   * Get benchmark results
   */
  async getBenchmarkResults(
    projectId: string,
    benchmarkType?: BenchmarkType,
    limit?: number
  ): Promise<GetBenchmarkResultsResponse> {
    const params: any = {};
    if (benchmarkType) params.type = benchmarkType;
    if (limit) params.limit = limit;

    const { data } = await axios.get<GetBenchmarkResultsResponse>(
      `${API_BASE}/results/${projectId}`,
      { params }
    );
    return data;
  },

  /**
   * Get a specific benchmark result
   */
  async getBenchmarkResult(resultId: string): Promise<BenchmarkResult> {
    const { data } = await axios.get<BenchmarkResult>(
      `${API_BASE}/result/${resultId}`
    );
    return data;
  },

  /**
   * Get benchmark summary and trends
   */
  async getBenchmarkSummary(
    projectId: string,
    startDate?: string,
    endDate?: string
  ): Promise<GetBenchmarkSummaryResponse> {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const { data } = await axios.get<GetBenchmarkSummaryResponse>(
      `${API_BASE}/summary/${projectId}`,
      { params }
    );
    return data;
  },

  /**
   * Compare multiple benchmarks
   */
  async compareBenchmarks(
    benchmarkIds: string[],
    name?: string
  ): Promise<CompareBenchmarksResponse> {
    const { data } = await axios.post<CompareBenchmarksResponse>(
      `${API_BASE}/compare`,
      {
        benchmark_ids: benchmarkIds,
        name: name || 'Comparison',
      }
    );
    return data;
  },

  /**
   * Get comparison by ID
   */
  async getComparison(comparisonId: string): Promise<BenchmarkComparison> {
    const { data } = await axios.get<BenchmarkComparison>(
      `${API_BASE}/comparison/${comparisonId}`
    );
    return data;
  },

  /**
   * Delete a benchmark result
   */
  async deleteBenchmark(resultId: string): Promise<{ success: boolean }> {
    const { data } = await axios.delete<{ success: boolean }>(
      `${API_BASE}/result/${resultId}`
    );
    return data;
  },

  /**
   * Cancel a running benchmark
   */
  async cancelBenchmark(resultId: string): Promise<{ success: boolean }> {
    const { data } = await axios.post<{ success: boolean }>(
      `${API_BASE}/result/${resultId}/cancel`
    );
    return data;
  },
};
