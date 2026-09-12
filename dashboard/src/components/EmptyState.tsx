import React from 'react';
import { cn } from './ActionBadge';
import { PackageOpen } from 'lucide-react';

interface Props {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<Props> = ({ 
  title = "No recommendations found", 
  message = "Try changing your filters.", 
  actionLabel, 
  onAction,
  className 
}) => {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-dashed border-slate-300", className)}>
      <div className="w-12 h-12 bg-slate-50 text-slate-400 rounded-full flex items-center justify-center mb-4">
        <PackageOpen size={24} />
      </div>
      <h3 className="text-lg font-medium text-slate-900 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 mb-4 max-w-sm">{message}</p>
      {actionLabel && onAction && (
        <button 
          onClick={onAction}
          className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
