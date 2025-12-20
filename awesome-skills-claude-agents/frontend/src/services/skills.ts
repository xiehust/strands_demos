import api from './api';
import type { Skill, SkillCreateRequest } from '../types';

export const skillsService = {
  // List all skills
  async list(): Promise<Skill[]> {
    const response = await api.get<Skill[]>('/skills');
    return response.data;
  },

  // Get skill by ID
  async get(id: string): Promise<Skill> {
    const response = await api.get<Skill>(`/skills/${id}`);
    return response.data;
  },

  // Upload skill ZIP
  async upload(file: File, name: string): Promise<Skill> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);

    const response = await api.post<Skill>('/skills/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Generate skill with AI
  async generate(data: SkillCreateRequest): Promise<Skill> {
    const response = await api.post<Skill>('/skills/generate', data);
    return response.data;
  },

  // Delete skill
  async delete(id: string): Promise<void> {
    await api.delete(`/skills/${id}`);
  },

  // List system skills
  async listSystem(): Promise<Skill[]> {
    const response = await api.get<Skill[]>('/skills/system');
    return response.data;
  },
};
