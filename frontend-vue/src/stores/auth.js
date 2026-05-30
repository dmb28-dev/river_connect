import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from '../services/api';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);

  const isCrew = computed(() => user.value?.role === 'crew');

  async function login(email, password) {
    const { data } = await authApi.login(email, password);
    localStorage.setItem('access_token', data.access_token);
    const me = await authApi.me();
    user.value = me.data;
  }

  async function init() {
    if (localStorage.getItem('access_token')) {
      try {
        const me = await authApi.me();
        user.value = me.data;
      } catch {
        localStorage.clear();
      }
    }
  }

  function logout() {
    localStorage.clear();
    user.value = null;
  }

  return { user, isCrew, login, init, logout };
});
