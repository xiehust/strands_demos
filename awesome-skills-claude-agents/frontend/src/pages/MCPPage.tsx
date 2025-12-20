import { useState } from 'react';
import { SearchBar, StatusBadge, Button, Modal, SkeletonTable } from '../components/common';
import type { MCPServer } from '../types';
import { useLoadingState } from '../hooks/useLoadingState';

// Mock data for demo
const mockMCPServers: MCPServer[] = [
  {
    id: '1',
    name: 'Production-Cluster-A',
    description: 'Main production cluster',
    connectionType: 'stdio',
    config: { command: 'npx', args: ['-y', '@modelcontextprotocol/server-filesystem', '/workspace'] },
    status: 'online',
    endpoint: '192.168.1.100:8080',
    version: 'v2.1.3',
    agentCount: 150,
    createdAt: '2025-01-01',
    updatedAt: '2025-01-01',
  },
  {
    id: '2',
    name: 'Staging-EU-West',
    description: 'Staging environment for EU region',
    connectionType: 'sse',
    config: { url: 'http://staging-eu.internal:8080/sse' },
    status: 'offline',
    endpoint: '10.0.5.23:8080',
    version: 'v2.1.1',
    agentCount: 75,
    createdAt: '2025-01-02',
    updatedAt: '2025-01-02',
  },
  {
    id: '3',
    name: 'Development-US-East',
    description: 'Development environment',
    connectionType: 'http',
    config: { url: 'http://dev.mcp.internal:9000' },
    status: 'error',
    endpoint: 'dev.mcp.internal:9000',
    version: 'v2.2.0-beta',
    agentCount: 12,
    createdAt: '2025-01-03',
    updatedAt: '2025-01-03',
  },
];

export default function MCPPage() {
  const [servers, setServers] = useState(mockMCPServers);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'online' | 'offline' | 'error'>('all');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);
  const [isInitialLoading] = useState(false);
  const testConnectionState = useLoadingState();

  const filteredServers = servers.filter((server) => {
    const matchesSearch = server.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || server.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleDelete = (id: string) => {
    setServers((prev) => prev.filter((server) => server.id !== id));
  };

  const handleTestConnection = async (id: string) => {
    await testConnectionState.execute(async () => {
      // Simulate connection test delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      setServers((prev) =>
        prev.map((server) =>
          server.id === id ? { ...server, status: 'online' as const } : server
        )
      );
    });
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">MCP Server Management</h1>
          <p className="text-muted mt-1">Monitor and manage all MCP servers from this central dashboard.</p>
        </div>
        <Button icon="add" onClick={() => setIsAddModalOpen(true)}>
          Add MCP Server
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-6">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search servers..."
          className="w-96"
        />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as typeof statusFilter)}
          className="px-4 py-2.5 bg-dark-card border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
        >
          <option value="all">Status: All</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
          <option value="error">Error</option>
        </select>
      </div>

      {/* MCP Servers Table */}
      <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden">
        {isInitialLoading ? (
          <SkeletonTable rows={5} columns={7} />
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="px-6 py-4 text-left">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-dark-border bg-dark-bg text-primary focus:ring-primary"
                  />
                </th>
                <th className="px-6 py-4 text-left text-sm font-medium text-muted">Server Name</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-muted">Status</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-muted">Endpoint/IP</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-muted">Version</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-muted">Agent Count</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-muted">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredServers.map((server) => (
                <tr
                  key={server.id}
                  className="border-b border-dark-border hover:bg-dark-hover transition-colors"
                >
                  <td className="px-6 py-4">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-dark-border bg-dark-bg text-primary focus:ring-primary"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-white font-medium">{server.name}</span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={server.status} />
                  </td>
                  <td className="px-6 py-4 text-muted">{server.endpoint}</td>
                  <td className="px-6 py-4 text-muted">{server.version}</td>
                  <td className="px-6 py-4 text-muted">{server.agentCount} Agents</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => setSelectedServer(server)}
                        className="p-2 rounded-lg text-muted hover:text-white hover:bg-dark-hover transition-colors"
                      >
                        <span className="material-symbols-outlined text-xl">edit</span>
                      </button>
                      <button
                        onClick={() => handleDelete(server.id)}
                        className="p-2 rounded-lg text-muted hover:text-status-error hover:bg-status-error/10 transition-colors"
                      >
                        <span className="material-symbols-outlined text-xl">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {filteredServers.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center">
                    <span className="material-symbols-outlined text-4xl text-muted mb-2">dns</span>
                    <p className="text-muted">No MCP servers found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Add/Edit Modal */}
      <Modal
        isOpen={isAddModalOpen || selectedServer !== null}
        onClose={() => {
          setIsAddModalOpen(false);
          setSelectedServer(null);
        }}
        title={selectedServer ? 'Edit MCP Server' : 'Add MCP Server'}
        size="lg"
      >
        <MCPServerForm
          server={selectedServer}
          onClose={() => {
            setIsAddModalOpen(false);
            setSelectedServer(null);
          }}
          onSave={(server) => {
            if (selectedServer) {
              setServers((prev) =>
                prev.map((s) => (s.id === server.id ? server : s))
              );
            } else {
              setServers((prev) => [...prev, server]);
            }
            setIsAddModalOpen(false);
            setSelectedServer(null);
          }}
          onTestConnection={handleTestConnection}
        />
      </Modal>
    </div>
  );
}

