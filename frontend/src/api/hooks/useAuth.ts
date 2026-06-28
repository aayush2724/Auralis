import { useMutation } from '@tanstack/react-query';
import client, { queryClient } from '../client';
import type { TokenResponse } from '../../types/api';

export const useLogin = () => {
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const { data } = await client.post<TokenResponse>('/auth/token', formData);
      localStorage.setItem('auralis_token', data.access_token);
      return data;
    },
  });
};

export const useLogout = () => {
  return () => {
    localStorage.removeItem('auralis_token');
    queryClient.clear();
    window.location.href = '/';
  };
};

export const useIsAuthenticated = () => {
  return !!localStorage.getItem('auralis_token');
};
