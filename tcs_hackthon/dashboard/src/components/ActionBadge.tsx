import React from 'react';
import { RecommendedAction } from '../types/recommendation';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Props {
  action: RecommendedAction;
  className?: string;
}

export const ActionBadge: React.FC<Props> = ({ action, className }) => {
  const getStyles = () => {
    switch (action) {
      case 'PROMOTE':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'HIGH PRIORITY PROMOTION':
        return 'bg-purple-100 text-purple-800 border-purple-200 font-bold';
      case 'LIMITED PROMOTION':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'CLEARANCE PROMOTION':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      case 'NO PROMOTION':
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  return (
    <span className={cn('px-2.5 py-0.5 rounded-full text-xs font-medium border', getStyles(), className)}>
      {action}
    </span>
  );
};
