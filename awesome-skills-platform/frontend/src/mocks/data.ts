import type { Agent, Skill, MCPServer, Conversation, Message } from '../types';

// Mock Agents
export const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Customer Service Bot',
    description: 'Handles customer inquiries and support requests',
    modelId: 'anthropic.claude-sonnet-4-5-20250929-v1:0',
    temperature: 0.7,
    maxTokens: 4096,
    thinkingEnabled: true,
    thinkingBudget: 2048,
    systemPrompt: 'You are a helpful customer service assistant.',
    skillIds: ['1', '2'],
    mcpIds: ['1'],
    status: 'active',
    createdAt: '2025-10-15T10:00:00Z',
    updatedAt: '2025-10-20T15:30:00Z',
  },
  {
    id: '2',
    name: 'Data Analysis Agent',
    description: 'Analyzes data and generates insights',
    modelId: 'anthropic.claude-sonnet-4-5-20250929-v1:0',
    temperature: 0.3,
    maxTokens: 8192,
    thinkingEnabled: false,
    thinkingBudget: 1024,
    skillIds: ['1', '3'],
    mcpIds: [],
    status: 'inactive',
    createdAt: '2025-10-18T14:20:00Z',
    updatedAt: '2025-10-25T09:15:00Z',
  },
  {
    id: '3',
    name: 'Content Generation Agent',
    description: 'Creates marketing content and blog posts',
    modelId: 'anthropic.claude-haiku-4-5-20251001-v1:0',
    temperature: 0.9,
    maxTokens: 2048,
    thinkingEnabled: false,
    thinkingBudget: 512,
    skillIds: ['4'],
    mcpIds: ['2'],
    status: 'active',
    createdAt: '2025-10-22T08:45:00Z',
    updatedAt: '2025-10-28T11:00:00Z',
  },
];

// Mock Skills
export const mockSkills: Skill[] = [
  {
    id: '1',
    name: 'xlsx',
    description: 'Read and analyze Excel files with data extraction and statistics',
    createdBy: 'system',
    createdAt: '2025-09-01T00:00:00Z',
    version: '1.0.0',
    isSystem: true,
  },
  {
    id: '2',
    name: 'pdf',
    description: 'Extract text and tables from PDF documents',
    createdBy: 'system',
    createdAt: '2025-09-01T00:00:00Z',
    version: '1.2.0',
    isSystem: true,
  },
  {
    id: '3',
    name: 'docx',
    description: 'Create and edit Word documents with formatting',
    createdBy: 'system',
    createdAt: '2025-09-01T00:00:00Z',
    version: '1.1.0',
    isSystem: true,
  },
  {
    id: '4',
    name: 'web-search',
    description: 'Search the web for real-time information using Tavily',
    createdBy: 'system',
    createdAt: '2025-09-15T00:00:00Z',
    version: '1.0.0',
    isSystem: true,
  },
  {
    id: '5',
    name: 'image-analysis',
    description: 'Analyze images and extract insights',
    createdBy: 'user123',
    createdAt: '2025-10-10T12:30:00Z',
    version: '0.9.0',
    isSystem: false,
  },
];

// Mock MCP Servers
export const mockMCPServers: MCPServer[] = [
  {
    id: '1',
    name: 'Production-Cluster-A',
    description: 'Main production MCP server cluster',
    connectionType: 'http',
    endpoint: '192.168.1.100:8080',
    status: 'online',
    version: 'v2.1.3',
    agentCount: 150,
    config: { url: 'http://192.168.1.100:8080' },
  },
  {
    id: '2',
    name: 'Staging-EU-West',
    description: 'European staging environment',
    connectionType: 'sse',
    endpoint: '10.0.5.23:8080',
    status: 'offline',
    version: 'v2.1.1',
    agentCount: 75,
    config: { url: 'http://10.0.5.23:8080' },
  },
  {
    id: '3',
    name: 'Development-US-East',
    description: 'Development environment for testing',
    connectionType: 'stdio',
    endpoint: 'dev.mcp.internal:9000',
    status: 'error',
    version: 'v2.2.0-beta',
    agentCount: 12,
    config: { command: 'mcp-server', args: ['--dev'] },
  },
];

// Mock Conversations
export const mockConversations: Conversation[] = [
  {
    id: '1',
    title: 'Python script for data analysis',
    agentId: '2',
    createdAt: '2025-11-01T10:00:00Z',
    updatedAt: '2025-11-01T10:35:00Z',
    messageCount: 8,
  },
  {
    id: '2',
    title: 'Image generation prompt',
    agentId: '3',
    createdAt: '2025-11-01T09:15:00Z',
    updatedAt: '2025-11-01T09:45:00Z',
    messageCount: 5,
  },
  {
    id: '3',
    title: 'Summarize Q3 report',
    agentId: '2',
    createdAt: '2025-10-31T16:20:00Z',
    updatedAt: '2025-10-31T16:50:00Z',
    messageCount: 12,
  },
  {
    id: '4',
    title: 'Translate this email',
    agentId: '1',
    createdAt: '2025-10-31T14:10:00Z',
    updatedAt: '2025-10-31T14:15:00Z',
    messageCount: 3,
  },
];

// Mock Messages
export const mockMessages: Message[] = [
  {
    id: '1',
    conversationId: '1',
    role: 'assistant',
    content: "Hello, I'm your AI Agent. How can I assist you today? You can ask me questions, upload images, or enable Skills for advanced tasks.",
    timestamp: '2025-11-01T10:30:00Z',
  },
  {
    id: '2',
    conversationId: '1',
    role: 'user',
    content: 'Please write a python script to parse a CSV and output the average of the "revenue" column.',
    timestamp: '2025-11-01T10:31:00Z',
  },
  {
    id: '3',
    conversationId: '1',
    role: 'assistant',
    content: 'Certainly. First, I need to use the "CodeInterpreter" tool to execute the script.',
    thinkingContent: 'The user wants to parse CSV data and calculate the average of a specific column. I should write a Python script using pandas for easy data manipulation.',
    toolUses: [
      {
        id: 'tool_1',
        name: 'CodeInterpreter',
        input: {
          code: `import pandas as pd
import io

# Sample CSV data
csv_data = """id,product,revenue,date
1,A,100,2023-01-15
2,B,150,2023-01-16
3,A,200,2023-01-17
4,C,50,2023-01-18
5,B,120,2023-01-19
"""

# Read CSV
df = pd.read_csv(io.StringIO(csv_data))

# Calculate average revenue
avg_revenue = df['revenue'].mean()

print(f"Average revenue: {avg_revenue}")`,
        },
        result: 'Average revenue: 124.0',
        status: 'success',
      },
    ],
    timestamp: '2025-11-01T10:32:00Z',
  },
];
