import clsx from 'clsx';

export interface ChipItem {
  id: string;
  name: string;
  description?: string;
}

interface ReadOnlyChipsProps {
  label: string;
  icon?: string;
  items: ChipItem[];
  emptyText?: string;
  loading?: boolean;
  className?: string;
}

/**
 * A read-only component to display a list of items as chips.
 * Used in ChatPage to show agent's configured Skills and MCPs.
 */
export default function ReadOnlyChips({
  label,
  icon,
  items,
  emptyText = 'None configured',
  loading = false,
  className,
}: ReadOnlyChipsProps) {
  return (
    <div className={clsx('', className)}>
      <div className="flex items-center gap-2 mb-2">
        {icon && (
          <span className="material-symbols-outlined text-muted text-sm">{icon}</span>
        )}
        <span className="text-xs font-medium text-muted uppercase tracking-wider">
          {label}
        </span>
      </div>

      {loading ? (
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-muted border-t-primary rounded-full animate-spin" />
          <span className="text-xs text-muted">Loading...</span>
        </div>
      ) : items.length === 0 ? (
        <span className="text-xs text-muted italic">{emptyText}</span>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {items.map((item) => (
            <span
              key={item.id}
              className="inline-flex items-center px-2 py-1 bg-dark-hover text-white rounded text-xs"
              title={item.description}
            >
              {item.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
