import React from 'react';
import { cn } from './ActionBadge';
import { InventoryStatus } from '../types/recommendation';

interface Props {
  status: InventoryStatus;
  className?: string;
}

export const InventoryStatusBadge: React.FC<Props> = ({ status, className }) => {
  const getStyles = () => {
    switch (status) {
      case 'HEALTHY':
        return 'bg-emerald-100 text-emerald-800';
      case 'LOW STOCK':
        return 'bg-yellow-100 text-yellow-800';
      case 'STOCKOUT RISK':
        return 'bg-red-100 text-red-800';
      case 'OVERSTOCKED':
        return 'bg-purple-100 text-purple-800';
      case 'NEAR EXPIRY':
        return 'bg-orange-100 text-orange-800 font-bold';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <span className={cn('px-2.5 py-1 rounded-md text-xs font-semibold tracking-wide', getStyles(), className)}>
      {status}
    </span>
  );
};
