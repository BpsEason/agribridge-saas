import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '@/views/DashboardView.vue';
import { esgApi, productApi, orderApi, financialApi, iotApi, notificationApi, blockchainApi } from '@/api';
import { useAuthStore } from '@/stores/auth';

// Mock APIs
vi.mock('@/api', () => ({
  esgApi: {
    getEsgReport: vi.fn(() => Promise.resolve({
      data: {
        farmer_name: 'Test Farmer',
        esg_score: 95.5,
        social_impact: { fair_trade_index: 0.95, community_engagement: 'High' },
        environmental_impact: { carbon_footprint_reduction_tons: 2.5, water_usage_efficiency: 'High' },
      },
    })),
  },
  productApi: {
    getProducts: vi.fn(() => Promise.resolve({
      data: [
        { id: 101, name: 'Test Apple', price: 25.50, farmer_id: 1, tenant_id: 1 },
        { id: 102, name: 'Test Orange', price: 30.00, farmer_id: 1, tenant_id: 1 },
      ],
    })),
  },
  orderApi: {
    getOrders: vi.fn(() => Promise.resolve({
      data: [
        { id: 1, product_id: 101, quantity: 2, total_price: 51.00, buyer_id: 10, status: 'completed', tenant_id: 1 },
        { id: 2, product_id: 102, quantity: 1, total_price: 30.00, buyer_id: 11, status: 'pending', tenant_id: 1 },
      ],
    })),
  },
  financialApi: {
    getTransactions: vi.fn(() => Promise.resolve({
      data: [
        { transaction_id: 'txn1', status: 'completed', amount: 100.00, currency: 'TWD', order_id: 1 },
      ],
    })),
  },
  iotApi: {
    getIoTData: vi.fn(() => Promise.resolve({
      data: [
        { device_id: 'sensor-001', timestamp: '2023-01-01T00:00:00Z', temperature: 20.0, humidity: 50.0 },
        { device_id: 'sensor-001', timestamp: '2023-01-01T00:05:00Z', temperature: 21.0, humidity: 51.0 },
      ],
    })),
  },
  blockchainApi: {
    getTransactions: vi.fn(() => Promise.resolve({
      data: [
        { sender: 'A', receiver: 'B', amount: 10, hash: 'hash1', timestamp: '2023-01-01T00:00:00Z', block_id: 1 },
      ],
    })),
    createTransaction: vi.fn(() => Promise.resolve({
        data: { sender: 'C', receiver: 'D', amount: 20, hash: 'hash2', timestamp: '2023-01-01T00:01:00Z', block_id: 2 }
    })),
  },
  notificationApi: {
    sendLineNotification: vi.fn(() => Promise.resolve({ message: 'Sent' })),
  },
}));


// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/login', name: 'Login', component: { template: '<div>Login</div>' } }],
});

// Mock Pinia store with isAuthenticated = true
const authenticatedPinia = createTestingPinia({
  createSpy: vi.fn,
  initialState: {
    auth: {
      token: 'mock-jwt-token',
    },
  },
});

