<template>
  <div class="dashboard-container p-4 sm:p-6 md:p-8 font-sans max-w-7xl mx-auto animate-fade-in">
    <header class="flex justify-between items-center mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-dark">AgriBridge 儀表板</h1>
      <div class="flex items-center space-x-4">
        <span class="text-gray-700 hidden sm:block">Hello, Farmer!</span>
        <button @click="handleLogout" class="px-4 py-2 bg-agriBlue text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition duration-300">
          登出
        </button>
      </div>
    </header>
    
    <div v-if="isLoading" class="flex justify-center items-center h-48">
      <p class="text-gray-500">載入數據中...</p>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- ESG Report Card -->
      <div class="card border-agriGreen">
        <h2 class="text-xl font-bold mb-4">農民 ESG 報告</h2>
        <div v-if="esgReport">
          <p><strong>農民：</strong> {{ esgReport.farmer_name }}</p>
          <p><strong>ESG 分數：</strong> <span class="text-3xl font-bold text-agriGreen">{{ esgReport.esg_score.toFixed(1) }}</span> / 100</p>
          <div class="mt-4">
            <h3 class="font-semibold">社會影響：</h3>
            <ul class="list-disc pl-5 text-sm">
              <li>公平貿易指數： {{ esgReport.social_impact.fair_trade_index }}</li>
              <li>社群參與： {{ esgReport.social_impact.community_engagement }}</li>
            </ul>
          </div>
          <div class="mt-2">
            <h3 class="font-semibold">環境影響：</h3>
            <ul class="list-disc pl-5 text-sm">
              <li>碳足跡減少： {{ esgReport.environmental_impact.carbon_footprint_reduction_tons }} tons CO2eq</li>
              <li>水資源效率： {{ esgReport.environmental_impact.water_usage_efficiency }}</li>
            </ul>
          </div>
        </div>
        <p v-else class="text-gray-500 italic">無法載入 ESG 報告。</p>
      </div>
      
      <!-- ESG Data Visualization Card -->
      <div class="card border-agriGreen md:col-span-2">
        <h2 class="text-xl font-bold mb-4">ESG 數據視覺化</h2>
        <div class="h-80">
          <Bar v-if="chartData.datasets[0].data.length > 0" :data="chartData" :options="chartOptions" />
          <p v-else class="text-gray-500 text-center py-20">數據不足以產生圖表。</p>
        </div>
      </div>

      <!-- Product Management Card -->
      <div class="card border-agriBlue">
        <h2 class="text-xl font-bold mb-4">商品管理</h2>
        <p class="text-gray-600">在此管理您的農產品上架、庫存和價格。</p>
        <button @click="fetchProducts" class="mt-4 px-4 py-2 bg-agriBlue text-white rounded-lg hover:bg-blue-600">
          <span v-if="!productsLoading">查看商品清單</span>
          <span v-else>載入中...</span>
        </button>
        <div v-if="products.length > 0" class="mt-4 text-sm max-h-32 overflow-y-auto border rounded p-2 bg-gray-50">
            <h4 class="font-semibold mb-1">最近商品:</h4>
            <ul class="list-disc pl-5">
                <li v-for="product in products" :key="product.id">
                    {{ product.name }} - ${{ product.price.toFixed(2) }} (農民ID: {{ product.farmer_id }})
                </li>
            </ul>
        </div>
        <p v-else-if="!productsLoading" class="text-gray-500 text-sm mt-2">無商品數據。</p>
      </div>

      <!-- Order History Card -->
      <div class="card border-agriBlue">
        <h2 class="text-xl font-bold mb-4">訂單歷史</h2>
        <p class="text-gray-600">查看您的所有訂單，管理訂單狀態和出貨。</p>
        <button @click="fetchOrders" class="mt-4 px-4 py-2 bg-agriBlue text-white rounded-lg hover:bg-blue-600">
          <span v-if="!ordersLoading">查看訂單</span>
          <span v-else>載入中...</span>
        </button>
        <div v-if="orders.length > 0" class="mt-4 text-sm max-h-32 overflow-y-auto border rounded p-2 bg-gray-50">
            <h4 class="font-semibold mb-1">最近訂單:</h4>
            <ul class="list-disc pl-5">
                <li v-for="order in orders" :key="order.id">
                    訂單 #{{ order.id }} - ${{ order.total_price.toFixed(2) }} (狀態: {{ order.status }})
                </li>
            </ul>
        </div>
        <p v-else-if="!ordersLoading" class="text-gray-500 text-sm mt-2">無訂單數據。</p>
      </div>

      <!-- Financial Ledger Card -->
      <div class="card border-agriGreen">
        <h2 class="text-xl font-bold mb-4">財務帳務與金流</h2>
        <p class="text-gray-600">此模組處理訂單、發票和金流串接（如藍新/Stripe），確保交易透明化。</p>
        <button @click="fetchTransactions" class="mt-4 px-4 py-2 bg-agriGreen text-white rounded-lg hover:bg-green-600">
            <span v-if="!transactionsLoading">查看交易記錄</span>
            <span v-else>載入中...</span>
        </button>
        <div v-if="transactions.length > 0" class="mt-4 text-sm max-h-32 overflow-y-auto border rounded p-2 bg-gray-50">
            <h4 class="font-semibold mb-1">最近交易:</h4>
            <ul class="list-disc pl-5">
                <li v-for="txn in transactions" :key="txn.transaction_id">
                    交易ID: {{ txn.transaction_id.substring(0, 8) }}... - ${{ txn.amount.toFixed(2) }} ({{ txn.status }})
                </li>
            </ul>
        </div>
        <p v-else-if="!transactionsLoading" class="text-gray-500 text-sm mt-2">無交易記錄。</p>
      </div>

      <!-- IoT Monitoring Card -->
      <div class="card border-agriGreen lg:col-span-2">
        <h2 class="text-xl font-bold mb-4">IoT 農場監測</h2>
        <p class="text-gray-600 mb-4">即時監測作物生長、土壤濕度等數據。</p>
        <button @click="fetchIoTData" class="mt-4 px-4 py-2 bg-agriGreen text-white rounded-lg hover:bg-green-600">
            <span v-if="!iotLoading">更新感測器數據與圖表</span>
            <span v-else>載入中...</span>
        </button>
        <div v-if="iotChartData.datasets[0].data.length > 0" class="h-64 sm:h-80 mt-4">
            <Line :data="iotChartData" :options="iotChartOptions" />
        </div>
        <div v-if="latestIoTData" class="mt-4 text-sm border rounded p-2 bg-gray-50">
            <h4 class="font-semibold mb-1">最新數據:</h4>
            <p>設備ID: {{ latestIoTData.device_id }}</p>
            <p v-if="latestIoTData.temperature !== undefined">溫度: {{ latestIoTData.temperature }}°C</p>
            <p v-if="latestIoTData.humidity !== undefined">濕度: {{ latestIoTData.humidity }}%</p>
            <p v-if="latestIoTData.soil_moisture !== undefined">土壤濕度: {{ latestIoTData.soil_moisture }}%</p>
            <p>更新時間: {{ new Date(latestIoTData.timestamp).toLocaleString() }}</p>
        </div>
        <p v-else-if="!iotLoading" class="text-gray-500 text-sm mt-2">無 IoT 數據或無法載入圖表。</p>
      </div>

      <!-- LINE Notification Demo Card -->
      <div class="card border-agriBlue">
        <h2 class="text-xl font-bold mb-4">LINE 通知測試</h2>
        <p class="text-gray-600 mb-2">點擊按鈕發送一個模擬的 LINE 通知。</p>
        <input
            type="text"
            v-model="lineUserIdInput"
            placeholder="輸入 LINE 用戶ID (U...)"
            class="shadow appearance-none border rounded-lg w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-agriBlue mb-3"
        />
        <button @click="sendLineNotification" :disabled="!lineUserIdInput" class="w-full px-4 py-2 bg-agriBlue text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed">
            發送 LINE 通知
        </button>
        <p class="text-gray-500 text-xs mt-2">請確保 LINE Bot 已配置並具備推播權限。</p>
      </div>

      <!-- Blockchain Transactions Card -->
      <div class="card border-agriGreen">
        <h2 class="text-xl font-bold mb-4">區塊鏈交易記錄</h2>
        <p class="text-gray-600">查看農產品供應鏈的模擬區塊鏈交易記錄。</p>
        <button @click="fetchBlockchainTransactions" class="mt-4 px-4 py-2 bg-agriGreen text-white rounded-lg hover:bg-green-600">
            <span v-if="!blockchainLoading">查看交易</span>
            <span v-else>載入中...</span>
        </button>
        <div v-if="blockchainTransactions.length > 0" class="mt-4 text-sm max-h-32 overflow-y-auto border rounded p-2 bg-gray-50">
            <h4 class="font-semibold mb-1">最近交易:</h4>
            <ul class="list-disc pl-5">
                <li v-for="txn in blockchainTransactions" :key="txn.hash">
                    Tx: {{ txn.hash.substring(0, 8) }}... | ${{ txn.amount.toFixed(2) }} | From: {{ txn.sender }}
                    <span v-if="txn.timestamp" class="text-gray-500"> ({{ new Date(txn.timestamp).toLocaleTimeString() }})</span>
                </li>
            </ul>
        </div>
        <p v-else-if="!blockchainLoading" class="text-gray-500 text-sm mt-2">無區塊鏈交易記錄。</p>
        <button @click="createMockBlockchainTransaction" class="mt-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600">
            新增模擬交易
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { useRouter } from 'vue-router';
import { Bar, Line } from 'vue-chartjs'; // Import Line for IoT chart
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';
import { esgApi, productApi, orderApi, financialApi, iotApi, notificationApi, blockchainApi } from '@/api';
import { useAuthStore } from '@/stores/auth';

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

