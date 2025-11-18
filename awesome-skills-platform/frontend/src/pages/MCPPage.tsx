import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mcpApi } from '../services/mcp';
import { Button } from '../components/common/Button';

export function MCPPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch MCP servers
  const { data: mcpServers = [], isLoading } = useQuery({
    queryKey: ['mcp'],
    queryFn: mcpApi.list,
  });

  // Delete MCP server mutation
  const deleteMCPMutation = useMutation({
    mutationFn: mcpApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mcp'] });
    },
  });
  return (
    <div className="p-8 h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">MCP Server Management</h1>
        <p className="text-text-muted">
          Monitor and manage all MCP servers from this central dashboard.
        </p>
      </div>

      {/* Toolbar */}
      <div className="mb-6 flex items-center gap-4">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
              search
            </span>
            <input
              type="text"
              placeholder="Search servers..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <select className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-primary">
          <option>Status: All</option>
          <option>Status: Online</option>
          <option>Status: Offline</option>
          <option>Status: Error</option>
        </select>

        <Button onClick={() => navigate('/mcp/add')}>
          <span className="material-symbols-outlined">add</span>
          Add MCP Server
        </Button>
      </div>

      {/* MCP Servers Table */}
      <div className="flex-1 bg-gray-900 rounded-lg border border-gray-800 overflow-hidden flex flex-col">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-text-muted">Loading MCP servers...</div>
          </div>
        ) : mcpServers.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="text-text-muted mb-4">No MCP servers found</div>
            <Button onClick={() => navigate('/mcp/add')}>
              <span className="material-symbols-outlined">add</span>
              Add Your First MCP Server
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto flex-1">
            <table className="w-full">
              <thead className="border-b border-gray-800 bg-gray-900 sticky top-0">
                <tr className="text-left">
                  <th className="px-6 py-4">
                    <input type="checkbox" className="w-4 h-4 rounded border-gray-600" />
                  </th>
                  <th className="px-6 py-4 font-medium text-text-muted">Server Name</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Status</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Endpoint/IP</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Version</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Agent Count</th>
                  <th className="px-6 py-4 font-medium text-text-muted">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mcpServers.map((server) => (
                  <tr
                    key={server.id}
                    className="border-b border-gray-800 hover:bg-gray-800 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <input type="checkbox" className="w-4 h-4 rounded border-gray-600" />
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium">{server.name}</div>
                        {server.description && (
                          <div className="text-sm text-text-muted mt-0.5">{server.description}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                          server.status === 'online'
                            ? 'bg-green-500/10 text-green-400'
                            : server.status === 'offline'
                            ? 'bg-gray-500/10 text-gray-400'
                            : 'bg-red-500/10 text-red-400'
                        }`}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                        {server.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-text-muted font-mono text-sm">
                      {server.endpoint}
                    </td>
                    <td className="px-6 py-4 text-text-muted">{server.version || 'N/A'}</td>
                    <td className="px-6 py-4 text-text-muted">{server.agentCount || 0} Agents</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button className="text-primary hover:text-blue-400 transition-colors text-sm font-medium">
                          Edit
                        </button>
                        <span className="text-gray-600">|</span>
                        <button
                          onClick={() => {
                            if (confirm(`Delete MCP server "${server.name}"?`)) {
                              deleteMCPMutation.mutate(server.id);
                            }
                          }}
                          disabled={deleteMCPMutation.isPending}
                          className="text-red-400 hover:text-red-300 transition-colors text-sm font-medium disabled:opacity-50"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
