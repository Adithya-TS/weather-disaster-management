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

// Request interceptor - add JWT token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
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
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
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
  getSocialMedia: (location, date) => {
    const params = new URLSearchParams();
    if (date) params.append('date', date);
    const queryString = params.toString();
    return apiClient.get(`/api/v1/social-media/${encodeURIComponent(location)}${queryString ? '?' + queryString : ''}`);
  },

  // Route weather analysis
  getRouteWeather: (startCity, endCity, date) => {
    const params = new URLSearchParams();
    params.append('start', startCity);
    params.append('end', endCity);
    if (date) params.append('date', date);
    return apiClient.get(`/api/v1/route-weather?${params.toString()}`);
  },

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

  // Seismic monitoring
  getEarthquakes: (data) => apiClient.post('/api/v1/earthquakes', data),
  getTsunamiWarnings: (data) => apiClient.post('/api/v1/tsunami-warnings', data),
  seismicFactCheck: (data) => apiClient.post('/api/v1/seismic-fact-check', data),

  // Session management
  getSessions: (limit = 10) => apiClient.get(`/api/v1/sessions?limit=${limit}`),
  getSession: (sessionId) => apiClient.get(`/api/v1/sessions/${sessionId}`),

  // Evaluation
  runEvaluation: () => apiClient.post('/api/v1/evaluate'),
  runBenchmark: () => apiClient.get('/api/v1/evaluate/benchmark'),

  // Authentication
  googleLogin: (data) => apiClient.post('/auth/google/callback', data),

  // Chat history
  getChatHistory: (limit = 50, offset = 0) => 
    apiClient.get(`/chat/history?limit=${limit}&offset=${offset}`),
  getChatById: (chatId) => apiClient.get(`/chat/history/${chatId}`),
};

export default apiClient;

