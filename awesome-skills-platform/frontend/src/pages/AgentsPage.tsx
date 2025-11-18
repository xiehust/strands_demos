import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { agentsApi } from '../services/agents';
import { skillsApi } from '../services/skills';
import { mcpApi } from '../services/mcp';
import { Button } from '../components/common/Button';
import type { Agent } from '../types';

export function AgentsPage() {
  const navigate = useNavigate();
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  // Fetch agents
  const { data: agents = [], isLoading: agentsLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: agentsApi.list,
  });

  // Fetch skills for the edit panel
  const { data: skills = [] } = useQuery({
    queryKey: ['skills'],
    queryFn: skillsApi.list,
  });

  // Fetch MCP servers for the edit panel
  const { data: mcpServers = [] } = useQuery({
    queryKey: ['mcp'],
    queryFn: mcpApi.list,
  });

  // Update agent mutation (reserved for future use)
  // const updateAgentMutation = useMutation({
  //   mutationFn: ({ id, data }: { id: string; data: any }) =>
  //     agentsApi.update(id, data),
  //   onSuccess: () => {
  //     queryClient.invalidateQueries({ queryKey: ['agents'] });
  //   },
  // });

  return (
    <div className="flex h-full">
      {/* Agents List */}
      <div className="flex-1 p-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Agent Management</h1>
            <p className="text-text-muted">Create, configure, and monitor your AI agents.</p>
          </div>
          <Button onClick={() => navigate('/agents/create')}>
            <span className="material-symbols-outlined">add</span>
            Add Agent
          </Button>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
              search
            </span>
            <input
              type="text"
              placeholder="Search agents by name or model..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        {/* Agents Table */}
        <div className="bg-gray-900 rounded-lg border border-gray-800">
          {agentsLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-text-muted">Loading agents...</div>
            </div>
          ) : agents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="text-text-muted mb-4">No agents found</div>
              <Button onClick={() => navigate('/agents/create')}>
                <span className="material-symbols-outlined">add</span>
                Create Your First Agent
              </Button>
            </div>
          ) : (
            <table className="w-full">
              <thead className="border-b border-gray-800">
                <tr className="text-left">
                  <th className="px-6 py-4 font-medium text-text-muted">Agent Name</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Status</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Base Model</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Max Tokens</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Actions</th>
                </tr>
              </thead>
              <tbody>
                {agents.map((agent) => (
                  <tr
                    key={agent.id}
                    className="border-b border-gray-800 hover:bg-gray-800 cursor-pointer transition-colors"
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <td className="px-6 py-4 font-medium">{agent.name}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                          agent.status === 'active'
                            ? 'bg-green-500/10 text-green-400'
                            : 'bg-gray-500/10 text-gray-400'
                        }`}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                        {agent.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-text-muted">
                      {agent.modelId.includes('sonnet') ? 'Claude Sonnet 4.5' : 'Claude Haiku 4.5'}
                    </td>
                    <td className="px-6 py-4 text-text-muted">{agent.maxTokens}</td>
                    <td className="px-6 py-4">
                      <button className="text-primary hover:text-blue-400 transition-colors">
                        Edit
                      </button>
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
        <div className="w-96 bg-gray-900 border-l border-gray-800 p-6 overflow-y-auto">
          <h2 className="text-xl font-semibold mb-2">Edit Agent</h2>
          <p className="text-text-muted text-sm mb-6">
            Modify the configuration for '{selectedAgent.name}'.
          </p>

          <div className="space-y-6">
            {/* Agent Name */}
            <div>
              <label className="block text-sm font-medium mb-2">Agent Name</label>
              <input
                type="text"
                value={selectedAgent.name}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:border-primary"
              />
            </div>

            {/* Base Model */}
            <div>
              <label className="block text-sm font-medium mb-2">Base Model</label>
              <select className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:border-primary">
                <option>Claude Sonnet 4.5</option>
                <option>Claude Haiku 4.5</option>
                <option>GPT-4</option>
              </select>
            </div>

            {/* Max Token */}
            <div>
              <label className="block text-sm font-medium mb-2">Max Token</label>
              <input
                type="number"
                value={selectedAgent.maxTokens}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:border-primary"
              />
            </div>

            {/* Enable Thinking Process */}
            <div>
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm font-medium">Enable Thinking Process</span>
                <input
                  type="checkbox"
                  checked={selectedAgent.thinkingEnabled}
                  className="w-12 h-6 bg-gray-700 rounded-full appearance-none cursor-pointer checked:bg-primary relative before:content-[''] before:absolute before:w-5 before:h-5 before:bg-white before:rounded-full before:top-0.5 before:left-0.5 checked:before:translate-x-6 before:transition-transform"
                />
              </label>
            </div>

            {/* Enabled Skills */}
            <div>
              <label className="block text-sm font-medium mb-2">Enabled Skills</label>
              <div className="space-y-2">
                {skills.map((skill) => (
                  <label key={skill.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedAgent.skillIds.includes(skill.id)}
                      className="w-4 h-4 rounded border-gray-600"
                    />
                    <span className="text-sm">{skill.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Enabled MCPs */}
            <div>
              <label className="block text-sm font-medium mb-2">Enabled MCPs</label>
              <div className="space-y-2">
                {mcpServers.map((mcp) => (
                  <label key={mcp.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedAgent.mcpIds.includes(mcp.id)}
                      className="w-4 h-4 rounded border-gray-600"
                    />
                    <span className="text-sm">{mcp.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <Button variant="ghost" className="flex-1">Cancel</Button>
              <Button className="flex-1">Save Changes</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
