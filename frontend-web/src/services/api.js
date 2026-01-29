// frontend-web/src/services/api.js
/**
 * API Service for communicating with Django backend.
 * Uses Axios for HTTP requests with token authentication support.
 */

import axios from 'axios';

// Base URL for the Django API
const API_BASE_URL = 'http://localhost:8000/api';

// Create Axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear storage
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

/**
 * Upload CSV file to backend
 * @param {File} file - The CSV file to upload
 * @returns {Promise} - Response with dataset info
 */
export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Get a specific dataset by ID
 * @param {number} id - Dataset ID
 * @returns {Promise} - Dataset details
 */
export const getDataset = async (id) => {
  const response = await api.get(`/dataset/${id}/`);
  return response.data;
};

/**
 * Get the most recently uploaded dataset
 * @returns {Promise} - Latest dataset
 */
export const getLatestDataset = async () => {
  const response = await api.get('/dataset/latest/');
  return response.data;
};

/**
 * Get upload history (last 5 datasets)
 * @returns {Promise} - Array of datasets
 */
export const getHistory = async () => {
  const response = await api.get('/history/');
  return response.data;
};

/**
 * Get summary for a specific dataset
 * @param {number} id - Dataset ID
 * @returns {Promise} - Summary statistics
 */
export const getSummary = async (id) => {
  const response = await api.get(`/summary/${id}/`);
  return response.data;
};

/**
 * Download PDF report for a dataset
 * @param {number} id - Dataset ID
 */
export const downloadPDF = async (id) => {
  const response = await api.get(`/pdf/${id}/`, {
    responseType: 'blob',
  });
  
  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `equipment_report_${id}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

/**
 * Delete a dataset
 * @param {number} id - Dataset ID
 */
export const deleteDataset = async (id) => {
  await api.delete(`/dataset/${id}/delete/`);
};

// ============== Authentication ==============

/**
 * Register new user
 * @param {object} userData - { username, password, email }
 * @returns {Promise} - User info and token
 */
export const register = async (userData) => {
  const response = await api.post('/auth/register/', userData);
  return response.data;
};

/**
 * Login user
 * @param {object} credentials - { username, password }
 * @returns {Promise} - User info and token
 */
export const login = async (credentials) => {
  const response = await api.post('/auth/login/', credentials);
  return response.data;
};

/**
 * Logout user
 */
export const logout = async () => {
  try {
    await api.post('/auth/logout/');
  } catch (error) {
    // Ignore errors on logout
  }
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
};

export default api;