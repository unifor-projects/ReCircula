import axios from 'axios';

const baseURL =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV !== 'production' ? 'http://localhost:8000' : undefined);

// Only throw at runtime in the browser, never during SSR / static pre-rendering.
// The env var must be set when deploying to production.
if (typeof window !== 'undefined' && !baseURL) {
  throw new Error('NEXT_PUBLIC_API_URL must be defined in production builds');
}

export const API_BASE_URL = baseURL;

const api = axios.create({
  baseURL,
  withCredentials: true,
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
