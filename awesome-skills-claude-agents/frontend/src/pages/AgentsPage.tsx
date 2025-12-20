import { useState } from 'react';
import clsx from 'clsx';
import { SearchBar, StatusBadge, Button, Modal, MultiSelect, SkeletonTable, Spinner } from '../components/common';
import type { Agent, Skill, MCPServer } from '../types';
import { skillsService } from '../services/skills';
import { mcpService } from '../services/mcp';
import { useLoadingState } from '../hooks/useLoadingState';

// Mock data for demo
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Customer Service Bot',
    description: 'Handles customer inquiries and support tickets',
    model: 'GPT-4o',
    permissionMode: 'default',
    maxTurns: 4096,
    systemPrompt: 'You are a helpful customer service agent.',
    allowedTools: ['Read', 'Write'],
    skillIds: ['knowledge-base-search', 'sentiment-analysis'],
    mcpIds: ['profanity-filter'],
    workingDirectory: '/workspace',
    enableBashTool: false,
    enableFileTools: true,
    enableWebTools: false,
    enableToolLogging: true,
    enableSafetyChecks: true,
    status: 'active',
    createdAt: '2025-01-01',
    updatedAt: '2025-01-01',
  },
  {
    id: '2',
    name: 'Data Analysis Agent',
    description: 'Analyzes data and generates reports',
    model: 'Claude 3 Opus',
    permissionMode: 'acceptEdits',
    maxTurns: 8192,
    systemPrompt: 'You are a data analysis expert.',
    allowedTools: ['Read', 'Write', 'Bash'],
    skillIds: ['api-integration'],
    mcpIds: [],
    workingDirectory: '/workspace',
    enableBashTool: true,
    enableFileTools: true,
    enableWebTools: true,
    enableToolLogging: true,
    enableSafetyChecks: true,
    status: 'inactive',
    createdAt: '2025-01-01',
    updatedAt: '2025-01-01',
  },
  {
    id: '3',
    name: 'Content Generation Agent',
    description: 'Creates and edits content',
    model: 'GPT-4',
    permissionMode: 'default',
    maxTurns: 2048,
    systemPrompt: 'You are a creative content writer.',
    allowedTools: ['Read', 'Write'],
    skillIds: [],
    mcpIds: [],
    workingDirectory: '/workspace',
    enableBashTool: false,
    enableFileTools: true,
    enableWebTools: false,
    enableToolLogging: true,
    enableSafetyChecks: true,
    status: 'active',
    createdAt: '2025-01-01',
    updatedAt: '2025-01-01',
  },
];

const models = ['GPT-4o', 'GPT-4', 'Claude 3 Opus', 'Claude 3.5 Sonnet', 'Claude Sonnet 4'];

