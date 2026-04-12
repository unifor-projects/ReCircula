import axios from 'axios';

const baseURL =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV !== 'production' ? 'http://localhost:8000' : undefined);

if (!baseURL) {
  throw new Error('NEXT_PUBLIC_API_URL must be defined in production builds');
}

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = sessionStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export default api;
