import api from './api';
import type { Skill, SkillCreateRequest, SyncResult, StreamEvent } from '../types';

// Request type for skill generation with agent
export interface SkillGenerateWithAgentRequest {
  skillName: string;
  skillDescription: string;
  sessionId?: string;
  message?: string;
  model?: string;
}

// Convert snake_case response to camelCase
const toCamelCase = (data: Record<string, unknown>): Skill => {
  return {
    id: data.id as string,
    name: data.name as string,
    description: data.description as string,
    s3Location: data.s3_location as string | undefined,
    createdBy: data.created_by as string,
    createdAt: data.created_at as string,
    updatedAt: data.updated_at as string,
    version: data.version as string,
    isSystem: data.is_system as boolean,
  };
};

// Convert sync result snake_case to camelCase
const toSyncResultCamelCase = (data: Record<string, unknown>): SyncResult => {
  return {
    added: (data.added as string[]) || [],
    updated: (data.updated as string[]) || [],
    removed: (data.removed as string[]) || [],
    errors: (data.errors as { skill: string; error: string }[]) || [],
    totalLocal: (data.total_local as number) || 0,
    totalS3: (data.total_s3 as number) || 0,
    totalDb: (data.total_db as number) || 0,
  };
};

export const skillsService = {
  // List all skills
  async list(): Promise<Skill[]> {
    const response = await api.get<Record<string, unknown>[]>('/skills');
    return response.data.map(toCamelCase);
  },

  // Get skill by ID
  async get(id: string): Promise<Skill> {
    const response = await api.get<Record<string, unknown>>(`/skills/${id}`);
    return toCamelCase(response.data);
  },

  // Upload skill ZIP
  async upload(file: File, name: string): Promise<Skill> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);

    const response = await api.post<Record<string, unknown>>('/skills/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return toCamelCase(response.data);
  },

  // Refresh/sync skills between local, S3 and database
  async refresh(): Promise<SyncResult> {
    const response = await api.post<Record<string, unknown>>('/skills/refresh');
    return toSyncResultCamelCase(response.data);
  },

  // Generate skill with AI
  async generate(data: SkillCreateRequest): Promise<Skill> {
    const response = await api.post<Record<string, unknown>>('/skills/generate', data);
    return toCamelCase(response.data);
  },

  // Delete skill
  async delete(id: string): Promise<void> {
    await api.delete(`/skills/${id}`);
  },

  // List system skills
  async listSystem(): Promise<Skill[]> {
    const response = await api.get<Record<string, unknown>[]>('/skills/system');
    return response.data.map(toCamelCase);
  },

  // Stream skill generation with agent
  streamGenerateWithAgent(
    request: SkillGenerateWithAgentRequest,
    onMessage: (event: StreamEvent) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): () => void {
    const controller = new AbortController();

    fetch('/api/skills/generate-with-agent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        skill_name: request.skillName,
        skill_description: request.skillDescription,
        session_id: request.sessionId,
        message: request.message,
        model: request.model,
      }),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          try {
            const errorData = await response.json();
            const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;
            throw new Error(errorMessage);
          } catch {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
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

  // Finalize skill creation (sync to S3 and save to DB)
  async finalize(skillName: string): Promise<Skill> {
    const response = await api.post<Record<string, unknown>>('/skills/finalize', {
      skill_name: skillName,
    });
    return toCamelCase(response.data);
  },
};
