"""
API Service for Cultural Bias Shield
Handles all API calls to the Flask backend
"""
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`Response received from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);

    // Handle specific error cases
    if (error.response?.status === 429) {
      throw new Error('Too many requests. Please try again in a moment.');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.response?.status === 404) {
      throw new Error('Service not found. Please check your configuration.');
    }

    throw error;
  }
);

export default api;

// Specific API methods
export const culturalBiasAPI = {
  // Analyze campaign for cultural bias
  analyzeCampaign: async (campaignData) => {
    try {
      const response = await api.post('/analyze', campaignData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Analysis failed');
    }
  },

  // Get supported countries
  getCountries: async () => {
    try {
      const response = await api.get('/countries');
      return response.data.countries;
    } catch (error) {
      throw new Error('Failed to load countries');
    }
  },

  // Get cultural dimensions for a country
  getCulturalDimensions: async (countryCode) => {
    try {
      const response = await api.get(`/cultural-dimensions/${countryCode}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to load cultural data for ${countryCode}`);
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Health check failed');
    }
  }
};
