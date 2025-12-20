/**
 * Chat API service with streaming support
 */
import { apiClient } from '../lib/api';
import type { ChatRequest, ChatResponse, Conversation } from '../types';

export interface StreamEvent {
  type: 'start' | 'text' | 'thinking' | 'tool_use' | 'tool_result' | 'done' | 'error';
  conversationId?: string;
  agentId?: string;
  content?: string;
  tool?: any;
  result?: any;
  modelId?: string;
  error?: string;
}

export type StreamCallback = (event: StreamEvent) => void;

/**
 * Send a message and receive a streaming response using Server-Sent Events (SSE).
 */
export async function streamChatMessage(
  request: ChatRequest,
  onEvent: StreamCallback,
  signal?: AbortSignal
): Promise<void> {
  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); // Remove "data: " prefix
          try {
            const event: StreamEvent = JSON.parse(data);
            onEvent(event);
          } catch (e) {
            console.error('Failed to parse SSE event:', data, e);
          }
        }
      }
    }
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.log('Stream aborted by user');
    } else {
      console.error('Stream error:', error);
      onEvent({
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }
}

export const chatApi = {
  /**
   * Send a message to an agent (non-streaming)
   */
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/api/chat', data);
    return response.data;
  },

  /**
   * Send a message with streaming response
   */
  streamMessage: streamChatMessage,

  /**
   * Get all conversations
   */
  getConversations: async (): Promise<Conversation[]> => {
    const response = await apiClient.get<Conversation[]>('/api/chat/conversations');
    return response.data;
  },

  /**
   * Get a specific conversation by ID
   */
  getConversation: async (conversationId: string): Promise<Conversation> => {
    const response = await apiClient.get<Conversation>(`/api/chat/conversations/${conversationId}`);
    return response.data;
  },

  /**
   * Delete a conversation
   */
  deleteConversation: async (conversationId: string): Promise<void> => {
    await apiClient.delete(`/api/chat/conversations/${conversationId}`);
  },

  /**
   * Clear a conversation
   */
  clearConversation: async (conversationId: string): Promise<void> => {
    await apiClient.post(`/api/chat/conversations/${conversationId}/clear`);
  },
};
