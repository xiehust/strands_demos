import { describe, it, expect, vi, beforeEach } from 'vitest';
import { agentsApi } from './agents';
import { apiClient } from '../lib/api';

// Mock the API client
vi.mock('../lib/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('agentsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('list', () => {
    it('should fetch all agents', async () => {
      const mockAgents = [
        { id: '1', name: 'Agent 1', modelId: 'claude-3' },
        { id: '2', name: 'Agent 2', modelId: 'claude-3' },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockAgents });

      const result = await agentsApi.list();

      expect(apiClient.get).toHaveBeenCalledWith('/api/agents');
      expect(result).toEqual(mockAgents);
    });

    it('should return empty array when no agents exist', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      const result = await agentsApi.list();

      expect(result).toEqual([]);
    });
  });

  describe('get', () => {
    it('should fetch a single agent by ID', async () => {
      const mockAgent = { id: 'test-123', name: 'Test Agent', modelId: 'claude-3' };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockAgent });

      const result = await agentsApi.get('test-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/agents/test-123');
      expect(result).toEqual(mockAgent);
    });
  });

  describe('create', () => {
    it('should create a new agent', async () => {
      const newAgent = {
        name: 'New Agent',
        modelId: 'claude-3',
        temperature: 0.7,
      };

      const createdAgent = { id: 'new-123', ...newAgent };

      vi.mocked(apiClient.post).mockResolvedValue({ data: createdAgent });

      const result = await agentsApi.create(newAgent);

      expect(apiClient.post).toHaveBeenCalledWith('/api/agents', newAgent);
      expect(result).toEqual(createdAgent);
    });
  });

  describe('update', () => {
    it('should update an existing agent', async () => {
      const updates = { name: 'Updated Name', temperature: 0.8 };
      const updatedAgent = { id: 'agent-123', ...updates, modelId: 'claude-3' };

      vi.mocked(apiClient.put).mockResolvedValue({ data: updatedAgent });

      const result = await agentsApi.update('agent-123', updates);

      expect(apiClient.put).toHaveBeenCalledWith('/api/agents/agent-123', updates);
      expect(result).toEqual(updatedAgent);
    });
  });

  describe('delete', () => {
    it('should delete an agent', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({});

      await agentsApi.delete('agent-123');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/agents/agent-123');
    });
  });
});
