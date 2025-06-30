import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '@/views/DashboardView.vue';
import LoginView from '@/views/LoginView.vue';
import { useAuthStore } from '@/stores/auth'; // Import Pinia store

const routes = [
  {
    path: '/',
    redirect: '/dashboard', // Redirect root to dashboard
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated; // Check if token exists

  if (to.meta.requiresAuth && !isAuthenticated) {
    // If route requires auth but user is not authenticated, redirect to login
    next('/login');
  } else if (to.name === 'Login' && isAuthenticated) {
    // If user is already authenticated and tries to go to login, redirect to dashboard
    next('/dashboard');
  } else {
    // Otherwise, allow navigation
    next();
  }
});

export default router;
