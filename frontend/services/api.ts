import axios from 'axios';

// Em dev, sem NEXT_PUBLIC_API_URL, o backend é o mesmo host que serviu a página na porta 8000:
// funciona em localhost e pelo IP da rede (celular) sem editar o .env a cada troca de Wi-Fi.
function devBaseURL(): string {
  const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  return `http://${host}:8000`;
}

const baseURL =
  process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV !== 'production' ? devBaseURL() : undefined);

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
