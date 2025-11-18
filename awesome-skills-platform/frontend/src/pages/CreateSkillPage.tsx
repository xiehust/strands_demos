import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';

type AgentStatus = 'idle' | 'generating' | 'completed' | 'error';

export function CreateSkillPage() {
  const navigate = useNavigate();
  const [description, setDescription] = useState('');
  const [agentStatus, setAgentStatus] = useState<AgentStatus>('idle');
  const [generatedSkill, setGeneratedSkill] = useState<string>('');

  const handleCreateSkill = () => {
    if (!description.trim()) {
      return;
    }

    setAgentStatus('generating');

    // Simulate AI generation
    setTimeout(() => {
      setGeneratedSkill(`# Weather Forecast Skill

## Description
A skill that retrieves current weather forecast for a given city using an external weather API.

## Usage
\`\`\`
skill: weather-forecast
city: San Francisco
\`\`\`

## Implementation
This skill uses OpenWeatherMap API to fetch real-time weather data.
`);
      setAgentStatus('completed');
    }, 3000);
  };

  const handleSaveSkill = () => {
    // TODO: Phase 3 - API call to save generated skill
    console.log('Saving skill:', { description, generatedSkill });
    navigate('/skills');
  };

  const getStatusIcon = () => {
    switch (agentStatus) {
      case 'generating':
        return (
          <div className="animate-spin">
            <span className="material-symbols-outlined text-primary text-2xl">
              progress_activity
            </span>
          </div>
        );
      case 'completed':
        return (
          <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-green-400 text-xl">
              check_circle
            </span>
          </div>
        );
      case 'error':
        return (
          <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-red-400 text-xl">
              error
            </span>
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
            <span className="material-symbols-outlined text-gray-400 text-xl">
              pending
            </span>
          </div>
        );
    }
  };

  const getStatusText = () => {
    switch (agentStatus) {
      case 'generating':
        return {
          title: 'Generating skill...',
          description: 'The agent is analyzing your description and creating the skill package.',
        };
      case 'completed':
        return {
          title: 'Skill generated successfully!',
          description: 'Review the generated skill below and click "Save Skill" to add it to your library.',
        };
      case 'error':
        return {
          title: 'Generation failed',
          description: 'An error occurred while generating the skill. Please try again.',
        };
      default:
        return {
          title: 'Waiting for input...',
          description: 'Describe your desired skill in the text area above and click "Create Skill" to begin.',
        };
    }
  };

  const statusInfo = getStatusText();

  return (
    <div className="min-h-screen bg-bg-dark text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/skills"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            <span className="material-symbols-outlined text-xl">arrow_back</span>
            Back to Skill Management
          </Link>
          <h1 className="text-3xl font-semibold mb-2">Create Skill with Agent</h1>
          <p className="text-gray-400">
            Describe the skill you want to create, and the Agent will generate it for you.
          </p>
        </div>

        {/* Skill Description */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-3">
            Skill Description
          </label>
          <div className="relative">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., A skill that takes a city name as input and returns the current weather forecast using an external API."
              rows={8}
              className="w-full bg-gray-800/50 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              disabled={agentStatus === 'generating'}
            />
          </div>
        </div>

        {/* Create Button */}
        <div className="flex justify-end mb-8">
          <Button
            type="button"
            variant="primary"
            onClick={handleCreateSkill}
            disabled={!description.trim() || agentStatus === 'generating'}
            icon={
              <span className="material-symbols-outlined">
                {agentStatus === 'generating' ? 'hourglass_empty' : 'auto_awesome'}
              </span>
            }
          >
            {agentStatus === 'generating' ? 'Generating...' : 'Create Skill'}
          </Button>
        </div>

        {/* Agent Status */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Agent Status</h2>

          <div className="flex items-start gap-4">
            {/* Status Icon */}
            <div className="flex-shrink-0 mt-1">
              {getStatusIcon()}
            </div>

            {/* Status Text */}
            <div className="flex-1">
              <h3 className="text-white font-medium mb-1">{statusInfo.title}</h3>
              <p className="text-sm text-gray-400">{statusInfo.description}</p>
            </div>
          </div>

          {/* Generated Skill Preview */}
          {agentStatus === 'completed' && generatedSkill && (
            <div className="mt-6 pt-6 border-t border-gray-700">
              <h3 className="text-sm font-medium mb-3 text-gray-300">
                Generated Skill Preview
              </h3>
              <div className="bg-gray-900/50 border border-gray-600 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                  {generatedSkill}
                </pre>
              </div>

              {/* Save Button */}
              <div className="flex justify-end gap-4 mt-6">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => navigate('/skills')}
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  variant="primary"
                  onClick={handleSaveSkill}
                  icon={<span className="material-symbols-outlined">save</span>}
                >
                  Save Skill
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
