<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 p-4">
    <div class="bg-white p-8 rounded-lg shadow-2xl w-full max-w-md animate-fade-in">
      <h2 class="text-3xl font-bold text-center mb-6 text-dark">AgriBridge 登入</h2>
      <p class="text-center text-gray-600 mb-6">請使用預設帳號登入進行演示。</p>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label for="username" class="block text-gray-700 text-sm font-bold mb-2">用戶名:</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="shadow appearance-none border rounded-lg w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-agriBlue"
            placeholder="agribridge_user"
            required
          />
        </div>
        <div class="mb-6">
          <label for="password" class="block text-gray-700 text-sm font-bold mb-2">密碼:</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="shadow appearance-none border rounded-lg w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline focus:border-agriBlue"
            placeholder="password"
            required
          />
        </div>
        <button
          type="submit"
          :disabled="isLoggingIn"
          class="w-full bg-agriGreen text-white font-bold py-3 px-4 rounded-lg hover:bg-green-600 transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!isLoggingIn">登入</span>
          <span v-else>登入中...</span>
        </button>
      </form>
      <div class="mt-6 text-center text-gray-500 text-sm">
        <p>（預設帳號：`agribridge_user` / 密碼：`password`）</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useAuthStore } from '@/stores/auth'; // Import Pinia auth store

const username = ref('');
const password = ref('');
const isLoggingIn = ref(false);

const router = useRouter();
const toast = useToast();
const authStore = useAuthStore(); // Access the auth store

const handleLogin = async () => {
  isLoggingIn.value = true;
  try {
    await authStore.login(username.value, password.value);
    toast.success('登入成功！歡迎使用 AgriBridge。');
    router.push('/dashboard');
  } catch (error) {
    console.error('Login failed:', error);
    toast.error('登入失敗，請檢查用戶名或密碼。');
  } finally {
    isLoggingIn.value = false;
  }
};
</script>
