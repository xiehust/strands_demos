import api from './api';
import type { MCPServer, MCPServerCreateRequest, MCPServerUpdateRequest } from '../types';

export const mcpService = {
  // List all MCP servers
  async list(): Promise<MCPServer[]> {
    const response = await api.get<MCPServer[]>('/mcp');
    return response.data;
  },

  // Get MCP server by ID
  async get(id: string): Promise<MCPServer> {
    const response = await api.get<MCPServer>(`/mcp/${id}`);
    return response.data;
  },

  // Create new MCP server
  async create(data: MCPServerCreateRequest): Promise<MCPServer> {
    const response = await api.post<MCPServer>('/mcp', data);
    return response.data;
  },

  // Update MCP server
  async update(id: string, data: MCPServerUpdateRequest): Promise<MCPServer> {
    const response = await api.put<MCPServer>(`/mcp/${id}`, data);
    return response.data;
  },

  // Delete MCP server
  async delete(id: string): Promise<void> {
    await api.delete(`/mcp/${id}`);
  },

  // Test MCP connection
  async testConnection(id: string): Promise<{ status: string; error?: string }> {
    const response = await api.post<{ status: string; error?: string }>(`/mcp/${id}/test`);
    return response.data;
  },
};
