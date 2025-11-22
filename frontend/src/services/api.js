import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Extract error message
    const errorMessage =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';

    // Handle different error status codes
    if (error.response) {
      switch (error.response.status) {
        case 401:
          break;
        case 403:
          break;
        case 404:
          break;
        case 500:
          break;
        default:
          break;
      }
    }

    // Don't show toast for cancelled requests
    if (error.code !== 'ERR_CANCELED') {
      toast.error(errorMessage);
    }

    return Promise.reject(error);
  }
);

// API service methods
export const apiService = {
  // Health check
  healthCheck: () => apiClient.get('/healthz'),

  // System status
  getStatus: () => apiClient.get('/api/v1/status'),

  // Weather data
  getWeather: (location, startDate, endDate) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const queryString = params.toString();
    return apiClient.get(`/api/v1/weather/${encodeURIComponent(location)}${queryString ? '?' + queryString : ''}`);
  },

  // Social media reports
  getSocialMedia: (location) => apiClient.get(`/api/v1/social-media/${encodeURIComponent(location)}`),

  // Analyze disaster
  analyzeDisaster: (data) => apiClient.post('/api/v1/analyze', data),

  // Generate response plan
  generatePlan: (data) => apiClient.post('/api/v1/plan', data),

  // Verify plan
  verifyPlan: (data) => apiClient.post('/api/v1/verify', data),

  // Send alerts
  sendAlerts: (data) => apiClient.post('/api/v1/alerts', data),

  // Full workflow
  executeWorkflow: (location) => apiClient.post('/api/v1/disaster-response', { location }),

  // Session management
  getSessions: (limit = 10) => apiClient.get(`/api/v1/sessions?limit=${limit}`),
  getSession: (sessionId) => apiClient.get(`/api/v1/sessions/${sessionId}`),

  // Evaluation
  runEvaluation: () => apiClient.post('/api/v1/evaluate'),
  runBenchmark: () => apiClient.get('/api/v1/evaluate/benchmark'),
};

export default apiClient;

