import React from 'react';
import { Recommendation } from '../types/recommendation';
import { ActionBadge } from './ActionBadge';
import { DemandBadge } from './DemandBadge';
import { Package, Sparkles } from 'lucide-react';

interface Props {
  recommendation: Recommendation;
  onClick?: () => void;
}

export const RecommendationCard: React.FC<Props> = ({ recommendation: rec, onClick }) => {
  const discount = rec.recommendation?.discount_pct ?? rec.discount_pct;
  const action = rec.recommendation?.action ?? rec.recommended_action;
  const objective = rec.recommendation?.objective;
  const reasonText = rec.reasons && rec.reasons.length > 0 ? rec.reasons[0] : rec.explanation;

  return (
    <div 
      onClick={onClick}
      className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-purple-300 transition-all cursor-pointer group flex flex-col h-full relative overflow-hidden"
    >
      <div className="flex justify-between items-start mb-3">
        <div className="pr-2">
          <span className="text-[10px] font-bold text-purple-600 uppercase tracking-wider bg-purple-50 px-2 py-0.5 rounded border border-purple-100 mb-1.5 inline-block">
            {rec.category}
          </span>
          <h3 className="font-semibold text-slate-900 group-hover:text-purple-700 transition-colors line-clamp-1 text-sm">{rec.product_name}</h3>
          <p className="text-xs text-slate-500 mt-0.5">{rec.dark_store_id} • {rec.city}</p>
        </div>
        <div className="text-right shrink-0">
          <span className="text-lg font-extrabold text-emerald-600">{discount}% OFF</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100">
        <div className="flex flex-col gap-0.5">
          <span className="text-slate-400 uppercase text-[10px] font-medium tracking-wider">Stock</span>
          <span className="font-semibold text-slate-800 flex items-center gap-1"><Package size={12} className="text-slate-400"/> {rec.current_stock} units</span>
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="text-slate-400 uppercase text-[10px] font-medium tracking-wider">Demand</span>
          <DemandBadge demand={rec.demand_status} className="w-fit scale-90 -ml-1" />
        </div>
      </div>

      {objective && (
        <div className="text-[11px] text-purple-900 bg-purple-50/70 p-2 rounded border border-purple-100 mb-3 line-clamp-1 font-medium">
          🎯 {objective}
        </div>
      )}

      <div className="mt-auto pt-3 border-t border-slate-100 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium text-slate-400 uppercase">Action</span>
          <ActionBadge action={action} />
        </div>
        <p className="text-xs text-slate-600 italic line-clamp-2">"{reasonText}"</p>
      </div>
    </div>
  );
};
