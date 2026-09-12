import React from 'react';
import { cn } from './ActionBadge';

export const LoadingSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn("animate-pulse bg-slate-200 rounded", className)}></div>
  );
};

export const TableSkeleton: React.FC = () => {
  return (
    <div className="w-full bg-white rounded-xl border border-slate-200 overflow-hidden">
      <div className="h-12 border-b border-slate-200 bg-slate-50 flex items-center px-6 gap-4">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <LoadingSkeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {[1, 2, 3, 4, 5].map(row => (
        <div key={row} className="h-16 border-b border-slate-100 flex items-center px-6 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <LoadingSkeleton key={i} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
};

export const CardSkeleton: React.FC = () => (
  <div className="bg-white p-6 rounded-xl border border-slate-200">
    <LoadingSkeleton className="h-4 w-1/3 mb-4" />
    <LoadingSkeleton className="h-8 w-1/2" />
  </div>
);
