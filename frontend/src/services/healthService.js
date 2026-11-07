import apiClient from './apiClient';

export const healthService = {
  /**
   * Fetch complete backend diagnostics (API, SQLite, ChromaDB, File Storage)
   */
  async getHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Lightweight ping check
   */
  async ping() {
    const response = await apiClient.get('/health/ping');
    return response.data;
  },

  /**
   * Fetch system metadata and product version settings
   */
  async getSystemInfo() {
    const response = await apiClient.get('/system/info');
    return response.data;
  },
};

export default healthService;