const toast = useToast();
const router = useRouter();
const authStore = useAuthStore();

const esgReport = ref(null);
const isLoading = ref(true); // Overall dashboard loading

// New state for various modules
const products = ref([]);
const productsLoading = ref(false);
const orders = ref([]);
const ordersLoading = ref(false);
const transactions = ref([]);
const transactionsLoading = ref(false);
const latestIoTData = ref(null);
const iotLoading = ref(false);
const blockchainTransactions = ref([]);
const blockchainLoading = ref(false);
const lineUserIdInput = ref(import.meta.env.VITE_LINE_USER_ID || ''); // Pre-fill with .env or empty

// Chart.js data and options for ESG
const chartData = ref({
  labels: ['公平貿易指數', '社群參與', '碳足跡減少', '水資源效率'],
  datasets: [
    {
      label: 'ESG 影響力指標',
      backgroundColor: ['#22C55E', '#3B82F6', '#EF4444', '#F59E0B'],
      data: [],
      maxBarThickness: 50,
      borderRadius: 5,
    },
  ],
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      max: 1.0, // Scale for impact metrics (normalized)
      title: {
        display: true,
        text: '影響力分數 (0-1)',
      },
    },
    x: {
      grid: {
        display: false,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    title: {
      display: true,
      text: '農民永續發展指標',
      font: { size: 16, weight: 'bold' },
    },
  },
});

