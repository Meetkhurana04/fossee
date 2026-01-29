// frontend-web/src/services/api.js
import axios from 'axios';

// Production mein same domain, development mein localhost
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api'  // Same domain pe hai toh bas /api
  : 'http://localhost:8000/api';

console.log('Environment:', process.env.NODE_ENV);
console.log('API URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
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

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

// ============== API Functions ==============

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getDataset = async (id) => {
  const response = await api.get(`/dataset/${id}/`);
  return response.data;
};

export const getLatestDataset = async () => {
  const response = await api.get('/dataset/latest/');
  return response.data;
};

export const getHistory = async () => {
  const response = await api.get('/history/');
  return response.data;
};

export const getSummary = async (id) => {
  const response = await api.get(`/summary/${id}/`);
  return response.data;
};

export const downloadPDF = async (id) => {
  const response = await api.get(`/pdf/${id}/`, { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `equipment_report_${id}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const deleteDataset = async (id) => {
  await api.delete(`/dataset/${id}/delete/`);
};

export const register = async (userData) => {
  const response = await api.post('/auth/register/', userData);
  return response.data;
};

export const login = async (credentials) => {
  const response = await api.post('/auth/login/', credentials);
  return response.data;
};

export const logout = async () => {
  try {
    await api.post('/auth/logout/');
  } catch (error) {}
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
};

export default api;