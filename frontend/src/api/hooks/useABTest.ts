import { useQuery } from '@tanstack/react-query';
import client from '../client';
import type { ABTestResults } from '../../types/api';

export const useABTestResults = () => {
  return useQuery({
    queryKey: ['abTestResults'],
    queryFn: async () => {
      const { data } = await client.get<ABTestResults>('/ab-test/results');
      return data;
    },
  });
};
