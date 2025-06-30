import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '@/views/LoginView.vue';
import { useAuthStore } from '@/stores/auth';

// Mock the router
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/dashboard', name: 'Dashboard', component: { template: '<div>Dashboard</div>' } }],
});

describe('LoginView', () => {
  it('renders login form correctly', () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia(),
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
          },
        },
      },
    });

    expect(wrapper.find('h2').text()).toBe('AgriBridge 登入');
    expect(wrapper.find('input[type="text"]').exists()).toBe(true);
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('登入');
  });

  it('calls auth store login on form submission and redirects on success', async () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
          }),
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
          },
        },
      },
    });

    const authStore = useAuthStore();
    authStore.login.mockResolvedValue(true); // Mock successful login

    await wrapper.find('input[type="text"]').setValue('testuser');
    await wrapper.find('input[type="password"]').setValue('testpassword');
    await wrapper.find('form').trigger('submit');

    expect(authStore.login).toHaveBeenCalledWith('testuser', 'testpassword');
    expect(wrapper.vm.$toast.success).toHaveBeenCalledWith('登入成功！歡迎使用 AgriBridge。');
    expect(router.currentRoute.value.path).toBe('/'); // Router push to /dashboard will internally redirect
  });

  it('shows error toast on login failure', async () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
          }),
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
          },
        },
      },
    });

    const authStore = useAuthStore();
    authStore.login.mockRejectedValue(new Error('Invalid credentials')); // Mock failed login

    await wrapper.find('input[type="text"]').setValue('invalid');
    await wrapper.find('input[type="password"]').setValue('invalid');
    await wrapper.find('form').trigger('submit');

    expect(authStore.login).toHaveBeenCalled();
    expect(wrapper.vm.$toast.error).toHaveBeenCalledWith('登入失敗，請檢查用戶名或密碼。');
  });
});
