/**
 * Chat API service
 */
import { apiClient } from '../lib/api';
import type { ChatRequest, ChatResponse, Conversation } from '../types';

export const chatApi = {
  /**
   * Send a message to an agent
   */
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/api/chat', data);
    return response.data;
  },

  /**
   * Get all conversations
   */
  getConversations: async (): Promise<Conversation[]> => {
    const response = await apiClient.get<Conversation[]>('/api/conversations');
    return response.data;
  },

  /**
   * Get a specific conversation by ID
   */
  getConversation: async (conversationId: string): Promise<Conversation> => {
    const response = await apiClient.get<Conversation>(`/api/conversations/${conversationId}`);
    return response.data;
  },
};
