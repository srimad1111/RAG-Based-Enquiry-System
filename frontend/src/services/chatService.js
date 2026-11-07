import apiClient from './apiClient';

export const chatService = {
  /**
   * Submit customer enquiry and generate version-grounded answer with citations (Phase 5)
   */
  async submitEnquiry(payload) {
    const response = await apiClient.post('/chat/enquiry', payload);
    return response.data;
  },

  /**
   * Fetch conversation thread history
   */
  async getThreadHistory(conversationId) {
    const response = await apiClient.get(`/chat/history/${encodeURIComponent(conversationId)}`);
    return response.data;
  },

  /**
   * Fetch recent enquiry audit logs
   */
  async getRecentLogs(limit = 20) {
    const response = await apiClient.get(`/chat/logs?limit=${limit}`);
    return response.data;
  },

  /**
   * Fetch LLM engine configuration
   */
  async getConfig() {
    const response = await apiClient.get('/chat/config');
    return response.data;
  }
};

export default chatService;

