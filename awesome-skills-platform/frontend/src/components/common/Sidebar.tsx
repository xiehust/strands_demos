import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

const navItems: NavItem[] = [
  { path: '/', label: 'Chat', icon: 'chat' },
  { path: '/agents', label: 'Agent Management', icon: 'smart_toy' },
  { path: '/skills', label: 'Skills', icon: 'extension' },
  { path: '/mcp', label: 'MCP Servers', icon: 'dns' },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-white">android</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold">AI Agent Platform</h1>
            <p className="text-sm text-text-muted">Workspace</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              )}
            >
              <span className="material-symbols-outlined text-xl">
                {item.icon}
              </span>
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800 space-y-1">
        <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 transition-colors w-full">
          <span className="material-symbols-outlined text-xl">settings</span>
          <span className="font-medium">Settings</span>
        </button>
        <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 transition-colors w-full">
          <span className="material-symbols-outlined text-xl">help</span>
          <span className="font-medium">Help</span>
        </button>
      </div>
    </aside>
  );
}
