import React from 'react';
import { cn } from './ActionBadge';

interface Props {
  riskPct: number;
  className?: string;
}

export const RiskBadge: React.FC<Props> = ({ riskPct, className }) => {
  const getRiskLevel = () => {
    if (riskPct > 60) return { label: 'CRITICAL', color: 'bg-red-100 text-red-800 border-red-200 font-bold' };
    if (riskPct > 30) return { label: 'HIGH', color: 'bg-orange-100 text-orange-800 border-orange-200' };
    if (riskPct > 10) return { label: 'MEDIUM', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' };
    return { label: 'LOW', color: 'bg-green-100 text-green-800 border-green-200' };
  };

  const config = getRiskLevel();

  return (
    <span className={cn('px-2 py-0.5 rounded text-xs font-medium border', config.color, className)}>
      {config.label} ({riskPct}%)
    </span>
  );
};
