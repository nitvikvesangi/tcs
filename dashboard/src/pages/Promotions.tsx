import React, { useEffect, useState } from 'react';
import { getRecommendations } from '../services/api';
import { Recommendation } from '../types/recommendation';
import { useAppContext } from '../context/AppContext';
import { CardSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';
import { toast } from '../components/Toast';
import { MapPin, Package, Percent, Check, X, Sparkles, TrendingUp, ShieldAlert, ArrowRight } from 'lucide-react';
import { ActionBadge } from '../components/ActionBadge';
import { ProductDetailsModal } from '../components/ProductDetailsModal';

export const Promotions: React.FC = () => {
  const { filters } = useAppContext();
  const [data, setData] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      const res = await getRecommendations(filters);
      // Filter items recommended for promotion
      setData(res.filter(r => (r.recommendation?.action || r.recommended_action).includes('PROMOTE')));
      setLoading(false);
    };
    fetch();
  }, [filters]);

  const handleApprove = (productName: string) => {
    toast(`Promotion approved for ${productName} in demo mode.`);
  };

  const handleReject = (productName: string) => {
    toast(`Promotion rejected for ${productName} in demo mode.`);
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-900">Promotion Planner</h1>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
            {data.length} OPPORTUNITIES
          </span>
        </div>
        <p className="text-slate-500 mt-1">AI-ranked promotion opportunities with multi-scenario revenue and inventory simulations.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : data.length === 0 ? (
        <EmptyState title="No promotions found" message="There are currently no AI-recommended promotions matching your criteria." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {data.map(rec => {
            const discount = rec.recommendation?.discount_pct ?? rec.discount_pct;
            const action = rec.recommendation?.action ?? rec.recommended_action;
            const objective = rec.recommendation?.objective;
            const optimalOption = rec.options?.find(o => o.discount_pct === discount) || rec.options?.[0];

            return (
              <div key={rec.product_id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col hover:border-purple-200 transition-all">
                {/* Header */}
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50/50 p-4 border-b border-purple-100 flex justify-between items-start">
                  <div>
                    <div className="text-[10px] font-bold text-purple-700 uppercase tracking-wider mb-1 flex items-center gap-1">
                      <Sparkles size={13} className="text-purple-600" /> AI RECOMMENDED PROMOTION
                    </div>
                    <h3 className="font-bold text-slate-900 text-base">{rec.product_name}</h3>
                    <p className="text-xs text-slate-500">{rec.category} • {rec.product_id}</p>
                  </div>
                  <ActionBadge action={action} />
                </div>
                
                {/* Body */}
                <div className="p-5 space-y-4 flex-1">
                  {/* Objective */}
                  {objective && (
                    <div className="bg-purple-50/80 p-3 rounded-lg border border-purple-100 text-xs">
                      <span className="font-bold text-purple-900 block mb-0.5">Objective:</span>
                      <p className="text-purple-800 font-medium">🎯 {objective}</p>
                    </div>
                  )}

                  {/* Core Metrics Grid */}
                  <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <div>
                      <span className="text-slate-400 block mb-0.5">Location</span>
                      <span className="font-semibold text-slate-800 flex items-center gap-1"><MapPin size={13} className="text-purple-500"/> {rec.dark_store_id} ({rec.city})</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block mb-0.5">Current Stock</span>
                      <span className="font-semibold text-slate-800 flex items-center gap-1"><Package size={13} className="text-slate-500"/> {rec.current_stock} units</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block mb-0.5">Demand Signal</span>
                      <span className="font-semibold text-slate-800 flex items-center gap-1"><TrendingUp size={13} className="text-emerald-500"/> {rec.demand_status} ({rec.demand_trend_pct > 0 ? '+' : ''}{rec.demand_trend_pct}%)</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block mb-0.5">Recommended Discount</span>
                      <span className="font-bold text-base text-purple-700 flex items-center gap-0.5"><Percent size={14}/> {discount}%</span>
                    </div>
                  </div>

                  {/* Projected AI Simulation Output */}
                  {optimalOption && (
                    <div className="border border-slate-200 rounded-lg p-3 bg-white">
                      <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center justify-between">
                        <span>Projected Impact @ {optimalOption.discount_pct}%</span>
                        <span className="text-purple-600 font-mono text-[10px]">Score: {optimalOption.score.toFixed(1)}</span>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-center text-xs">
                        <div className="bg-slate-50 p-1.5 rounded">
                          <div className="text-[9px] text-slate-400 uppercase">Exp. Sales</div>
                          <div className="font-bold text-slate-900">{optimalOption.expected_sales_units}u</div>
                        </div>
                        <div className="bg-slate-50 p-1.5 rounded">
                          <div className="text-[9px] text-slate-400 uppercase">Exp. Revenue</div>
                          <div className="font-bold text-slate-900">₹{optimalOption.expected_revenue}</div>
                        </div>
                        <div className="bg-slate-50 p-1.5 rounded">
                          <div className="text-[9px] text-slate-400 uppercase">Profit Lift</div>
                          <div className="font-bold text-emerald-600">{optimalOption.profit_impact_pct > 0 ? '+' : ''}{optimalOption.profit_impact_pct}%</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* AI Reasons Bullet list */}
                  <div className="space-y-1.5 text-xs text-slate-600">
                    <span className="font-semibold text-slate-900 block text-[11px] uppercase tracking-wide">Key AI Factors:</span>
                    {(rec.reasons?.slice(0, 2) || [rec.explanation]).map((reason, idx) => (
                      <div key={idx} className="flex items-start gap-1.5 text-[11px] leading-relaxed">
                        <span className="text-purple-500 font-bold">•</span>
                        <span>{reason}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Footer Buttons */}
                <div className="p-4 border-t border-slate-100 flex gap-2 bg-slate-50">
                  <button 
                    onClick={() => setSelectedRec(rec)}
                    className="px-3 py-2 bg-white border border-slate-200 text-slate-600 font-medium rounded-lg hover:bg-slate-100 transition-colors text-xs flex items-center gap-1"
                  >
                    Simulate <ArrowRight size={12}/>
                  </button>
                  <button 
                    onClick={() => handleReject(rec.product_name)}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg hover:bg-red-50 hover:text-red-700 hover:border-red-200 transition-colors text-xs"
                  >
                    <X size={14} /> Reject
                  </button>
                  <button 
                    onClick={() => handleApprove(rec.product_name)}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors shadow-sm text-xs"
                  >
                    <Check size={14} /> Approve
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <ProductDetailsModal isOpen={!!selectedRec} onClose={() => setSelectedRec(null)} rec={selectedRec} />
    </div>
  );
};
