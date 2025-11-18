import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { agentsApi } from '../services/agents';
import { skillsApi } from '../services/skills';
import { mcpApi } from '../services/mcp';
import { Button } from '../components/common/Button';

const availableModels = [
  { id: 'anthropic.claude-sonnet-4-5-20250929-v1:0', name: 'Claude Sonnet 4.5' },
  { id: 'anthropic.claude-haiku-4-5-20251001-v1:0', name: 'Claude Haiku 4.5' },
  { id: 'anthropic.claude-opus-4-5-20250514-v1:0', name: 'Claude Opus 4.5' },
];

export function CreateAgentPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    modelId: '',
    maxTokens: 4096,
    thinkingEnabled: false,
    skillIds: [] as string[],
    mcpIds: [] as string[],
  });

  const [skillSearch, setSkillSearch] = useState('');
  const [mcpSearch, setMcpSearch] = useState('');

  // Fetch skills
  const { data: skills = [] } = useQuery({
    queryKey: ['skills'],
    queryFn: skillsApi.list,
  });

  // Fetch MCP servers
  const { data: mcpServers = [] } = useQuery({
    queryKey: ['mcp'],
    queryFn: mcpApi.list,
  });

  // Create agent mutation
  const createAgentMutation = useMutation({
    mutationFn: agentsApi.create,
    onSuccess: () => {
      navigate('/agents');
    },
  });

  const filteredSkills = skills.filter(skill =>
    skill.name.toLowerCase().includes(skillSearch.toLowerCase()) ||
    skill.description.toLowerCase().includes(skillSearch.toLowerCase())
  );

  const filteredMCPs = mcpServers.filter(mcp =>
    mcp.name.toLowerCase().includes(mcpSearch.toLowerCase()) ||
    (mcp.description?.toLowerCase() || '').includes(mcpSearch.toLowerCase())
  );

  const handleSkillToggle = (skillId: string) => {
    setFormData(prev => ({
      ...prev,
      skillIds: prev.skillIds.includes(skillId)
        ? prev.skillIds.filter(id => id !== skillId)
        : [...prev.skillIds, skillId],
    }));
  };

  const handleMCPToggle = (mcpId: string) => {
    setFormData(prev => ({
      ...prev,
      mcpIds: prev.mcpIds.includes(mcpId)
        ? prev.mcpIds.filter(id => id !== mcpId)
        : [...prev.mcpIds, mcpId],
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.modelId) {
      alert('Please fill in required fields: Name and Model');
      return;
    }

    createAgentMutation.mutate({
      name: formData.name,
      modelId: formData.modelId,
      maxTokens: formData.maxTokens,
      thinkingEnabled: formData.thinkingEnabled,
      skillIds: formData.skillIds,
      mcpIds: formData.mcpIds,
      status: 'active',
    });
  };

  const handleCancel = () => {
    navigate('/agents');
  };

  return (
    <div className="min-h-screen bg-bg-dark text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/agents"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            <span className="material-symbols-outlined text-xl">arrow_back</span>
            Back to Agent Management
          </Link>
          <h1 className="text-3xl font-semibold mb-2">Add New Agent</h1>
          <p className="text-gray-400">
            Configure and launch a new AI agent to the platform.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="bg-gray-800/50 rounded-lg p-8 space-y-6">
            {/* Agent Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2">
                Agent Name
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Customer Support Bot"
                className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                required
              />
            </div>

            {/* Model and Max Token */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label htmlFor="model" className="block text-sm font-medium mb-2">
                  Model
                </label>
                <select
                  id="model"
                  value={formData.modelId}
                  onChange={(e) => setFormData(prev => ({ ...prev, modelId: e.target.value }))}
                  className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent appearance-none"
                  required
                >
                  <option value="" disabled>Select a model</option>
                  {availableModels.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="maxTokens" className="block text-sm font-medium mb-2">
                  Max Token
                </label>
                <input
                  type="number"
                  id="maxTokens"
                  value={formData.maxTokens}
                  onChange={(e) => setFormData(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                  placeholder="e.g., 4096"
                  min="256"
                  max="200000"
                  className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  required
                />
              </div>
            </div>

            {/* Thinking Toggle */}
            <div className="flex items-center justify-between py-4 border-t border-b border-gray-700">
              <div>
                <div className="text-sm font-medium mb-1">Thinking</div>
                <div className="text-sm text-gray-400">
                  Enable the agent to show its thinking process.
                </div>
              </div>
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, thinkingEnabled: !prev.thinkingEnabled }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  formData.thinkingEnabled ? 'bg-primary' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    formData.thinkingEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Skills and MCPs */}
            <div className="grid grid-cols-2 gap-8 pt-2">
              {/* Skills */}
              <div>
                <h3 className="text-lg font-medium mb-4">Skills</h3>
                <div className="relative mb-4">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xl">
                    search
                  </span>
                  <input
                    type="text"
                    value={skillSearch}
                    onChange={(e) => setSkillSearch(e.target.value)}
                    placeholder="Search skills..."
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {filteredSkills.map(skill => (
                    <label key={skill.id} className="flex items-start gap-3 cursor-pointer group">
                      <input
                        type="checkbox"
                        checked={formData.skillIds.includes(skill.id)}
                        onChange={() => handleSkillToggle(skill.id)}
                        className="mt-1 w-4 h-4 rounded border-gray-600 bg-gray-700 text-primary focus:ring-2 focus:ring-primary focus:ring-offset-0"
                      />
                      <div className="flex-1">
                        <div className="text-sm text-white group-hover:text-primary transition-colors">
                          {skill.name}
                        </div>
                        <div className="text-xs text-gray-400 mt-0.5">
                          {skill.description}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* MCPs */}
              <div>
                <h3 className="text-lg font-medium mb-4">MCPs</h3>
                <div className="relative mb-4">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xl">
                    search
                  </span>
                  <input
                    type="text"
                    value={mcpSearch}
                    onChange={(e) => setMcpSearch(e.target.value)}
                    placeholder="Search MCPs..."
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {filteredMCPs.map(mcp => (
                    <label key={mcp.id} className="flex items-start gap-3 cursor-pointer group">
                      <input
                        type="checkbox"
                        checked={formData.mcpIds.includes(mcp.id)}
                        onChange={() => handleMCPToggle(mcp.id)}
                        className="mt-1 w-4 h-4 rounded border-gray-600 bg-gray-700 text-primary focus:ring-2 focus:ring-primary focus:ring-offset-0"
                      />
                      <div className="flex-1">
                        <div className="text-sm text-white group-hover:text-primary transition-colors">
                          {mcp.name}
                        </div>
                        <div className="text-xs text-gray-400 mt-0.5">
                          {mcp.description || 'No description'}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-4 mt-8">
            <Button
              type="button"
              variant="secondary"
              onClick={handleCancel}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Save Agent
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
