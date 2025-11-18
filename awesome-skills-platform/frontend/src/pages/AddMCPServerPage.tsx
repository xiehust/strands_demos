import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';

type ConnectionType = 'http' | 'stdio';

interface MCPFormData {
  name: string;
  type: ConnectionType;
  // HTTP fields
  serverAddress: string;
  headers: string;
  // stdio fields
  command: string;
  args: string;
  env: string;
}

export function AddMCPServerPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<MCPFormData>({
    name: '',
    type: 'http',
    serverAddress: '',
    headers: '',
    command: '',
    args: '',
    env: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Phase 3 - API call to create MCP server
    console.log('Creating MCP server:', formData);
    navigate('/mcp');
  };

  const handleCancel = () => {
    navigate('/mcp');
  };

  return (
    <div className="min-h-screen bg-bg-dark text-white p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/mcp"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            <span className="material-symbols-outlined text-xl">arrow_back</span>
            Back to MCP Management
          </Link>
          <h1 className="text-3xl font-semibold mb-2">Add New MCP Server</h1>
          <p className="text-gray-400">
            Configure and add a new server to your management platform.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-8 space-y-6">
            {/* Server Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2">
                Server Name
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Production-Cluster-A"
                className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                required
              />
            </div>

            {/* Type */}
            <div>
              <label htmlFor="type" className="block text-sm font-medium mb-2">
                Type
              </label>
              <select
                id="type"
                value={formData.type}
                onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as ConnectionType }))}
                className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent appearance-none cursor-pointer"
              >
                <option value="http">HTTP</option>
                <option value="stdio">stdio</option>
              </select>
            </div>

            {/* HTTP Fields */}
            {formData.type === 'http' && (
              <>
                {/* Server Address */}
                <div>
                  <label htmlFor="serverAddress" className="block text-sm font-medium mb-2">
                    Server Address
                  </label>
                  <input
                    type="text"
                    id="serverAddress"
                    value={formData.serverAddress}
                    onChange={(e) => setFormData(prev => ({ ...prev, serverAddress: e.target.value }))}
                    placeholder="e.g., http://192.168.1.100:8080"
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    required={formData.type === 'http'}
                  />
                </div>

                {/* Headers */}
                <div>
                  <label htmlFor="headers" className="block text-sm font-medium mb-2">
                    Headers
                  </label>
                  <textarea
                    id="headers"
                    value={formData.headers}
                    onChange={(e) => setFormData(prev => ({ ...prev, headers: e.target.value }))}
                    placeholder="e.g., Authorization: Bearer <token>"
                    rows={4}
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none font-mono text-sm"
                  />
                  <p className="mt-2 text-xs text-gray-400">
                    Enter one header per line in the format: Header-Name: Value
                  </p>
                </div>
              </>
            )}

            {/* stdio Fields */}
            {formData.type === 'stdio' && (
              <>
                {/* Command */}
                <div>
                  <label htmlFor="command" className="block text-sm font-medium mb-2">
                    Command
                  </label>
                  <input
                    type="text"
                    id="command"
                    value={formData.command}
                    onChange={(e) => setFormData(prev => ({ ...prev, command: e.target.value }))}
                    placeholder="e.g., /usr/local/bin/mcp-server"
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent font-mono text-sm"
                    required={formData.type === 'stdio'}
                  />
                  <p className="mt-2 text-xs text-gray-400">
                    Full path to the executable command
                  </p>
                </div>

                {/* Args */}
                <div>
                  <label htmlFor="args" className="block text-sm font-medium mb-2">
                    Args
                  </label>
                  <input
                    type="text"
                    id="args"
                    value={formData.args}
                    onChange={(e) => setFormData(prev => ({ ...prev, args: e.target.value }))}
                    placeholder="e.g., --port 8080 --config /etc/mcp.conf"
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent font-mono text-sm"
                  />
                  <p className="mt-2 text-xs text-gray-400">
                    Command line arguments (space-separated)
                  </p>
                </div>

                {/* Env */}
                <div>
                  <label htmlFor="env" className="block text-sm font-medium mb-2">
                    Env
                  </label>
                  <textarea
                    id="env"
                    value={formData.env}
                    onChange={(e) => setFormData(prev => ({ ...prev, env: e.target.value }))}
                    placeholder="e.g., NODE_ENV=production&#10;API_KEY=your-api-key"
                    rows={4}
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none font-mono text-sm"
                  />
                  <p className="mt-2 text-xs text-gray-400">
                    Environment variables (one per line in format: KEY=value)
                  </p>
                </div>
              </>
            )}
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
              Save
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
