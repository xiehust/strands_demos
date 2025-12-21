import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import clsx from 'clsx';
import { SearchBar, StatusBadge, Button, Modal, MultiSelect, SkeletonTable, Spinner, ToolSelector, getDefaultEnabledTools, ResizableTable, ResizableTableCell, ConfirmDialog } from '../components/common';
import type { Agent, AgentCreateRequest, Skill, MCPServer } from '../types';
import { agentsService } from '../services/agents';
import { skillsService } from '../services/skills';
import { mcpService } from '../services/mcp';
import { useLoadingState } from '../hooks/useLoadingState';

// Agent table column configuration
const AGENT_COLUMNS = [
  { key: 'name', header: 'Agent Name', initialWidth: 180, minWidth: 120 },
  { key: 'status', header: 'Status', initialWidth: 100, minWidth: 80 },
  { key: 'model', header: 'Base Model', initialWidth: 200, minWidth: 150 },
  { key: 'skills', header: 'Enabled Skills', initialWidth: 200, minWidth: 120 },
  { key: 'mcps', header: 'Enabled MCPs', initialWidth: 200, minWidth: 120 },
  { key: 'actions', header: 'Actions', initialWidth: 140, minWidth: 100, align: 'right' as const },
];

export default function AgentsPage() {
  const navigate = useNavigate();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  // Loading states for save operations
  const saveState = useLoadingState();

  // Fetch agents and models on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agentsData, modelsData] = await Promise.all([
          agentsService.list(),
          agentsService.listModels(),
        ]);
        setAgents(agentsData);
        setModels(modelsData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setIsInitialLoading(false);
      }
    };
    fetchData();
  }, []);

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

  // Fetch skills and MCPs on mount for table display
  useEffect(() => {
    fetchSkills();
    fetchMCPs();
  }, []);

  // Helper functions to get names from IDs
  const getSkillNames = (skillIds: string[]) => {
    if (!skillIds || skillIds.length === 0) return '-';
    const names = skillIds
      .map((id) => skills.find((s) => s.id === id)?.name)
      .filter(Boolean);
    return names.length > 0 ? names.join(', ') : '-';
  };

  const getMcpNames = (mcpIds: string[]) => {
    if (!mcpIds || mcpIds.length === 0) return '-';
    const names = mcpIds
      .map((id) => mcpServers.find((m) => m.id === id)?.name)
      .filter(Boolean);
    return names.length > 0 ? names.join(', ') : '-';
  };

  const filteredAgents = agents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.model?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSaveChanges = async () => {
    if (!selectedAgent) return;

    await saveState.execute(async () => {
      const updated = await agentsService.update(selectedAgent.id, selectedAgent);
      setAgents((prev) =>
        prev.map((agent) => (agent.id === updated.id ? updated : agent))
      );
      setSelectedAgent(updated);
    });
  };

  // Delete confirmation state
  const [deleteTarget, setDeleteTarget] = useState<Agent | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (agent: Agent) => {
    setDeleteTarget(agent);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await agentsService.delete(deleteTarget.id);
      setAgents((prev) => prev.filter((a) => a.id !== deleteTarget.id));
      if (selectedAgent?.id === deleteTarget.id) {
        setSelectedAgent(null);
      }
      setDeleteTarget(null);
    } catch (error) {
      console.error('Failed to delete agent:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleStartChat = (agentId: string) => {
    navigate(`/chat?agentId=${agentId}`);
  };

  const handleCreateAgent = async (data: AgentCreateRequest) => {
    try {
      const created = await agentsService.create(data);
      setAgents((prev) => [...prev, created]);
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error('Failed to create agent:', error);
    }
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
              <SkeletonTable rows={5} columns={6} />
            ) : (
              <ResizableTable columns={AGENT_COLUMNS}>
                {filteredAgents.map((agent) => (
                  <tr
                    key={agent.id}
                    className={clsx(
                      'border-b border-dark-border hover:bg-dark-hover transition-colors cursor-pointer',
                      selectedAgent?.id === agent.id && 'bg-dark-hover'
                    )}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <ResizableTableCell>
                      <span className="text-white font-medium">{agent.name}</span>
                    </ResizableTableCell>
                    <ResizableTableCell>
                      <StatusBadge status={agent.status} />
                    </ResizableTableCell>
                    <ResizableTableCell>
                      <span className="text-muted">{agent.model}</span>
                    </ResizableTableCell>
                    <ResizableTableCell>
                      <span className="text-muted" title={getSkillNames(agent.skillIds)}>
                        {getSkillNames(agent.skillIds)}
                      </span>
                    </ResizableTableCell>
                    <ResizableTableCell>
                      <span className="text-muted" title={getMcpNames(agent.mcpIds)}>
                        {getMcpNames(agent.mcpIds)}
                      </span>
                    </ResizableTableCell>
                    <ResizableTableCell align="right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStartChat(agent.id);
                          }}
                          className="p-2 rounded-lg text-muted hover:text-primary hover:bg-primary/10 transition-colors"
                          title="Start chat with this agent"
                        >
                          <span className="material-symbols-outlined text-xl">chat</span>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedAgent(agent);
                          }}
                          className="p-2 rounded-lg text-muted hover:text-white hover:bg-dark-hover transition-colors"
                          title="Edit agent"
                        >
                          <span className="material-symbols-outlined text-xl">edit</span>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteClick(agent);
                          }}
                          className="p-2 rounded-lg text-muted hover:text-status-error hover:bg-status-error/10 transition-colors"
                          title="Delete agent"
                        >
                          <span className="material-symbols-outlined text-xl">delete</span>
                        </button>
                      </div>
                    </ResizableTableCell>
                  </tr>
                ))}
                {filteredAgents.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <span className="material-symbols-outlined text-4xl text-muted mb-2">smart_toy</span>
                      <p className="text-muted">No agents found</p>
                    </td>
                  </tr>
                )}
              </ResizableTable>
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

              {/* System Prompt */}
              <div>
                <label className="block text-sm font-medium text-muted mb-2">System Prompt</label>
                <textarea
                  value={selectedAgent.systemPrompt || ''}
                  onChange={(e) =>
                    setSelectedAgent({ ...selectedAgent, systemPrompt: e.target.value || undefined })
                  }
                  placeholder="Enter system prompt instructions..."
                  rows={4}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary resize-none"
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

              {/* Built-in Tools */}
              <ToolSelector
                selectedTools={selectedAgent.allowedTools}
                onChange={(allowedTools) =>
                  setSelectedAgent({ ...selectedAgent, allowedTools })
                }
              />

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
          onCreate={handleCreateAgent}
          models={models}
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

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Delete Agent"
        message={
          <>
            Are you sure you want to delete <strong>{deleteTarget?.name}</strong>?
            <br />
            <span className="text-sm">This action cannot be undone.</span>
          </>
        }
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
        isLoading={isDeleting}
      />
    </div>
  );
}

