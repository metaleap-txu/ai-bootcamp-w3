/**
 * API client configuration using Axios.
 * 
 * Provides a configured Axios instance with error handling and interceptors.
 */
import axios, { AxiosError, AxiosResponse } from 'axios';

// Base API URL - uses Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * Configured Axios instance for API calls.
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

/**
 * Response interceptor for handling successful responses.
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as any;
      
      console.error(`API Error ${status}:`, data?.message || error.message);
      
      // You can add specific error handling here
      if (status === 401) {
        // Handle unauthorized
      } else if (status === 403) {
        // Handle forbidden
      } else if (status === 404) {
        // Handle not found
      } else if (status >= 500) {
        // Handle server errors
        console.error('Server error occurred');
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from server:', error.message);
    } else {
      // Error setting up the request
      console.error('Request setup error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

/**
 * Extract error message from API error.
 */
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as any;
    return data?.message || error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};
