<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-slate-900 to-blue-950">
    <form @submit.prevent="handleLogin" class="w-full max-w-md bg-slate-800 rounded-2xl p-8">
      <h1 class="text-2xl font-bold text-center mb-6">River Connect (Vue)</h1>
      <input v-model="email" type="email" placeholder="Email" class="w-full p-3 rounded-lg bg-slate-700 mb-3" required />
      <input v-model="password" type="password" placeholder="Пароль" class="w-full p-3 rounded-lg bg-slate-700 mb-3" required />
      <p v-if="error" class="text-emergency text-sm mb-3">{{ error }}</p>
      <button type="submit" class="w-full py-3 bg-primary rounded-lg font-semibold" :disabled="loading">
        {{ loading ? 'Вход...' : 'Войти' }}
      </button>
      <div class="mt-4 flex gap-2">
        <button type="button" @click="email='passenger1@test.com'; password='password123'" class="text-xs px-2 py-1 bg-slate-700 rounded">Пассажир</button>
        <button type="button" @click="email='captain@ship.com'; password='captain123'" class="text-xs px-2 py-1 bg-slate-700 rounded">Капитан</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const email = ref('passenger1@test.com');
const password = ref('password123');
const error = ref('');
const loading = ref(false);
const auth = useAuthStore();
const router = useRouter();

async function handleLogin() {
  loading.value = true;
  error.value = '';
  try {
    await auth.login(email.value, password.value);
    router.push('/');
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка входа';
  } finally {
    loading.value = false;
  }
}
</script>