// Create Agent Form Component
function CreateAgentForm({
  onClose,
  onCreate,
  models,
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
  onCreate: (data: AgentCreateRequest) => void;
  models: string[];
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
  const [systemPrompt, setSystemPrompt] = useState('');
  const [model, setModel] = useState(models[0] || '');
  const [skillIds, setSkillIds] = useState<string[]>([]);
  const [mcpIds, setMcpIds] = useState<string[]>([]);
  const [allowedTools, setAllowedTools] = useState<string[]>(getDefaultEnabledTools());

  // Update default model when models list loads
  useEffect(() => {
    if (models.length > 0 && !model) {
      setModel(models[0]);
    }
  }, [models, model]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data: AgentCreateRequest = {
      name,
      description: description || undefined,
      model,
      permissionMode: 'default',
      systemPrompt: systemPrompt || undefined,
      skillIds,
      mcpIds,
      allowedTools,
    };
    onCreate(data);
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
        <label className="block text-sm font-medium text-muted mb-2">System Prompt</label>
        <textarea
          value={systemPrompt}
          onChange={(e) => setSystemPrompt(e.target.value)}
          placeholder="Enter system prompt instructions for the agent (optional)"
          rows={4}
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

      {/* Built-in Tools */}
      <ToolSelector
        selectedTools={allowedTools}
        onChange={setAllowedTools}
      />

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
