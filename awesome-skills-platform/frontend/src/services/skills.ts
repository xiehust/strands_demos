/**
 * Skills API service
 */
import { apiClient } from '../lib/api';
import type { Skill } from '../types';

export interface CreateSkillRequest {
  name: string;
  description: string;
  version?: string;
  isSystem?: boolean;
}

export const skillsApi = {
  /**
   * Get all skills
   */
  async list(): Promise<Skill[]> {
    const response = await apiClient.get<Skill[]>('/api/skills');
    return response.data;
  },

  /**
   * Get a skill by ID
   */
  async get(id: string): Promise<Skill> {
    const response = await apiClient.get<Skill>(`/api/skills/${id}`);
    return response.data;
  },

  /**
   * Create a new skill
   */
  async create(data: CreateSkillRequest): Promise<Skill> {
    const response = await apiClient.post<Skill>('/api/skills', data);
    return response.data;
  },

  /**
   * Delete a skill
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/skills/${id}`);
  },
};
