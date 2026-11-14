import axios from 'axios';

import { API_BASE_URL } from './api';

export { API_BASE_URL };
export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export const authClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});
