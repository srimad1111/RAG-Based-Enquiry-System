import apiClient from './apiClient';

export const ragService = {
  /**
   * Get ChromaDB indexing status and statistics
   */
  async getStatus() {
    const response = await apiClient.get('/rag/status');
    return response.data;
  },

  /**
   * Search vectors using semantic embedding similarity and metadata filtering
   */
  async searchVectors(searchParams) {
    const response = await apiClient.post('/rag/search', searchParams);
    return response.data;
  },

  /**
   * Index chunks for a specific document into ChromaDB
   */
  async indexDocument(documentId) {
    const response = await apiClient.post(`/rag/index?document_id=${encodeURIComponent(documentId)}`);
    return response.data;
  },

  /**
   * Synchronize / Re-index all processed documents from SQLite into ChromaDB
   */
  async reindexAll() {
    const response = await apiClient.post('/rag/reindex');
    return response.data;
  }
};

export default ragService;

