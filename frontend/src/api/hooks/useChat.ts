import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import client from '../client';
import type { ChatResponse, ChatRequest, Message } from '../../types/api';

export const useChat = (sessionId: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const req: ChatRequest = { session_id: sessionId, message };
      const { data } = await client.post<ChatResponse>('/chat', req);
      return data;
    },
    onSuccess: (data) => {
      setLastResponse(data);
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
  });

  const sendMessage = (message: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    chatMutation.mutate(message);
  };

  return {
    messages,
    sendMessage,
    clearMessages: () => {
      setMessages([]);
      setLastResponse(null);
    },
    isLoading: chatMutation.isPending,
    lastResponse,
  };
};
