import React from 'react';
import { useAppContext } from '../context/AppContext';
import { X, Filter } from 'lucide-react';
import { DemandStatus, RecommendedAction, RiskLevel } from '../types/recommendation';

export const FilterBar: React.FC = () => {
  const { filters, updateFilter, clearFilters } = useAppContext();

  const categories = ['Snacks', 'Beverages', 'Dairy', 'Groceries', 'Personal Care', 'Household', 'Pet Care', 'Fruits & Vegetables', 'Ready to Eat', 'Bakery'];
  const demandStatuses: DemandStatus[] = ['High', 'Rising', 'Stable', 'Falling', 'Low'];
  const actions: RecommendedAction[] = ['PROMOTE', 'NO PROMOTION', 'CLEARANCE PROMOTION', 'LIMITED PROMOTION', 'HIGH PRIORITY PROMOTION'];
  const risks: RiskLevel[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

  const hasFilters = Object.values(filters).some(v => v !== undefined && v !== '');

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200 mb-6 flex flex-wrap items-center gap-3">
      <div className="flex items-center gap-2 text-sm font-medium text-slate-700 mr-2">
        <Filter size={16} /> Filters
      </div>
      
      <select 
        value={filters.category || ''} 
        onChange={e => updateFilter('category', e.target.value || undefined)}
        className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 outline-none focus:border-purple-400"
      >
        <option value="">All Categories</option>
        {categories.map(c => <option key={c} value={c}>{c}</option>)}
      </select>

      <select 
        value={filters.demand_status || ''} 
        onChange={e => updateFilter('demand_status', e.target.value || undefined)}
        className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 outline-none focus:border-purple-400"
      >
        <option value="">All Demand</option>
        {demandStatuses.map(d => <option key={d} value={d}>{d}</option>)}
      </select>

      <select 
        value={filters.recommended_action || ''} 
        onChange={e => updateFilter('recommended_action', e.target.value || undefined)}
        className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 outline-none focus:border-purple-400 max-w-[200px]"
      >
        <option value="">All Actions</option>
        {actions.map(a => <option key={a} value={a}>{a}</option>)}
      </select>

      <select 
        value={filters.risk_level || ''} 
        onChange={e => updateFilter('risk_level', e.target.value || undefined)}
        className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 outline-none focus:border-purple-400"
      >
        <option value="">All Risks</option>
        {risks.map(r => <option key={r} value={r}>{r}</option>)}
      </select>

      {hasFilters && (
        <button 
          onClick={clearFilters}
          className="ml-auto flex items-center gap-1 text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors"
        >
          <X size={14} /> Clear
        </button>
      )}
    </div>
  );
};
