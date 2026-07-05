import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient();

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
});

client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auralis_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auralis_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const chatClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 120000,
});

chatClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auralis_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

chatClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auralis_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export async function chatRequest<T>(reqBody: unknown, retries = 2): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const { data } = await chatClient.post<T>('/chat', reqBody);
      return data;
    } catch (err) {
      lastError = err;
      if (attempt < retries) {
        const delay = Math.min(1000 * 2 ** attempt, 8000);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }
  throw lastError;
}

export default client;
