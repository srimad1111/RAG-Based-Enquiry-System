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
   * Fetch latest evaluation benchmark report or empty state
   */
  async getReport() {
    const response = await apiClient.get('/analytics/report');
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

