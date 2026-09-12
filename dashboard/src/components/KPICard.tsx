import React from 'react';
import { cn } from './ActionBadge';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  className?: string;
}

export const KPICard: React.FC<KPICardProps> = ({ title, value, icon, trend, className }) => {
  return (
    <div className={cn('bg-white p-6 rounded-xl border border-slate-100 shadow-sm flex flex-col', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-500">{title}</h3>
        <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
          {icon}
        </div>
      </div>
      <div className="flex items-baseline gap-2 mt-auto">
        <span className="text-2xl font-bold text-slate-900">{value}</span>
        {trend && (
          <span className={cn('text-xs font-medium', trend.isPositive ? 'text-green-600' : 'text-red-600')}>
            {trend.isPositive ? '+' : ''}{trend.value}
          </span>
        )}
      </div>
    </div>
  );
};