// MCP Server Form Component
function MCPServerForm({
  server,
  onClose,
  onSave,
  onTestConnection,
}: {
  server: MCPServer | null;
  onClose: () => void;
  onSave: (server: MCPServer) => void;
  onTestConnection: (id: string) => void;
}) {
  const [name, setName] = useState(server?.name || '');
  const [description, setDescription] = useState(server?.description || '');
  const [connectionType, setConnectionType] = useState<'stdio' | 'sse' | 'http'>(
    server?.connectionType || 'stdio'
  );
  const [command, setCommand] = useState(
    server?.connectionType === 'stdio' ? (server.config.command as string) : ''
  );
  const [args, setArgs] = useState(
    server?.connectionType === 'stdio' ? (server.config.args as string[]).join(' ') : ''
  );
  const [url, setUrl] = useState(
    server?.connectionType !== 'stdio' ? (server?.config.url as string) || '' : ''
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    let config: Record<string, unknown> = {};
    let endpoint = '';

    if (connectionType === 'stdio') {
      config = { command, args: args.split(' ').filter(Boolean) };
      endpoint = `${command} ${args}`;
    } else {
      config = { url };
      endpoint = url.replace(/^https?:\/\//, '');
    }

    const newServer: MCPServer = {
      id: server?.id || Date.now().toString(),
      name,
      description,
      connectionType,
      config,
      status: server?.status || 'offline',
      endpoint,
      version: server?.version || 'v1.0.0',
      agentCount: server?.agentCount || 0,
      createdAt: server?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    onSave(newServer);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-muted mb-2">Server Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., Production-Main"
          required
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-muted mb-2">Description</label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g., Main production MCP server"
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-muted mb-2">Connection Type</label>
        <div className="flex gap-4">
          {(['stdio', 'sse', 'http'] as const).map((type) => (
            <label key={type} className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="connectionType"
                value={type}
                checked={connectionType === type}
                onChange={(e) => setConnectionType(e.target.value as typeof connectionType)}
                className="w-4 h-4 border-dark-border bg-dark-bg text-primary focus:ring-primary"
              />
              <span className="text-white uppercase">{type}</span>
            </label>
          ))}
        </div>
      </div>

      {connectionType === 'stdio' ? (
        <>
          <div>
            <label className="block text-sm font-medium text-muted mb-2">Command</label>
            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="e.g., npx"
              required
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-muted mb-2">Arguments</label>
            <input
              type="text"
              value={args}
              onChange={(e) => setArgs(e.target.value)}
              placeholder="e.g., -y @modelcontextprotocol/server-filesystem /workspace"
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary"
            />
          </div>
        </>
      ) : (
        <div>
          <label className="block text-sm font-medium text-muted mb-2">URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={connectionType === 'sse' ? 'http://server:port/sse' : 'http://server:port'}
            required
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder:text-muted focus:outline-none focus:border-primary"
          />
        </div>
      )}

      <div className="flex gap-3 pt-4">
        <Button type="button" variant="secondary" onClick={onClose}>
          Cancel
        </Button>
        {server && (
          <Button
            type="button"
            variant="secondary"
            onClick={() => onTestConnection(server.id)}
          >
            Test Connection
          </Button>
        )}
        <Button type="submit" className="flex-1">
          {server ? 'Save Changes' : 'Add Server'}
        </Button>
      </div>
    </form>
  );
}