export default function AgentsPage() {
  const [agents, setAgents] = useState(mockAgents);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(mockAgents[0]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isInitialLoading] = useState(false);

  // Loading states for save operations
  const saveState = useLoadingState();

  // Skills and MCPs state
  const [skills, setSkills] = useState<Skill[]>([]);
  const [mcpServers, setMcpServers] = useState<MCPServer[]>([]);
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [loadingMCPs, setLoadingMCPs] = useState(false);
  const [skillsError, setSkillsError] = useState<string | null>(null);
  const [mcpsError, setMcpsError] = useState<string | null>(null);

  // Fetch skills
  const fetchSkills = async () => {
    setLoadingSkills(true);
    setSkillsError(null);
    try {
      const data = await skillsService.list();
      setSkills(data);
    } catch (error) {
      console.error('Failed to fetch skills:', error);
      setSkillsError('Failed to load skills');
    } finally {
      setLoadingSkills(false);
    }
  };

  // Fetch MCP servers
  const fetchMCPs = async () => {
    setLoadingMCPs(true);
    setMcpsError(null);
    try {
      const data = await mcpService.list();
      setMcpServers(data);
    } catch (error) {
      console.error('Failed to fetch MCP servers:', error);
      setMcpsError('Failed to load MCP servers');
    } finally {
      setLoadingMCPs(false);
    }
  };

  const filteredAgents = agents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.model?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSaveChanges = async () => {
    if (!selectedAgent) return;

    await saveState.execute(async () => {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));
      setAgents((prev) =>
        prev.map((agent) => (agent.id === selectedAgent.id ? selectedAgent : agent))
      );
    });
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Agent Management</h1>
          <p className="text-muted mt-1">Create, configure, and monitor your AI agents.</p>
        </div>
        <Button icon="add" onClick={() => setIsCreateModalOpen(true)}>
          Add Agent
        </Button>
      </div>

      <div className="flex gap-6">
        {/* Agent List */}
        <div className="flex-1">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search agents by name or model..."
            className="mb-4"
          />

          <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden">
            {isInitialLoading ? (
              <SkeletonTable rows={5} columns={5} />
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-border">
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted">Agent Name</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted">Base Model</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted">Max Tokens</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-muted">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAgents.map((agent) => (
                    <tr
                      key={agent.id}
                      className={clsx(
                        'border-b border-dark-border hover:bg-dark-hover transition-colors cursor-pointer',
                        selectedAgent?.id === agent.id && 'bg-dark-hover'
                      )}
                      onClick={() => setSelectedAgent(agent)}
                    >
                      <td className="px-6 py-4">
                        <span className="text-white font-medium">{agent.name}</span>
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={agent.status} />
                      </td>
                      <td className="px-6 py-4 text-muted">{agent.model}</td>
                      <td className="px-6 py-4 text-muted">{agent.maxTurns}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedAgent(agent);
                            }}
                            className="p-2 rounded-lg text-muted hover:text-white hover:bg-dark-hover transition-colors"
                          >
                            <span className="material-symbols-outlined text-xl">edit</span>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setAgents((prev) => prev.filter((a) => a.id !== agent.id));
                            }}
                            className="p-2 rounded-lg text-muted hover:text-status-error hover:bg-status-error/10 transition-colors"
                          >
                            <span className="material-symbols-outlined text-xl">delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Edit Panel */}
        {selectedAgent && (
          <div className="w-80 bg-dark-card border border-dark-border rounded-xl p-6">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-white">Edit Agent</h2>
              <p className="text-sm text-muted mt-1">
                Modify the configuration for '{selectedAgent.name}'.
              </p>
            </div>

            <div className="space-y-4">
              {/* Agent Name */}
              <div>
                <label className="block text-sm font-medium text-muted mb-2">Agent Name</label>
                <input
                  type="text"
                  value={selectedAgent.name}
                  onChange={(e) =>
                    setSelectedAgent({ ...selectedAgent, name: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
                />
              </div>

              {/* Base Model */}
              <div>
                <label className="block text-sm font-medium text-muted mb-2">Base Model</label>
                <select
                  value={selectedAgent.model}
                  onChange={(e) =>
                    setSelectedAgent({ ...selectedAgent, model: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
                >
                  {models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>

              {/* Max Token */}
              <div>
                <label className="block text-sm font-medium text-muted mb-2">Max Token</label>
                <input
                  type="number"
                  value={selectedAgent.maxTurns}
                  onChange={(e) =>
                    setSelectedAgent({ ...selectedAgent, maxTurns: parseInt(e.target.value) })
                  }
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
                />
              </div>

              {/* Enable Thinking Process */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-muted">Enable Thinking Process</label>
                <button
                  onClick={() =>
                    setSelectedAgent({
                      ...selectedAgent,
                      enableToolLogging: !selectedAgent.enableToolLogging,
                    })
                  }
                  className={clsx(
                    'w-12 h-6 rounded-full transition-colors relative',
                    selectedAgent.enableToolLogging ? 'bg-primary' : 'bg-dark-border'
                  )}
                >
                  <span
                    className={clsx(
                      'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                      selectedAgent.enableToolLogging ? 'left-7' : 'left-1'
                    )}
                  />
                </button>
              </div>

              {/* Enabled Skills */}
              <MultiSelect
                label="Enabled Skills"
                placeholder="Select skills..."
                options={skills.map((skill) => ({
                  id: skill.id,
                  name: skill.name,
                  description: skill.description,
                }))}
                selectedIds={selectedAgent.skillIds}
                onChange={(skillIds) =>
                  setSelectedAgent({ ...selectedAgent, skillIds })
                }
                loading={loadingSkills}
                error={skillsError || undefined}
                onOpen={fetchSkills}
              />

              {/* Enabled MCPs */}
              <MultiSelect
                label="Enabled MCPs"
                placeholder="Select MCP servers..."
                options={mcpServers.map((mcp) => ({
                  id: mcp.id,
                  name: mcp.name,
                  description: mcp.description,
                }))}
                selectedIds={selectedAgent.mcpIds}
                onChange={(mcpIds) =>
                  setSelectedAgent({ ...selectedAgent, mcpIds })
                }
                loading={loadingMCPs}
                error={mcpsError || undefined}
                onOpen={fetchMCPs}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 mt-6">
              <Button variant="secondary" className="flex-1" onClick={() => setSelectedAgent(null)} disabled={saveState.isLoading}>
                Cancel
              </Button>
              <Button className="flex-1" onClick={handleSaveChanges} disabled={saveState.isLoading}>
                {saveState.isLoading ? (
                  <span className="flex items-center gap-2">
                    <Spinner size="sm" color="#ffffff" />
                    Saving...
                  </span>
                ) : (
                  'Save Changes'
                )}
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Agent"
        size="lg"
      >
        <CreateAgentForm
          onClose={() => setIsCreateModalOpen(false)}
          onCreate={(agent) => {
            setAgents((prev) => [...prev, agent]);
            setIsCreateModalOpen(false);
          }}
          skills={skills}
          mcpServers={mcpServers}
          loadingSkills={loadingSkills}
          loadingMCPs={loadingMCPs}
          skillsError={skillsError}
          mcpsError={mcpsError}
          onFetchSkills={fetchSkills}
          onFetchMCPs={fetchMCPs}
        />
      </Modal>
    </div>
  );
}

// Create Agent Form Component
function CreateAgentForm({
  onClose,
  onCreate,
  skills,
  mcpServers,
  loadingSkills,
  loadingMCPs,
  skillsError,
  mcpsError,
  onFetchSkills,
  onFetchMCPs,
}: {
  onClose: () => void;
  onCreate: (agent: Agent) => void;
  skills: Skill[];
  mcpServers: MCPServer[];
  loadingSkills: boolean;
  loadingMCPs: boolean;
  skillsError: string | null;
  mcpsError: string | null;
  onFetchSkills: () => void;
  onFetchMCPs: () => void;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [model, setModel] = useState('Claude Sonnet 4');
  const [skillIds, setSkillIds] = useState<string[]>([]);
  const [mcpIds, setMcpIds] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newAgent: Agent = {
      id: Date.now().toString(),
      name,
      description,
      model,
      permissionMode: 'default',
      maxTurns: 4096,
      systemPrompt: '',
      allowedTools: [],
      skillIds,
      mcpIds,
      workingDirectory: '/workspace',
      enableBashTool: false,
      enableFileTools: true,
      enableWebTools: false,
      enableToolLogging: true,
      enableSafetyChecks: true,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    onCreate(newAgent);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-muted mb-2">Agent Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter agent name"
          required
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-muted mb-2">Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what this agent does"
          rows={3}
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary resize-none"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-muted mb-2">Base Model</label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
        >
          {models.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      {/* Skills Selection */}
      <MultiSelect
        label="Skills (Optional)"
        placeholder="Select skills..."
        options={skills.map((skill) => ({
          id: skill.id,
          name: skill.name,
          description: skill.description,
        }))}
        selectedIds={skillIds}
        onChange={setSkillIds}
        loading={loadingSkills}
        error={skillsError || undefined}
        onOpen={onFetchSkills}
      />

      {/* MCP Servers Selection */}
      <MultiSelect
        label="MCP Servers (Optional)"
        placeholder="Select MCP servers..."
        options={mcpServers.map((mcp) => ({
          id: mcp.id,
          name: mcp.name,
          description: mcp.description,
        }))}
        selectedIds={mcpIds}
        onChange={setMcpIds}
        loading={loadingMCPs}
        error={mcpsError || undefined}
        onOpen={onFetchMCPs}
      />

      <div className="flex gap-3 pt-4">
        <Button type="button" variant="secondary" className="flex-1" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" className="flex-1">
          Create Agent
        </Button>
      </div>
    </form>
  );
}
