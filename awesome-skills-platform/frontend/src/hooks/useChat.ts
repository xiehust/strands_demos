/**
 * Custom hook for managing chat state with streaming support
 */
import { useState, useCallback, useRef } from 'react';
import { streamChatMessage, type StreamEvent } from '../services/chat';
import type { ChatMessage } from '../types';

export interface UseChatOptions {
  agentId: string;
  conversationId?: string;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  cancelStream: () => void;
  clearMessages: () => void;
  conversationId: string | null;
}

export function useChat({ agentId, conversationId: initialConversationId }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(initialConversationId || null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const currentMessageRef = useRef<string>('');

  const sendMessage = useCallback(
    async (content: string) => {
      if (isStreaming) {
        console.warn('Already streaming a message');
        return;
      }

      // Add user message
      const userMessage: ChatMessage = {
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsStreaming(true);
      setError(null);
      currentMessageRef.current = '';

      // Create abort controller for cancellation
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      try {
        await streamChatMessage(
          {
            agentId,
            message: content,
            conversationId: conversationId || undefined,
          },
          (event: StreamEvent) => {
            switch (event.type) {
              case 'start':
                // Set conversation ID from server
                if (event.conversationId) {
                  setConversationId(event.conversationId);
                }
                // Add empty assistant message that will be updated
                setMessages((prev) => [
                  ...prev,
                  {
                    role: 'assistant',
                    content: '',
                    timestamp: new Date().toISOString(),
                  },
                ]);
                break;

              case 'text':
                // Accumulate text chunks
                if (event.content) {
                  currentMessageRef.current += event.content;
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.role === 'assistant') {
                      lastMessage.content = currentMessageRef.current;
                    }
                    return newMessages;
                  });
                }
                break;

              case 'thinking':
                // Add thinking content
                if (event.content) {
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.role === 'assistant') {
                      if (!lastMessage.thinking) {
                        lastMessage.thinking = [];
                      }
                      lastMessage.thinking.push(event.content!);
                    }
                    return newMessages;
                  });
                }
                break;

              case 'tool_use':
                // Handle tool use event
                console.log('Tool use:', event.tool);
                break;

              case 'tool_result':
                // Handle tool result event
                console.log('Tool result:', event.result);
                break;

              case 'done':
                // Stream complete
                setIsStreaming(false);
                currentMessageRef.current = '';
                break;

              case 'error':
                // Handle error
                setError(event.error || 'Unknown error occurred');
                setIsStreaming(false);
                currentMessageRef.current = '';
                break;
            }
          },
          abortController.signal
        );
      } catch (err) {
        console.error('Failed to send message:', err);
        setError(err instanceof Error ? err.message : 'Failed to send message');
        setIsStreaming(false);
      } finally {
        abortControllerRef.current = null;
      }
    },
    [agentId, conversationId, isStreaming]
  );

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    currentMessageRef.current = '';
  }, []);

  return {
    messages,
    isStreaming,
    error,
    sendMessage,
    cancelStream,
    clearMessages,
    conversationId,
  };
}
