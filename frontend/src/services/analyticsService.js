import apiClient from './apiClient';

export const analyticsService = {
  /**
   * Fetch aggregate operational and evaluation metrics overview
   */
  async getOverview() {
    const response = await apiClient.get('/analytics/overview');
    return response.data;
  },

  /**
   * Fetch all recorded evaluation runs
   */
  async getRuns() {
    const response = await apiClient.get('/analytics/runs');
    return response.data;
  },

  /**
   * Fetch latest evaluation benchmark report or a specific run report
   */
  async getReport(runFile = null) {
    const url = runFile ? `/analytics/report?run_file=${encodeURIComponent(runFile)}` : '/analytics/report';
    const response = await apiClient.get(url);
    return response.data;
  },

  /**
   * Execute RAG benchmark suite across all product versions (v1.0, v2.0, v3.0)
   */
  async runBenchmark() {
    const response = await apiClient.post('/analytics/evaluate', {}, {
      timeout: 120000, // Benchmark takes ~20s
    });
    return response.data;
  },
};

export default analyticsService;

