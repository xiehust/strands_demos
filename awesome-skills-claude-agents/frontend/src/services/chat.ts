import type { ChatRequest, StreamEvent, ChatSession } from '../types';
import api from './api';

export const chatService = {
  // Stream chat messages using SSE
  streamChat(
    request: ChatRequest,
    onMessage: (event: StreamEvent) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): () => void {
    const controller = new AbortController();

    fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        agent_id: request.agentId,
        message: request.message,
        session_id: request.sessionId,
        enable_skills: request.enableSkills,
        enable_mcp: request.enableMCP,
      }),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            onComplete();
            break;
          }

          buffer += decoder.decode(value, { stream: true });

          // Process SSE events
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                onComplete();
                return;
              }
              try {
                const event: StreamEvent = JSON.parse(data);
                onMessage(event);
              } catch {
                // Ignore parse errors for incomplete data
              }
            }
          }
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          onError(error);
        }
      });

    // Return cleanup function
    return () => {
      controller.abort();
    };
  },

  // List chat sessions
  async listSessions(agentId?: string): Promise<ChatSession[]> {
    const params = agentId ? { agent_id: agentId } : {};
    const response = await api.get<ChatSession[]>('/chat/sessions', { params });
    return response.data;
  },

  // Delete chat session
  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/chat/sessions/${sessionId}`);
  },
};
