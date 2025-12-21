// Agent Types
export interface Agent {
  id: string;
  name: string;
  description?: string;
  model?: string;
  permissionMode: 'default' | 'acceptEdits' | 'plan' | 'bypassPermissions';
  systemPrompt?: string;
  allowedTools: string[];
  skillIds: string[];
  mcpIds: string[];
  workingDirectory: string;
  enableBashTool: boolean;
  enableFileTools: boolean;
  enableWebTools: boolean;
  enableToolLogging: boolean;
  enableSafetyChecks: boolean;
  status: 'active' | 'inactive';
  createdAt: string;
  updatedAt: string;
}

export interface AgentCreateRequest {
  name: string;
  description?: string;
  model?: string;
  permissionMode?: 'default' | 'acceptEdits' | 'plan' | 'bypassPermissions';
  systemPrompt?: string;
  skillIds?: string[];
  mcpIds?: string[];
  allowedTools?: string[];
  enableBashTool?: boolean;
  enableFileTools?: boolean;
  enableWebTools?: boolean;
}

export interface AgentUpdateRequest extends Partial<AgentCreateRequest> {}

// Skill Types
export interface Skill {
  id: string;
  name: string;
  description: string;
  s3Location?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  version: string;
  isSystem: boolean;
}

export interface SkillCreateRequest {
  name: string;
  description: string;
}

export interface SyncError {
  skill: string;
  error: string;
}

export interface SyncResult {
  added: string[];
  updated: string[];
  removed: string[];
  errors: SyncError[];
  totalLocal: number;
  totalS3: number;
  totalDb: number;
}

// MCP Server Types
export interface MCPServer {
  id: string;
  name: string;
  description?: string;
  connectionType: 'stdio' | 'sse' | 'http';
  config: Record<string, unknown>;
  allowedTools?: string[];
  rejectedTools?: string[];
  endpoint?: string;
  version?: string;
  createdAt: string;
  updatedAt: string;
}

export interface MCPServerCreateRequest {
  name: string;
  description?: string;
  connectionType: 'stdio' | 'sse' | 'http';
  config: Record<string, unknown>;
  allowedTools?: string[];
  rejectedTools?: string[];
}

export interface MCPServerUpdateRequest extends Partial<MCPServerCreateRequest> {}

// Chat/Message Types
export interface ChatSession {
  id: string;
  agentId: string;
  title: string;
  createdAt: string;
  lastAccessedAt: string;
}

export interface ChatMessage {
  id: string;
  sessionId: string;
  role: 'user' | 'assistant';
  content: ContentBlock[];
  model?: string;
  createdAt: string;
}

export interface TextContent {
  type: 'text';
  text: string;
}

export interface ToolUseContent {
  type: 'tool_use';
  id: string;
  name: string;
  input: Record<string, unknown>;
}

export interface ToolResultContent {
  type: 'tool_result';
  toolUseId: string;
  content?: string;
  isError: boolean;
}

// AskUserQuestion types
export interface AskUserQuestionOption {
  label: string;
  description: string;
}

export interface AskUserQuestion {
  question: string;
  header: string;
  options: AskUserQuestionOption[];
  multiSelect: boolean;
}

export interface AskUserQuestionContent {
  type: 'ask_user_question';
  toolUseId: string;
  questions: AskUserQuestion[];
}

export type ContentBlock = TextContent | ToolUseContent | ToolResultContent | AskUserQuestionContent;

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: ContentBlock[];
  timestamp: string;
  model?: string;
}

export interface ChatRequest {
  agentId: string;
  message: string;
  sessionId?: string;
  enableSkills?: boolean;
  enableMCP?: boolean;
}

export interface StreamEvent {
  type: 'assistant' | 'tool_use' | 'tool_result' | 'result' | 'error' | 'ask_user_question' | 'session_start';
  content?: ContentBlock[];
  model?: string;
  sessionId?: string;
  durationMs?: number;
  totalCostUsd?: number;
  numTurns?: number;
  skillName?: string; // For skill creation result
  // AskUserQuestion fields
  toolUseId?: string;
  questions?: AskUserQuestion[];
  // Error fields
  error?: string;
  message?: string;
  code?: string;
  detail?: string;
  suggestedAction?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

// Error Types
export interface ErrorResponse {
  code: string;
  message: string;
  detail?: string;
  suggestedAction?: string;
  requestId?: string;
}

export interface ValidationErrorField {
  field: string;
  error: string;
}

export interface ValidationErrorResponse extends ErrorResponse {
  code: 'VALIDATION_FAILED';
  fields: ValidationErrorField[];
}

export interface RateLimitErrorResponse extends ErrorResponse {
  code: 'RATE_LIMIT_EXCEEDED';
  retryAfter: number;
}

// Error code constants
export const ErrorCodes = {
  // Validation (400)
  VALIDATION_FAILED: 'VALIDATION_FAILED',
  // Authentication (401)
  AUTH_TOKEN_MISSING: 'AUTH_TOKEN_MISSING',
  AUTH_TOKEN_INVALID: 'AUTH_TOKEN_INVALID',
  AUTH_TOKEN_EXPIRED: 'AUTH_TOKEN_EXPIRED',
  // Authorization (403)
  FORBIDDEN: 'FORBIDDEN',
  // Not Found (404)
  AGENT_NOT_FOUND: 'AGENT_NOT_FOUND',
  SKILL_NOT_FOUND: 'SKILL_NOT_FOUND',
  MCP_SERVER_NOT_FOUND: 'MCP_SERVER_NOT_FOUND',
  SESSION_NOT_FOUND: 'SESSION_NOT_FOUND',
  // Conflict (409)
  DUPLICATE_RESOURCE: 'DUPLICATE_RESOURCE',
  // Rate Limit (429)
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  // Server (500)
  SERVER_ERROR: 'SERVER_ERROR',
  AGENT_EXECUTION_ERROR: 'AGENT_EXECUTION_ERROR',
  AGENT_TIMEOUT: 'AGENT_TIMEOUT',
  // Service (503)
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  DATABASE_UNAVAILABLE: 'DATABASE_UNAVAILABLE',
} as const;

export type ErrorCode = (typeof ErrorCodes)[keyof typeof ErrorCodes];

// Loading State Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface LoadingStateInfo {
  state: LoadingState;
  error?: ErrorResponse;
}
