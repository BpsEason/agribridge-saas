import { defineStore } from 'pinia';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('agribridge_token') || null,
    user: null, // You might store user info here
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post(`${API_BASE_URL}/login`, { username, password });
        const { access_token, token_type } = response.data;
        this.token = access_token;
        localStorage.setItem('agribridge_token', access_token);
        // You might fetch user profile here if needed
        return true;
      } catch (error) {
        this.logout(); // Clear token on failed login attempt
        throw error; // Re-throw to handle in component
      }
    },
    logout() {
      this.token = null;
      localStorage.removeItem('agribridge_token');
      this.user = null;
    },
    // Optional: action to check token validity with backend
    async checkAuth() {
      if (!this.token) {
        this.logout();
        return false;
      }
      try {
        // This endpoint requires authentication to test token validity
        const response = await axios.get(`${API_BASE_URL}/protected`, {
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        });
        // If the backend also returns user info with protected endpoint
        // this.user = response.data.user;
        return true;
      } catch (error) {
        console.error('Token validation failed:', error);
        this.logout();
        return false;
      }
    },
  },
  persist: {
    key: 'agribridge_auth',
    paths: ['token'], // Only persist the token
  },
});