// Chart.js data and options for IoT
const iotChartData = ref({
  labels: [],
  datasets: [
    {
      label: '溫度 (°C)',
      borderColor: '#EF4444',
      backgroundColor: 'rgba(239, 68, 68, 0.2)',
      tension: 0.3,
      data: [],
      yAxisID: 'yTemp',
    },
    {
      label: '濕度 (%)',
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      tension: 0.3,
      data: [],
      yAxisID: 'yHumid',
    },
  ],
});

const iotChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'time', // Assuming timestamps are parsable
      time: {
        unit: 'minute',
        tooltipFormat: 'HH:mm',
        displayFormats: {
          minute: 'HH:mm',
        },
      },
      title: {
        display: true,
        text: '時間',
      },
    },
    yTemp: {
      type: 'linear',
      display: true,
      position: 'left',
      title: {
        display: true,
        text: '溫度 (°C)',
      },
      grid: {
        drawOnChartArea: true,
      },
    },
    yHumid: {
      type: 'linear',
      display: true,
      position: 'right',
      title: {
        display: true,
        text: '濕度 (%)',
      },
      grid: {
        drawOnChartArea: false, // Only draw grid lines for the left axis
      },
    },
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
    },
    title: {
      display: true,
      text: 'IoT 感測器歷史數據',
      font: { size: 16, weight: 'bold' },
    },
  },
});


const fetchESGReport = async () => {
  isLoading.value = true;
  try {
    const token = authStore.token;
    if (!token) {
      toast.error('未驗證身份，請重新登入。');
      router.push('/login');
      return;
    }
    const response = await esgApi.getEsgReport(1); // Fetch data for farmer_id = 1 (assuming tenant 1)
    esgReport.value = response.data;
  } catch (error) {
    console.error('Failed to fetch ESG report:', error);
    toast.error('無法載入 ESG 報告，請確認後端服務是否已啟動或登入狀態。');
    if (error.response && error.response.status === 401) {
      authStore.logout();
      router.push('/login');
    }
  } finally {
    isLoading.value = false;
  }
};

const fetchProducts = async () => {
    productsLoading.value = true;
    try {
        const response = await productApi.getProducts(5, 0); // Fetch top 5 products
        products.value = response.data;
    } catch (error) {
        console.error('Failed to fetch products:', error);
        toast.error('無法載入商品清單。');
    } finally {
        productsLoading.value = false;
    }
};

const fetchOrders = async () => {
    ordersLoading.value = true;
    try {
        const response = await orderApi.getOrders(5, 0); // Fetch top 5 orders
        orders.value = response.data;
    } catch (error) {
        console.error('Failed to fetch orders:', error);
        toast.error('無法載入訂單歷史。');
    } finally {
        ordersLoading.value = false;
    }
};

