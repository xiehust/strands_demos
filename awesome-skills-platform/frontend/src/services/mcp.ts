/**
 * MCP Servers API service
 */
import { apiClient } from '../lib/api';
import type { MCPServer } from '../types';

export interface CreateMCPServerRequest {
  name: string;
  description?: string;
  connectionType: 'stdio' | 'sse' | 'http';
  endpoint: string;
  config?: Record<string, any>;
}

export interface UpdateMCPServerRequest {
  name?: string;
  description?: string;
  connectionType?: 'stdio' | 'sse' | 'http';
  endpoint?: string;
  config?: Record<string, any>;
}

export const mcpApi = {
  /**
   * Get all MCP servers
   */
  async list(): Promise<MCPServer[]> {
    const response = await apiClient.get<MCPServer[]>('/api/mcp');
    return response.data;
  },

  /**
   * Get an MCP server by ID
   */
  async get(id: string): Promise<MCPServer> {
    const response = await apiClient.get<MCPServer>(`/api/mcp/${id}`);
    return response.data;
  },

  /**
   * Create a new MCP server
   */
  async create(data: CreateMCPServerRequest): Promise<MCPServer> {
    const response = await apiClient.post<MCPServer>('/api/mcp', data);
    return response.data;
  },

  /**
   * Update an MCP server
   */
  async update(id: string, data: UpdateMCPServerRequest): Promise<MCPServer> {
    const response = await apiClient.put<MCPServer>(`/api/mcp/${id}`, data);
    return response.data;
  },

  /**
   * Delete an MCP server
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/mcp/${id}`);
  },
};
