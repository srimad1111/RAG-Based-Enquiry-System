import apiClient from './apiClient';

export const documentService = {
  /**
   * Fetch overview of all documented versions (v1.0, v2.0, v3.0)
   */
  async getOverview() {
    const response = await apiClient.get('/documents/overview');
    return response.data;
  },

  /**
   * Fetch documentation files for a specific version
   */
  async getByVersion(version) {
    const response = await apiClient.get(`/documents/version/${version}`);
    return response.data;
  },
};

export default documentService;