const fetchTransactions = async () => {
    transactionsLoading.value = true;
    try {
        const response = await financialApi.getTransactions(5, 0); // Fetch top 5 transactions
        transactions.value = response.data;
    } catch (error) {
        console.error('Failed to fetch transactions:', error);
        toast.error('無法載入交易記錄。');
    } finally {
        transactionsLoading.value = false;
    }
};

const fetchIoTData = async () => {
    iotLoading.value = true;
    try {
        const deviceId = 'farm-sensor-001'; 
        const response = await iotApi.getIoTData(deviceId, 20); // Fetch last 20 data points
        if (response.data && response.data.length > 0) {
            latestIoTData.value = response.data[response.data.length - 1]; // Get latest data point

            // Prepare data for Chart.js
            iotChartData.value.labels = response.data.map(d => new Date(d.timestamp));
            iotChartData.value.datasets[0].data = response.data.map(d => d.temperature);
            iotChartData.value.datasets[1].data = response.data.map(d => d.humidity);
        } else {
            iotChartData.value.labels = [];
            iotChartData.value.datasets[0].data = [];
            iotChartData.value.datasets[1].data = [];
            latestIoTData.value = null;
        }
    } catch (error) {
        console.error('Failed to fetch IoT data:', error);
        toast.error('無法載入 IoT 數據或圖表。');
    } finally {
        iotLoading.value = false;
    }
};

const fetchBlockchainTransactions = async () => {
    blockchainLoading.value = true;
    try {
        const response = await blockchainApi.getTransactions(5); // Fetch top 5 blockchain transactions
        blockchainTransactions.value = response.data;
    } catch (error) {
        console.error('Failed to fetch blockchain transactions:', error);
        toast.error('無法載入區塊鏈交易記錄。');
    } finally {
        blockchainLoading.value = false;
    }
};

const createMockBlockchainTransaction = async () => {
    try {
        const mockTransaction = {
            sender: `Farmer_${Math.floor(Math.random() * 100)}`,
            receiver: `Buyer_${Math.floor(Math.random() * 100)}`,
            amount: parseFloat((Math.random() * 1000).toFixed(2)),
            data: `Sale of produce on ${new Date().toLocaleDateString()}`
        };
        await blockchainApi.createTransaction(mockTransaction);
        toast.success('已新增模擬區塊鏈交易！');
        fetchBlockchainTransactions(); // Refresh the list
    } catch (error) {
        console.error('Failed to create mock blockchain transaction:', error);
        toast.error('新增模擬區塊鏈交易失敗。');
    }
};


const handleLogout = () => {
  authStore.logout();
  router.push('/login');
  toast.success('您已成功登出。');
};

const sendLineNotification = async () => {
  if (!lineUserIdInput.value || lineUserIdInput.value === 'Udeadbeefdeadbeefdeadbeefdeadbeef') {
    toast.error('請輸入有效的 LINE 用戶ID，或更新 .env 中的 LINE_USER_ID。');
    return;
  }
  try {
    // This calls the mock frontend-facing endpoint in FastAPI
    await notificationApi.sendLineNotification(lineUserIdInput.value, `AgriBridge 提醒: 您有一筆新訂單待處理，訂單金額 $${(Math.random() * 500 + 100).toFixed(2)}。`);
    toast.success('LINE 通知已發送（模擬）。請檢查後端控制台輸出和您的 LINE 裝置。');
  } catch (error) {
    console.error('Failed to send LINE notification:', error);
    toast.error('LINE 通知發送失敗，請檢查後端設定或網路連接。');
  }
};


// Watch for changes in esgReport and update chart data
watch(esgReport, (newReport) => {
  if (newReport) {
    chartData.value.datasets[0].data = [
      newReport.social_impact.fair_trade_index,
      newReport.social_impact.community_engagement === 'High' ? 0.9 : 0.5,
      // Normalize carbon reduction for the chart (example)
      newReport.environmental_impact.carbon_footprint_reduction_tons / 5, # Normalize for 0-1 scale, assuming max 5 tons
      newReport.environmental_impact.water_usage_efficiency === 'Moderate' ? 0.7 : 0.4,
    ];
  }
}, { immediate: true });

onMounted(() => {
  // Check auth status on mount
  if (!authStore.isAuthenticated) {
    router.push('/login');
    toast.info('請登入以繼續。');
  } else {
    fetchESGReport();
    // Pre-fetch other module data on dashboard load for better demo
    fetchProducts();
    fetchOrders();
    fetchTransactions();
    fetchIoTData();
    fetchBlockchainTransactions();
  }
});
</script>

<style scoped>
.card {
  @apply bg-white p-6 rounded-lg shadow-lg transition-transform transform hover:scale-105;
}
.border-agriGreen {
  @apply border-t-4 border-agriGreen;
}
.border-agriBlue {
  @apply border-t-4 border-agriBlue;
}
</style>
