import React, { useEffect, useState } from 'react';
import { Recommendation, RecommendationOption } from '../types/recommendation';
import { X, MapPin, TrendingUp, Calendar, Cloud, Clock, AlertTriangle, Sparkles, CheckCircle2, ShieldAlert, BarChart2, Layers } from 'lucide-react';
import { ActionBadge } from './ActionBadge';
import { cn } from './ActionBadge';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  rec: Recommendation | null;
}

export const ProductDetailsModal: React.FC<Props> = ({ isOpen, onClose, rec }) => {
  const [selectedOption, setSelectedOption] = useState<RecommendationOption | null>(null);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      if (rec?.options && rec.options.length > 0) {
        // default select the option that matches recommended discount or highest score
        const match = rec.options.find(o => o.discount_pct === rec.recommendation.discount_pct) || rec.options[0];
        setSelectedOption(match);
      }
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen, rec]);

  if (!isOpen || !rec) return null;

  const getUrgencyColor = (urgency: string) => {
    switch (urgency?.toUpperCase()) {
      case 'CRITICAL': return 'bg-red-500 text-white';
      case 'HIGH': return 'bg-orange-500 text-white';
      case 'MEDIUM': return 'bg-yellow-500 text-slate-900';
      case 'LOW':
      default: return 'bg-emerald-500 text-white';
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex justify-end">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" 
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="relative w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-purple-600 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                {rec.category}
              </span>
              <span className="text-xs text-slate-400 font-mono">ID: {rec.product_id}</span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 leading-tight">{rec.product_name}</h2>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-slate-100 text-slate-500 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Top Location & Stock Stats */}
          <div className="grid grid-cols-3 gap-3 bg-slate-50 border border-slate-200 rounded-xl p-4">
            <div>
              <div className="text-xs text-slate-500 flex items-center gap-1 mb-1">
                <MapPin size={13} className="text-purple-600"/> Dark Store
              </div>
              <div className="font-bold text-slate-900 text-sm">{rec.dark_store_id}</div>
              <div className="text-xs text-slate-500">{rec.city}</div>
            </div>
            <div>
              <div className="text-xs text-slate-500 mb-1">Current Stock</div>
              <div className="text-lg font-bold text-slate-900">{rec.current_stock} <span className="text-xs font-normal text-slate-500">units</span></div>
              <div className="text-xs text-slate-500">{rec.days_to_expiry}d to expiry</div>
            </div>
            <div>
              <div className="text-xs text-slate-500 mb-1">Stockout Risk</div>
              <div className={cn("text-lg font-bold", rec.stockout_risk_pct > 30 ? "text-red-600" : "text-emerald-600")}>
                {rec.stockout_risk_pct}%
              </div>
              <div className="text-xs text-slate-500">Demand: {rec.demand_status}</div>
            </div>
          </div>

          {/* AI Decision Box */}
          <section className="bg-gradient-to-br from-purple-900 to-indigo-950 text-white rounded-2xl p-5 shadow-lg relative overflow-hidden">
            <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 w-32 h-32 bg-purple-500/20 rounded-full blur-2xl" />
            
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-purple-500/30 rounded-lg backdrop-blur-md">
                  <Sparkles size={16} className="text-purple-300" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-purple-200">AI Recommendation Engine</span>
              </div>
              <ActionBadge action={rec.recommendation?.action || rec.recommended_action} className="bg-white/10 text-white border-white/20 backdrop-blur-md font-semibold text-xs" />
            </div>

            {/* Strategic Objective */}
            <div className="mb-4">
              <div className="text-xs text-purple-300 uppercase font-semibold tracking-wide mb-1">Objective</div>
              <p className="text-sm font-medium text-purple-100 bg-white/5 p-3 rounded-lg border border-white/10">
                🎯 {rec.recommendation?.objective || "Optimize inventory turnover and preserve margin."}
              </p>
            </div>

            {/* AI Rationale Reasons */}
            <div>
              <div className="text-xs text-purple-300 uppercase font-semibold tracking-wide mb-2">Why AI Recommended This</div>
              <div className="space-y-2">
                {(rec.reasons && rec.reasons.length > 0 ? rec.reasons : [rec.explanation]).map((reason, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-200 bg-white/5 px-3 py-2 rounded-lg border border-white/5">
                    <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Inventory Urgency Snapshot */}
          {rec.inventory_snapshot && (
            <section className="border border-slate-200 rounded-xl p-4 bg-white shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                  <Layers size={14} className="text-slate-500" /> Inventory Snapshot & Urgency
                </h3>
                <div className="flex items-center gap-1.5 text-xs font-semibold">
                  <span className="text-slate-500">Alert Score:</span>
                  <span className={cn(
                    "px-2 py-0.5 rounded font-mono font-bold",
                    rec.inventory_snapshot.inventory_alert_score > 70 ? "bg-red-100 text-red-700" :
                    rec.inventory_snapshot.inventory_alert_score > 40 ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-700"
                  )}>
                    {rec.inventory_snapshot.inventory_alert_score}/100
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
                  <div className="text-[11px] text-slate-500 font-medium mb-1">Stockout Urgency</div>
                  <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded", getUrgencyColor(rec.inventory_snapshot.stockout_urgency))}>
                    {rec.inventory_snapshot.stockout_urgency}
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
                  <div className="text-[11px] text-slate-500 font-medium mb-1">Overstock Urgency</div>
                  <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded", getUrgencyColor(rec.inventory_snapshot.overstock_urgency))}>
                    {rec.inventory_snapshot.overstock_urgency}
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
                  <div className="text-[11px] text-slate-500 font-medium mb-1">Expiry Urgency</div>
                  <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded", getUrgencyColor(rec.inventory_snapshot.expiry_urgency))}>
                    {rec.inventory_snapshot.expiry_urgency}
                  </span>
                </div>
              </div>
            </section>
          )}

          {/* Scenario Simulation Options (AI Options Matrix) */}
          {rec.options && rec.options.length > 0 && (
            <section className="border border-purple-100 rounded-xl p-4 bg-purple-50/30">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-purple-900 flex items-center gap-1.5">
                    <BarChart2 size={14} className="text-purple-600" /> Scenario Simulator (AI Options)
                  </h3>
                  <p className="text-[11px] text-slate-500">Compare discount trade-offs evaluated by the optimization model</p>
                </div>
              </div>

              {/* Option Selector Tabs */}
              <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
                {rec.options.map((opt, i) => {
                  const isSelected = selectedOption?.discount_pct === opt.discount_pct;
                  const isRecommended = opt.discount_pct === (rec.recommendation?.discount_pct ?? rec.discount_pct);
                  return (
                    <button
                      key={i}
                      onClick={() => setSelectedOption(opt)}
                      className={cn(
                        "px-3 py-2 rounded-lg text-xs font-medium transition-all text-left border shrink-0 flex flex-col gap-0.5",
                        isSelected
                          ? "bg-purple-600 text-white border-purple-600 shadow-sm"
                          : "bg-white text-slate-700 border-slate-200 hover:border-purple-300"
                      )}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-bold">{opt.discount_pct}% Discount</span>
                        {isRecommended && (
                          <span className={cn("text-[9px] px-1 py-0.2 rounded font-semibold uppercase", isSelected ? "bg-white text-purple-700" : "bg-purple-100 text-purple-800")}>
                            Optimal
                          </span>
                        )}
                      </div>
                      <span className={cn("text-[10px]", isSelected ? "text-purple-200" : "text-slate-400")}>
                        AI Score: {opt.score.toFixed(1)}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Active Option Metrics */}
              {selectedOption && (
                <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400 font-medium uppercase">Expected Sales</div>
                    <div className="text-sm font-bold text-slate-900">{selectedOption.expected_sales_units} units</div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400 font-medium uppercase">Expected Revenue</div>
                    <div className="text-sm font-bold text-slate-900">₹{selectedOption.expected_revenue.toLocaleString()}</div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400 font-medium uppercase">Profit Impact</div>
                    <div className={cn("text-sm font-bold", selectedOption.profit_impact_pct >= 0 ? "text-emerald-600" : "text-red-600")}>
                      {selectedOption.profit_impact_pct > 0 ? '+' : ''}{selectedOption.profit_impact_pct}%
                    </div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400 font-medium uppercase">Stockout Risk</div>
                    <div className={cn("text-sm font-bold", selectedOption.stockout_risk_pct > 30 ? "text-orange-600" : "text-slate-700")}>
                      {selectedOption.stockout_risk_pct}%
                    </div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400 font-medium uppercase">Inventory Reduction</div>
                    <div className="text-sm font-bold text-purple-700">{selectedOption.inventory_reduction_pct}%</div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400 font-medium uppercase">Waste Reduction</div>
                    <div className="text-sm font-bold text-emerald-600">{selectedOption.expiry_waste_reduction_pct}%</div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100 col-span-2">
                    <div className="text-[10px] text-slate-400 font-medium uppercase">Expected Profit</div>
                    <div className="text-sm font-bold text-slate-900">₹{selectedOption.expected_profit.toLocaleString()}</div>
                  </div>
                </div>
              )}
            </section>
          )}

          {/* Risk Alert Flag */}
          {rec.risk_flag ? (
            <section className="bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
              <ShieldAlert className="text-red-600 shrink-0" size={20} />
              <div>
                <h4 className="text-sm font-bold text-red-900">Risk Flag: {rec.risk_flag}</h4>
                <p className="text-xs text-red-700 mt-0.5">
                  Stockout risk is {rec.stockout_risk_pct}%. Immediate store intervention or replenishment is flagged.
                </p>
              </div>
            </section>
          ) : (
            <section className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex gap-3">
              <CheckCircle2 className="text-emerald-600 shrink-0" size={20} />
              <div>
                <h4 className="text-sm font-bold text-emerald-900">No Critical Operational Risk Detected</h4>
                <p className="text-xs text-emerald-700 mt-0.5">Inventory levels and demand signals are within safe thresholds.</p>
              </div>
            </section>
          )}

          {/* Hyperlocal Context Grid */}
          <section>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Hyperlocal Signals</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="border border-slate-200 rounded-lg p-3 bg-white">
                <div className="text-slate-400 mb-1 flex items-center gap-1"><TrendingUp size={12}/> Demand Trend</div>
                <div className="font-semibold text-slate-900">{rec.demand_trend_pct > 0 ? '+' : ''}{rec.demand_trend_pct}% ({rec.trend_signal})</div>
              </div>
              <div className="border border-slate-200 rounded-lg p-3 bg-white">
                <div className="text-slate-400 mb-1 flex items-center gap-1"><Calendar size={12}/> Shelf Life</div>
                <div className="font-semibold text-slate-900">{rec.days_to_expiry} days remaining</div>
              </div>
              <div className="border border-slate-200 rounded-lg p-3 bg-white">
                <div className="text-slate-400 mb-1 flex items-center gap-1"><Cloud size={12}/> Weather Index</div>
                <div className="font-semibold text-slate-900">{rec.weather_condition}</div>
              </div>
              <div className="border border-slate-200 rounded-lg p-3 bg-white">
                <div className="text-slate-400 mb-1 flex items-center gap-1"><Clock size={12}/> Timing</div>
                <div className="font-semibold text-slate-900">{rec.time_of_day} {rec.is_weekend ? '(Weekend)' : ''}</div>
              </div>
              <div className="border border-slate-200 rounded-lg p-3 bg-white">
                <div className="text-slate-400 mb-1">Gross Margin</div>
                <div className="font-semibold text-slate-900">{rec.gross_margin_before_promo}%</div>
              </div>
              <div className="border border-slate-200 rounded-lg p-3 bg-white">
                <div className="text-slate-400 mb-1">Price Gap</div>
                <div className="font-semibold text-slate-900">{rec.competitor_price_gap_pct}% vs Competitor</div>
              </div>
            </div>
          </section>

        </div>
        
        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex gap-3 sticky bottom-0 z-10">
          <button onClick={onClose} className="flex-1 py-2.5 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg hover:bg-slate-100 transition-colors text-sm">
            Close
          </button>
          {(rec.recommendation?.action || rec.recommended_action).includes('PROMOTE') && (
            <button className="flex-1 py-2.5 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors shadow-sm text-sm flex items-center justify-center gap-1.5">
              <Sparkles size={15}/> Approve {rec.recommendation?.discount_pct ?? rec.discount_pct}% Promo
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
