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
   * Search vectors using semantic embedding similarity and metadata filtering (Phase 3)
   */
  async searchVectors(searchParams) {
    const response = await apiClient.post('/rag/search', searchParams);
    return response.data;
  },

  /**
   * Transform an informal customer question into a documentation-oriented query (Phase 4 Part A)
   */
  async rewriteQuery(params) {
    const response = await apiClient.post('/rag/rewrite', params);
    return response.data;
  },

  /**
   * Execute full version-aware hybrid retrieval (Phase 4 Part C & D)
   */
  async retrieveHybrid(params) {
    const response = await apiClient.post('/rag/retrieve', params);
    return response.data;
  },

  /**
   * 3-Way Comparative Evaluation (Raw Dense vs Rewritten Dense vs Rewritten Hybrid) (Phase 4 Part E)
   */
  async compareRetrievalMethods(params) {
    const response = await apiClient.post('/rag/compare', params);
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
   * Synchronize / Re-index all processed documents from SQLite into ChromaDB & BM25
   */
  async reindexAll() {
    const response = await apiClient.post('/rag/reindex');
    return response.data;
  }
};

export default ragService;
