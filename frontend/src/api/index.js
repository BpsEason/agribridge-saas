import axios from 'axios';
import { useAuthStore } from '@/stores/auth'; // Import auth store for token

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add JWT token to requests (optional, can be done per-request too)
api.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const esgApi = {
  getEsgReport: (farmerId) => api.get(`/farmers/${farmerId}/esg-report`),
  createFarmer: (data) => api.post('/farmers', data),
  getAllFarmers: () => api.get('/farmers'),
};

export const productApi = {
  getProducts: (limit = 10, offset = 0) => api.get(`/products?limit=${limit}&offset=${offset}`),
  createProduct: (data) => api.post('/products', data),
  getProductById: (productId) => api.get(`/products/${productId}`),
};

export const orderApi = {
  getOrders: (limit = 10, offset = 0) => api.get(`/orders?limit=${limit}&offset=${offset}`),
  createOrder: (data) => api.post('/orders', data),
};

export const financialApi = {
  processPayment: (data) => api.post('/payments', data),
  getTransactions: (limit = 10, offset = 0) => api.get(`/ledger/transactions?limit=${limit}&offset=${offset}`),
};

export const iotApi = {
  sendIoTData: (data) => api.post('/iot/data', data),
  getIoTData: (deviceId, limit = 20) => api.get(`/iot/data/${deviceId}?limit=${limit}`),
};

export const blockchainApi = {
  getTransactions: (limit = 5) => api.get(`/blockchain/transactions?limit=${limit}`),
  createTransaction: (data) => api.post('/blockchain/transactions', data),
};

export const notificationApi = {
  sendLineNotification: (userId, message) => {
    // This is a simplified call; in a real app, backend would handle the push
    // We call a mock endpoint that simulates backend sending the LINE push.
    return api.post('/notifications/send-line-message', { user_id: userId, message: message });
  }
};
