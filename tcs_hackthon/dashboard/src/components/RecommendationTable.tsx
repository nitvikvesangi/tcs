import React from 'react';
import { Recommendation } from '../types/recommendation';
import { ActionBadge } from './ActionBadge';
import { DemandBadge } from './DemandBadge';
import { RiskBadge } from './RiskBadge';
import { cn } from './ActionBadge';

interface Props {
  data: Recommendation[];
  onRowClick?: (rec: Recommendation) => void;
  className?: string;
}

export const RecommendationTable: React.FC<Props> = ({ data, onRowClick, className }) => {
  return (
    <div className={cn("bg-white rounded-xl border border-slate-200 overflow-x-auto", className)}>
      <table className="w-full text-left border-collapse min-w-[900px]">
        <thead>
          <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
            <th className="px-6 py-4 font-medium">Product</th>
            <th className="px-6 py-4 font-medium">Store</th>
            <th className="px-6 py-4 font-medium">Stock</th>
            <th className="px-6 py-4 font-medium">Demand</th>
            <th className="px-6 py-4 font-medium">Risk</th>
            <th className="px-6 py-4 font-medium">Action</th>
            <th className="px-6 py-4 font-medium text-right">Discount</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {data.map((rec) => (
            <tr 
              key={rec.product_id} 
              onClick={() => onRowClick?.(rec)}
              className={cn(
                "group transition-colors", 
                onRowClick ? "cursor-pointer hover:bg-slate-50" : ""
              )}
            >
              <td className="px-6 py-4">
                <div className="font-medium text-slate-900 group-hover:text-purple-700 transition-colors">{rec.product_name}</div>
                <div className="text-xs text-slate-500">{rec.category} • {rec.product_id}</div>
              </td>
              <td className="px-6 py-4 text-sm text-slate-600">
                <div>{rec.dark_store_id}</div>
                <div className="text-xs text-slate-400">{rec.city}</div>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm font-medium text-slate-900">{rec.current_stock}</div>
              </td>
              <td className="px-6 py-4">
                <DemandBadge demand={rec.demand_status} />
              </td>
              <td className="px-6 py-4">
                <RiskBadge riskPct={rec.stockout_risk_pct} />
              </td>
              <td className="px-6 py-4">
                <ActionBadge action={rec.recommended_action} />
              </td>
              <td className="px-6 py-4 text-right">
                <span className={cn(
                  "font-bold", 
                  rec.discount_pct > 0 ? "text-green-600" : "text-slate-400"
                )}>
                  {rec.discount_pct}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
