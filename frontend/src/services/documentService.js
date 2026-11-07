import apiClient from './apiClient';

export const documentService = {
  /**
   * Fetch overview of base documentation files from filesystem
   */
  async getOverview() {
    const response = await apiClient.get('/documents/overview');
    return response.data;
  },

  /**
   * List ingested documents from SQLite with optional filters
   */
  async listDocuments(params = {}) {
    const response = await apiClient.get('/documents', { params });
    return response.data;
  },

  /**
   * Get overall ingestion statistics across versions and types
   */
  async getStats() {
    const response = await apiClient.get('/documents/stats/overview');
    return response.data;
  },

  /**
   * Fetch a single document record by ID
   */
  async getDocument(documentId) {
    const response = await apiClient.get(`/documents/${documentId}`);
    return response.data;
  },

  /**
   * Fetch all structured chunks for a document
   */
  async getDocumentChunks(documentId) {
    const response = await apiClient.get(`/documents/${documentId}/chunks`);
    return response.data;
  },

  /**
   * Admin upload document (multipart/form-data)
   */
  async uploadDocument(formData) {
    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Delete an ingested document and its chunks
   */
  async deleteDocument(documentId) {
    const response = await apiClient.delete(`/documents/${documentId}`);
    return response.data;
  },
};

export default documentService;
