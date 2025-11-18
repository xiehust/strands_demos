/**
 * Agents API service
 */
import { apiClient } from '../lib/api';
import type { Agent } from '../types';

export interface CreateAgentRequest {
  name: string;
  description?: string;
  modelId: string;
  temperature?: number;
  maxTokens?: number;
  thinkingEnabled?: boolean;
  thinkingBudget?: number;
  systemPrompt?: string;
  skillIds?: string[];
  mcpIds?: string[];
  status?: 'active' | 'inactive';
}

export interface UpdateAgentRequest {
  name?: string;
  description?: string;
  modelId?: string;
  temperature?: number;
  maxTokens?: number;
  thinkingEnabled?: boolean;
  thinkingBudget?: number;
  systemPrompt?: string;
  skillIds?: string[];
  mcpIds?: string[];
  status?: 'active' | 'inactive';
}

export const agentsApi = {
  /**
   * Get all agents
   */
  async list(): Promise<Agent[]> {
    const response = await apiClient.get<Agent[]>('/api/agents');
    return response.data;
  },

  /**
   * Get an agent by ID
   */
  async get(id: string): Promise<Agent> {
    const response = await apiClient.get<Agent>(`/api/agents/${id}`);
    return response.data;
  },

  /**
   * Create a new agent
   */
  async create(data: CreateAgentRequest): Promise<Agent> {
    const response = await apiClient.post<Agent>('/api/agents', data);
    return response.data;
  },

  /**
   * Update an agent
   */
  async update(id: string, data: UpdateAgentRequest): Promise<Agent> {
    const response = await apiClient.put<Agent>(`/api/agents/${id}`, data);
    return response.data;
  },

  /**
   * Delete an agent
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/agents/${id}`);
  },
};
