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
    // Add any auth tokens here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
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
          // Handle unauthorized
          break;
        case 403:
          // Handle forbidden
          break;
        case 404:
          // Handle not found
          break;
        case 500:
          // Handle server error
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
  getWeather: (city) => apiClient.get(`/api/v1/weather/${city}`),

  // Social media reports
  getSocialMedia: (city) => apiClient.get(`/api/v1/social-media/${city}`),

  // Analyze disaster
  analyzeDisaster: (data) => apiClient.post('/api/v1/analyze', data),

  // Generate response plan
  generatePlan: (data) => apiClient.post('/api/v1/plan', data),

  // Verify plan
  verifyPlan: (data) => apiClient.post('/api/v1/verify', data),

  // Send alerts
  sendAlerts: (data) => apiClient.post('/api/v1/alerts', data),

  // Full workflow
  executeWorkflow: (data) => apiClient.post('/api/v1/disaster-response', data),

  // Session management
  getSessions: (limit = 10) => apiClient.get(`/api/v1/sessions?limit=${limit}`),
  getSession: (sessionId) => apiClient.get(`/api/v1/sessions/${sessionId}`),

  // Evaluation
  runEvaluation: () => apiClient.post('/api/v1/evaluate'),
  runBenchmark: () => apiClient.get('/api/v1/evaluate/benchmark'),
};

export default apiClient;

