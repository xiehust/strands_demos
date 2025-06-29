import { RemoteAgent, AddAgentRequest, DeleteAgentRequest, InvokeStreamRequest, PreviewAgentRequest, PreviewAgentResponse } from '@/types';

export class ApiService {
  private baseUrl = '/api';

  async getRemoteAgents(): Promise<RemoteAgent[]> {
    try {
      const response = await fetch(`${this.baseUrl}/list_agents`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch remote agents:', error);
      throw error;
    }
  }

  async addAgent(request: AddAgentRequest): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/add_agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to add agent:', error);
      throw error;
    }
  }

  async deleteAgent(request: DeleteAgentRequest): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/delete_agent`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to delete agent:', error);
      throw error;
    }
  }

  async updateAgentEnabled(agentId: string, enabled: boolean): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/update_agent_enabled`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ agent_id: agentId, enabled }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to update agent enabled status:', error);
      throw error;
    }
  }

  async previewAgent(request: PreviewAgentRequest): Promise<PreviewAgentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/preview_agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to preview agent:', error);
      throw error;
    }
  }

  async invokeStream(
    request: InvokeStreamRequest,
    onMessage: (data: any) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<() => void> {
    let abortController: AbortController | null = null;
    
    try {
      abortController = new AbortController();
      
      const response = await fetch(`${this.baseUrl}/invoke_stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      const processStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              // Process any remaining buffer content
              if (buffer.trim()) {
                const lines = buffer.split('\n');
                for (const line of lines) {
                  if (line.trim() && line.startsWith('data: ')) {
                    try {
                      const data = JSON.parse(line.slice(6));
                      onMessage(data);
                    } catch (e) {
                      console.warn('Failed to parse final SSE data:', line);
                    }
                  }
                }
              }
              onComplete?.();
              break;
            }

            // Decode chunk immediately without buffering
            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;
            
            // Process complete lines immediately
            const lines = buffer.split('\n');
            // Keep the last incomplete line in buffer
            buffer = lines.pop() || '';

            // Process each complete line immediately
            for (const line of lines) {
              if (line.trim() && line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  // Call onMessage immediately for real-time streaming
                  onMessage(data);
                } catch (e) {
                  console.warn('Failed to parse SSE data:', line);
                }
              }
            }
          }
        } catch (error) {
          if (error instanceof Error && error.name === 'AbortError') {
            console.log('Stream was cancelled');
            return;
          }
          onError?.(error instanceof Error ? error : new Error('Stream reading failed'));
        } finally {
          reader.releaseLock();
        }
      };

      // Start processing stream immediately
      processStream();

      // Return a function to cancel the stream
      return () => {
        if (abortController) {
          abortController.abort();
        }
        reader.cancel();
      };
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was cancelled');
        return () => {};
      }
      onError?.(error instanceof Error ? error : new Error('Failed to start stream'));
      return () => {};
    }
  }
}

export const apiService = new ApiService();