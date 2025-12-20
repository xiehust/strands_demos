import api from './api';
import type { Agent, AgentCreateRequest, AgentUpdateRequest } from '../types';

export const agentsService = {
  // List all agents
  async list(): Promise<Agent[]> {
    const response = await api.get<Agent[]>('/agents');
    return response.data;
  },

  // Get agent by ID
  async get(id: string): Promise<Agent> {
    const response = await api.get<Agent>(`/agents/${id}`);
    return response.data;
  },

  // Create new agent
  async create(data: AgentCreateRequest): Promise<Agent> {
    const response = await api.post<Agent>('/agents', data);
    return response.data;
  },

  // Update agent
  async update(id: string, data: AgentUpdateRequest): Promise<Agent> {
    const response = await api.put<Agent>(`/agents/${id}`, data);
    return response.data;
  },

  // Delete agent
  async delete(id: string): Promise<void> {
    await api.delete(`/agents/${id}`);
  },

  // Get default agent
  async getDefault(): Promise<Agent> {
    const response = await api.get<Agent>('/agents/default');
    return response.data;
  },
};
