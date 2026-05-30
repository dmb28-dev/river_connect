import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;

export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
};

export const vesselsApi = {
  get: (id) => api.get(`/vessels/${id}`),
  route: (id) => api.get(`/vessels/${id}/route`),
  telemetry: (id) => api.get(`/vessels/${id}/telemetry`),
};

export const notificationsApi = {
  list: () => api.get('/notifications'),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
};

export const emergencyApi = {
  create: (data) => api.post('/emergency', data),
  list: () => api.get('/emergency'),
  updateStatus: (id, data) => api.patch(`/emergency/${id}/status`, data),
};
