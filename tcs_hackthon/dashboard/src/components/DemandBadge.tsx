import React from 'react';
import { DemandStatus } from '../types/recommendation';
import { cn } from './ActionBadge';
import { TrendingUp, TrendingDown, Minus, ArrowUp, ArrowDown } from 'lucide-react';

interface Props {
  demand: DemandStatus;
  className?: string;
}

export const DemandBadge: React.FC<Props> = ({ demand, className }) => {
  const getConfig = () => {
    switch (demand) {
      case 'High':
        return { color: 'text-green-700 bg-green-50 border-green-200', icon: <ArrowUp className="w-3 h-3 mr-1" /> };
      case 'Rising':
        return { color: 'text-emerald-700 bg-emerald-50 border-emerald-200', icon: <TrendingUp className="w-3 h-3 mr-1" /> };
      case 'Stable':
        return { color: 'text-slate-700 bg-slate-50 border-slate-200', icon: <Minus className="w-3 h-3 mr-1" /> };
      case 'Falling':
        return { color: 'text-orange-700 bg-orange-50 border-orange-200', icon: <TrendingDown className="w-3 h-3 mr-1" /> };
      case 'Low':
        return { color: 'text-red-700 bg-red-50 border-red-200', icon: <ArrowDown className="w-3 h-3 mr-1" /> };
      default:
        return { color: 'text-gray-700 bg-gray-50 border-gray-200', icon: null };
    }
  };

  const config = getConfig();

  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border', config.color, className)}>
      {config.icon}
      {demand}
    </span>
  );
};
