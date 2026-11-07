import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 120s timeout for local LLM inference & hybrid search
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorDetails = {
      message: error.response?.data?.error?.message || error.message || 'Network request failed',
      status: error.response?.status,
      path: error.config?.url,
    };
    return Promise.reject(errorDetails);
  }
);

export default apiClient;

