export interface RemoteAgent {
  id: string;
  name: string;
  description: string;
  url: string;
  skill_name: string;
  skill_description: string;
  skills?: Array<{
    name: string;
    description: string;
  }>;
  status: string;
  enabled: boolean;
}

export interface AddAgentRequest {
  url: string;
}

export interface DeleteAgentRequest {
  agent_id: string;
}

export interface InvokeStreamRequest {
  query: string;
}

export interface PreviewAgentRequest {
  url: string;
}

export interface PreviewAgentResponse {
  name: string;
  description: string;
  skills: Array<{
    name: string;
    description: string;
  }>;
}

export interface StreamResponse {
  type: 'start' | 'stream' | 'final' | 'error' | 'complete';
  content?: string;
  message?: string;
  agent_id?: string;
}