// Agent types
export interface Agent {
  id: string;
  name: string;
  description?: string;
  modelId: string;
  temperature: number;
  maxTokens: number;
  thinkingEnabled: boolean;
  thinkingBudget: number;
  systemPrompt?: string;
  skillIds: string[];
  mcpIds: string[];
  status: 'active' | 'inactive';
  createdAt: string;
  updatedAt: string;
}

// Skill types
export interface Skill {
  id: string;
  name: string;
  description: string;
  createdBy: string;
  createdAt: string;
  version: string;
  isSystem: boolean;
}

// MCP Server types
export interface MCPServer {
  id: string;
  name: string;
  description?: string;
  connectionType: 'stdio' | 'sse' | 'http';
  endpoint: string;
  status: 'online' | 'offline' | 'error';
  version?: string;
  agentCount?: number;
  config: Record<string, any>;
}

// Message types
export interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant';
  content: string;
  thinkingContent?: string;
  toolUses?: ToolUse[];
  timestamp: string;
}

export interface ToolUse {
  id: string;
  name: string;
  input: Record<string, any>;
  result?: string;
  status: 'pending' | 'success' | 'error';
}

// Conversation types
export interface Conversation {
  id: string;
  title: string;
  agentId: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

// Chat API types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  thinking?: string[];
  timestamp?: string;
}

export interface ChatRequest {
  agentId: string;
  message: string;
  conversationId?: string;
}

export interface ChatResponse {
  agentId: string;
  conversationId: string;
  message: string;
  thinking?: string[];
  modelId: string;
  stopReason?: string;
  timestamp: string;
}