describe('DashboardView - Product and Order Cards', () => {
  it('displays products after fetching', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true, // Stub Chart.js components
          Line: true,
        },
      },
    });

    // Ensure auth store is recognized
    const authStore = useAuthStore();
    expect(authStore.isAuthenticated).toBe(true);

    // Wait for initial data fetches
    await vi.waitFor(() => expect(productApi.getProducts).toHaveBeenCalled());
    await wrapper.vm.$nextTick(); // Wait for DOM update

    const productCard = wrapper.find('.card:has(h2:text("商品管理"))');
    expect(productCard.exists()).toBe(true);
    expect(productCard.text()).toContain('Test Apple - $25.50');
    expect(productCard.text()).toContain('Test Orange - $30.00');
    expect(productCard.text()).not.toContain('載入中...');
  });

  it('displays orders after fetching', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true,
          Line: true,
        },
      },
    });

    await vi.waitFor(() => expect(orderApi.getOrders).toHaveBeenCalled());
    await wrapper.vm.$nextTick();

    const orderCard = wrapper.find('.card:has(h2:text("訂單歷史"))');
    expect(orderCard.exists()).toBe(true);
    expect(orderCard.text()).toContain('訂單 #1 - $51.00 (狀態: completed)');
    expect(orderCard.text()).toContain('訂單 #2 - $30.00 (狀態: pending)');
    expect(orderCard.text()).not.toContain('載入中...');
  });

  it('displays financial transactions after fetching', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true,
          Line: true,
        },
      },
    });

    await vi.waitFor(() => expect(financialApi.getTransactions).toHaveBeenCalled());
    await wrapper.vm.$nextTick();

    const financialCard = wrapper.find('.card:has(h2:text("財務帳務與金流"))');
    expect(financialCard.exists()).toBe(true);
    expect(financialCard.text()).toContain('交易ID: txn1... - $100.00 (completed)');
    expect(financialCard.text()).not.toContain('載入中...');
  });

  it('displays IoT data and chart after fetching', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true,
          Line: { template: '<canvas class="mock-line-chart"></canvas>' }, // Stub Line with canvas
        },
      },
    });

    await vi.waitFor(() => expect(iotApi.getIoTData).toHaveBeenCalled());
    await wrapper.vm.$nextTick();

    const iotCard = wrapper.find('.card:has(h2:text("IoT 農場監測"))');
    expect(iotCard.exists()).toBe(true);
    expect(iotCard.text()).toContain('設備ID: sensor-001');
    expect(iotCard.text()).toContain('溫度: 21.0°C');
    expect(iotCard.text()).toContain('濕度: 51.0%');
    expect(iotCard.find('.mock-line-chart').exists()).toBe(true);
    expect(iotCard.text()).not.toContain('載入中...');
  });

  it('displays blockchain transactions after fetching', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true,
          Line: true,
        },
      },
    });

    await vi.waitFor(() => expect(blockchainApi.getTransactions).toHaveBeenCalled());
    await wrapper.vm.$nextTick();

    const blockchainCard = wrapper.find('.card:has(h2:text("區塊鏈交易記錄"))');
    expect(blockchainCard.exists()).toBe(true);
    expect(blockchainCard.text()).toContain('Tx: hash1... | $10.00 | From: A');
    expect(blockchainCard.text()).not.toContain('載入中...');
  });

  it('creates a mock blockchain transaction when button is clicked', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true,
          Line: true,
        },
      },
    });

    // Mock both get and create calls
    blockchainApi.createTransaction.mockResolvedValueOnce({
        sender: 'NewSender', receiver: 'NewReceiver', amount: 50.00, hash: 'newhash', timestamp: '2023-01-02T00:00:00Z', block_id: 3
    });
    blockchainApi.getTransactions.mockResolvedValueOnce({
        data: [
            { sender: 'NewSender', receiver: 'NewReceiver', amount: 50.00, hash: 'newhash', timestamp: '2023-01-02T00:00:00Z', block_id: 3 },
            { sender: 'A', receiver: 'B', amount: 10, hash: 'hash1', timestamp: '2023-01-01T00:00:00Z', block_id: 1 },
        ],
    });


    const blockchainCard = wrapper.find('.card:has(h2:text("區塊鏈交易記錄"))');
    const createButton = blockchainCard.find('button:text("新增模擬交易")');
    await createButton.trigger('click');

    expect(blockchainApi.createTransaction).toHaveBeenCalled();
    expect(wrapper.vm.$toast.success).toHaveBeenCalledWith('已新增模擬區塊鏈交易！');
    
    // Check if the list is updated
    await vi.waitFor(() => expect(blockchainApi.getTransactions).toHaveBeenCalledTimes(2)); // Initial load + refresh
    expect(blockchainCard.text()).toContain('Tx: newhash... | $50.00 | From: NewSender');
  });


  it('sends LINE notification with dynamic user ID', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true,
          Line: true,
        },
      },
    });

    const lineCard = wrapper.find('.card:has(h2:text("LINE 通知測試"))');
    const userIdInput = lineCard.find('input[type="text"]');
    const sendButton = lineCard.find('button:text("發送 LINE 通知")');

    await userIdInput.setValue('U123456789abcdef123456789abcdef12'); // Valid mock ID
    await sendButton.trigger('click');

    expect(notificationApi.sendLineNotification).toHaveBeenCalledWith(
      'U123456789abcdef123456789abcdef12',
      expect.stringContaining('AgriBridge 提醒: 您有一筆新訂單待處理') // Message format
    );
    expect(wrapper.vm.$toast.success).toHaveBeenCalledWith(
      expect.stringContaining('LINE 通知已發送（模擬）')
    );
  });

  it('shows error if LINE user ID is empty or default mock ID', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          router,
          authenticatedPinia,
        ],
        mocks: {
          $toast: {
            success: vi.fn(),
            error: vi.fn(),
            info: vi.fn(),
          },
        },
        stubs: {
          Bar: true,
          Line: true,
        },
      },
    });

    const lineCard = wrapper.find('.card:has(h2:text("LINE 通知測試"))');
    const userIdInput = lineCard.find('input[type="text"]');
    const sendButton = lineCard.find('button:text("發送 LINE 通知")');

    // Test with empty ID
    await userIdInput.setValue('');
    await sendButton.trigger('click');
    expect(wrapper.vm.$toast.error).toHaveBeenCalledWith('請輸入有效的 LINE 用戶ID。');

    // Test with default mock ID
    await userIdInput.setValue('Udeadbeefdeadbeefdeadbeefdeadbeef');
    await sendButton.trigger('click');
    expect(wrapper.vm.$toast.error).toHaveBeenCalledWith(expect.stringContaining('請輸入有效的 LINE 用戶ID'));
    
    expect(notificationApi.sendLineNotification).not.toHaveBeenCalled(); // Should not call API
  });

});
