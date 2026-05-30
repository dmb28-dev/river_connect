import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({ baseURL: `${API_URL}/api` });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
};

export const vesselsApi = {
  list: () => api.get('/vessels'),
  get: (id) => api.get(`/vessels/${id}`),
  telemetry: (id) => api.get(`/vessels/${id}/telemetry`),
  route: (id) => api.get(`/vessels/${id}/route`),
};

export const notificationsApi = {
  list: (type) => api.get('/notifications', { params: type ? { notification_type: type } : {} }),
  create: (data) => api.post('/notifications', data),
  emergency: (data) => api.post('/notifications/emergency', data),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
};

export const emergencyApi = {
  create: (data) => api.post('/emergency', data),
  list: (status) => api.get('/emergency', { params: status ? { status_filter: status } : {} }),
  updateStatus: (id, data) => api.patch(`/emergency/${id}/status`, data),
};

export default api;
