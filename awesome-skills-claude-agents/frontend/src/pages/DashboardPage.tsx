import { Link } from 'react-router-dom';

const quickActions = [
  {
    title: 'Start a Chat',
    description: 'Begin a conversation with an AI agent',
    icon: 'chat',
    path: '/chat',
    color: 'bg-blue-500/20 text-blue-400',
  },
  {
    title: 'Manage Agents',
    description: 'Create and configure your AI agents',
    icon: 'smart_toy',
    path: '/agents',
    color: 'bg-purple-500/20 text-purple-400',
  },
  {
    title: 'View Skills',
    description: 'Browse and manage available skills',
    icon: 'construction',
    path: '/skills',
    color: 'bg-green-500/20 text-green-400',
  },
  {
    title: 'MCP Servers',
    description: 'Monitor and configure MCP connections',
    icon: 'dns',
    path: '/mcp',
    color: 'bg-orange-500/20 text-orange-400',
  },
];

export default function DashboardPage() {
  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome to Agent Platform</h1>
        <p className="text-muted">
          Manage your AI agents, skills, and MCP server connections
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <Link
              key={action.path}
              to={action.path}
              className="p-6 bg-dark-card border border-dark-border rounded-xl hover:bg-dark-hover transition-colors group"
            >
              <div
                className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${action.color}`}
              >
                <span className="material-symbols-outlined text-2xl">{action.icon}</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-primary transition-colors">
                {action.title}
              </h3>
              <p className="text-sm text-muted">{action.description}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-6 bg-dark-card border border-dark-border rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-muted">Total Agents</span>
              <span className="material-symbols-outlined text-primary">smart_toy</span>
            </div>
            <p className="text-3xl font-bold text-white">3</p>
            <p className="text-sm text-status-online mt-1">2 active</p>
          </div>
          <div className="p-6 bg-dark-card border border-dark-border rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-muted">Available Skills</span>
              <span className="material-symbols-outlined text-green-400">construction</span>
            </div>
            <p className="text-3xl font-bold text-white">5</p>
            <p className="text-sm text-muted mt-1">3 system, 2 custom</p>
          </div>
          <div className="p-6 bg-dark-card border border-dark-border rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-muted">MCP Servers</span>
              <span className="material-symbols-outlined text-orange-400">dns</span>
            </div>
            <p className="text-3xl font-bold text-white">3</p>
            <p className="text-sm text-status-online mt-1">1 online</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Recent Conversations</h2>
        <div className="bg-dark-card border border-dark-border rounded-xl p-6">
          <div className="text-center py-8">
            <span className="material-symbols-outlined text-4xl text-muted mb-2">chat</span>
            <p className="text-muted">No recent conversations</p>
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors"
            >
              <span className="material-symbols-outlined text-xl">add</span>
              Start New Chat
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
