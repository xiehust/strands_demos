import { NavLink, useLocation } from 'react-router-dom';
import clsx from 'clsx';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

const navItems: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: 'dashboard' },
  { path: '/chat', label: 'Chat', icon: 'chat' },
  { path: '/agents', label: 'Agent Management', icon: 'smart_toy' },
  { path: '/skills', label: 'Skill Management', icon: 'construction' },
  { path: '/mcp', label: 'MCP Management', icon: 'dns' },
];

const bottomNavItems: NavItem[] = [
  { path: '/settings', label: 'Settings', icon: 'settings' },
  { path: '/help', label: 'Help', icon: 'help' },
];

export default function Sidebar() {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <aside className="w-64 bg-dark-bg border-r border-dark-border flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-dark-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary">smart_toy</span>
          </div>
          <div>
            <h1 className="font-semibold text-white">Agent Platform</h1>
            <p className="text-xs text-muted">Workspace</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
              isActive(item.path)
                ? 'bg-primary text-white'
                : 'text-muted hover:bg-dark-hover hover:text-white'
            )}
          >
            <span className="material-symbols-outlined text-xl">{item.icon}</span>
            <span className="text-sm font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom navigation */}
      <div className="py-4 px-3 border-t border-dark-border space-y-1">
        {bottomNavItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
              isActive(item.path)
                ? 'bg-primary text-white'
                : 'text-muted hover:bg-dark-hover hover:text-white'
            )}
          >
            <span className="material-symbols-outlined text-xl">{item.icon}</span>
            <span className="text-sm font-medium">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </aside>
  );
}
