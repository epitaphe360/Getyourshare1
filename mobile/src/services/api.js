/**
 * API Service - Connection to ShareYourSales Backend
 * Connects to the same backend as the web application
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Base URL - Change this to your backend URL
// Development: http://localhost:8001 or http://YOUR_LOCAL_IP:8001
// Production: https://your-production-api.com
const API_BASE_URL = __DEV__
  ? 'http://10.0.2.2:8001'  // Android emulator
  : 'https://your-production-api.com';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  async config => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout user
      await AsyncStorage.removeItem('authToken');
      await AsyncStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

// ============================================
// AUTHENTICATION APIs
// ============================================

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    if (response.data.token) {
      await AsyncStorage.setItem('authToken', response.data.token);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  logout: async () => {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('user');
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/api/auth/profile', profileData);
    return response.data;
  },
};

// ============================================
// DASHBOARD APIs
// ============================================

export const dashboardAPI = {
  getStats: async (role) => {
    const response = await api.get(`/api/dashboard/stats?role=${role}`);
    return response.data;
  },

  getChartData: async (type, period) => {
    const response = await api.get(`/api/dashboard/charts/${type}?period=${period}`);
    return response.data;
  },
};

// ============================================
// MARKETPLACE APIs
// ============================================

export const marketplaceAPI = {
  getProducts: async (params = {}) => {
    const response = await api.get('/api/marketplace/products', { params });
    return response.data;
  },

  getProductDetails: async (productId) => {
    const response = await api.get(`/api/marketplace/products/${productId}`);
    return response.data;
  },

  searchProducts: async (query) => {
    const response = await api.get('/api/marketplace/search', { params: { q: query } });
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/api/marketplace/categories');
    return response.data;
  },
};

// ============================================
// AFFILIATION APIs
// ============================================

export const affiliationAPI = {
  requestAffiliation: async (productId, message) => {
    const response = await api.post('/api/affiliation/request', {
      product_id: productId,
      message,
    });
    return response.data;
  },

  getMyRequests: async () => {
    const response = await api.get('/api/affiliation/requests');
    return response.data;
  },

  approveRequest: async (requestId) => {
    const response = await api.post(`/api/affiliation/requests/${requestId}/approve`);
    return response.data;
  },

  rejectRequest: async (requestId, reason) => {
    const response = await api.post(`/api/affiliation/requests/${requestId}/reject`, { reason });
    return response.data;
  },
};

// ============================================
// TRACKING LINKS APIs
// ============================================

export const linksAPI = {
  getMyLinks: async () => {
    const response = await api.get('/api/affiliate-links/my-links');
    return response.data;
  },

  getLinkStats: async (linkId) => {
    const response = await api.get(`/api/affiliate-links/${linkId}/stats`);
    return response.data;
  },

  generateQRCode: async (linkId) => {
    const response = await api.get(`/api/affiliate-links/${linkId}/qrcode`);
    return response.data;
  },
};

// ============================================
// PRODUCTS APIs (Merchants)
// ============================================

export const productsAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/api/products', { params });
    return response.data;
  },

  getById: async (productId) => {
    const response = await api.get(`/api/products/${productId}`);
    return response.data;
  },

  create: async (productData) => {
    const response = await api.post('/api/products', productData);
    return response.data;
  },

  update: async (productId, productData) => {
    const response = await api.put(`/api/products/${productId}`, productData);
    return response.data;
  },

  delete: async (productId) => {
    const response = await api.delete(`/api/products/${productId}`);
    return response.data;
  },

  uploadImage: async (productId, imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    const response = await api.post(`/api/products/${productId}/image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// ============================================
// CONVERSIONS & ANALYTICS APIs
// ============================================

export const analyticsAPI = {
  getConversions: async (params = {}) => {
    const response = await api.get('/api/conversions', { params });
    return response.data;
  },

  getClicks: async (params = {}) => {
    const response = await api.get('/api/clicks', { params });
    return response.data;
  },

  getRevenue: async (period) => {
    const response = await api.get(`/api/analytics/revenue?period=${period}`);
    return response.data;
  },

  getPerformance: async () => {
    const response = await api.get('/api/analytics/performance');
    return response.data;
  },
};

// ============================================
// MESSAGING APIs
// ============================================

export const messagingAPI = {
  getConversations: async () => {
    const response = await api.get('/api/messages/conversations');
    return response.data;
  },

  getMessages: async (conversationId) => {
    const response = await api.get(`/api/messages/${conversationId}`);
    return response.data;
  },

  sendMessage: async (recipientId, message) => {
    const response = await api.post('/api/messages/send', {
      recipient_id: recipientId,
      message,
    });
    return response.data;
  },

  markAsRead: async (messageId) => {
    const response = await api.put(`/api/messages/${messageId}/read`);
    return response.data;
  },
};

// ============================================
// NOTIFICATIONS APIs
// ============================================

export const notificationsAPI = {
  getAll: async () => {
    const response = await api.get('/api/notifications');
    return response.data;
  },

  markAsRead: async (notificationId) => {
    const response = await api.put(`/api/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.put('/api/notifications/read-all');
    return response.data;
  },
};

// ============================================
// SETTINGS APIs
// ============================================

export const settingsAPI = {
  getPersonalSettings: async () => {
    const response = await api.get('/api/settings/personal');
    return response.data;
  },

  updatePersonalSettings: async (settings) => {
    const response = await api.put('/api/settings/personal', settings);
    return response.data;
  },

  getCompanySettings: async () => {
    const response = await api.get('/api/settings/company');
    return response.data;
  },

  updateCompanySettings: async (settings) => {
    const response = await api.put('/api/settings/company', settings);
    return response.data;
  },

  changePassword: async (oldPassword, newPassword) => {
    const response = await api.post('/api/settings/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

// ============================================
// SUBSCRIPTIONS APIs (Stripe)
// ============================================

export const subscriptionAPI = {
  getPlans: async () => {
    const response = await api.get('/api/subscriptions/plans');
    return response.data;
  },

  getCurrentSubscription: async () => {
    const response = await api.get('/api/subscriptions/current');
    return response.data;
  },

  subscribe: async (planId, paymentMethodId) => {
    const response = await api.post('/api/subscriptions/subscribe', {
      plan_id: planId,
      payment_method_id: paymentMethodId,
    });
    return response.data;
  },

  cancelSubscription: async () => {
    const response = await api.post('/api/subscriptions/cancel');
    return response.data;
  },
};

export default api;
