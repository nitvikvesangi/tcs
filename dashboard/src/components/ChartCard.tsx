import React from 'react';
import { cn } from './ActionBadge';

interface Props {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export const ChartCard: React.FC<Props> = ({ title, children, className }) => {
  return (
    <div className={cn('bg-white p-6 rounded-xl border border-slate-200 shadow-sm', className)}>
      <h3 className="text-sm font-bold text-slate-900 mb-6">{title}</h3>
      <div className="w-full">
        {children}
      </div>
    </div>
  );
};
