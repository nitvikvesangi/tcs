import React, { useEffect, useState } from 'react';
import { getRecommendations } from '../services/api';
import { Recommendation, InventoryStatus } from '../types/recommendation';
import { useAppContext } from '../context/AppContext';
import { KPICard } from '../components/KPICard';
import { InventoryStatusBadge } from '../components/InventoryStatusBadge';
import { TableSkeleton, CardSkeleton } from '../components/LoadingSkeleton';
import { Package, AlertTriangle, AlertOctagon, TrendingDown, Layers } from 'lucide-react';
import { EmptyState } from '../components/EmptyState';
import { cn } from '../components/ActionBadge';

export const Inventory: React.FC = () => {
  const { filters } = useAppContext();
  const [data, setData] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      const res = await getRecommendations(filters);
      setData(res);
      setLoading(false);
    };
    fetch();
  }, [filters]);

  const getStatus = (rec: Recommendation): InventoryStatus => {
    if (rec.stockout_risk_pct > 60) return 'STOCKOUT RISK';
    if (rec.days_to_expiry < 7) return 'NEAR EXPIRY';
    if (rec.current_stock > 300) return 'OVERSTOCKED'; // arbitrary mock threshold
    if (rec.current_stock < 20) return 'LOW STOCK';
    return 'HEALTHY';
  };

  const enhancedData = data.map(rec => ({ ...rec, status: getStatus(rec) }));

  const kpis = {
    total: enhancedData.length,
    lowStock: enhancedData.filter(d => d.status === 'LOW STOCK').length,
    stockoutRisk: enhancedData.filter(d => d.status === 'STOCKOUT RISK').length,
    overstock: enhancedData.filter(d => d.status === 'OVERSTOCKED').length,
    nearExpiry: enhancedData.filter(d => d.status === 'NEAR EXPIRY').length,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Inventory Intelligence</h1>
        <p className="text-slate-500 mt-1">Monitor hyperlocal inventory health across dark stores.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <KPICard title="Total Products" value={kpis.total} icon={<Package size={20}/>} />
          <KPICard title="Low Stock" value={kpis.lowStock} icon={<TrendingDown size={20}/>} className="border-yellow-200 bg-yellow-50/30" />
          <KPICard title="Stockout Risk" value={kpis.stockoutRisk} icon={<AlertTriangle size={20}/>} className="border-red-200 bg-red-50/30" />
          <KPICard title="Overstock" value={kpis.overstock} icon={<Layers size={20}/>} className="border-purple-200 bg-purple-50/30" />
          <KPICard title="Near Expiry" value={kpis.nearExpiry} icon={<AlertOctagon size={20}/>} className="border-orange-200 bg-orange-50/30" />
        </div>
      )}

      {loading ? (
        <TableSkeleton />
      ) : enhancedData.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[900px]">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                <th className="px-6 py-4 font-medium">Product</th>
                <th className="px-6 py-4 font-medium">Store</th>
                <th className="px-6 py-4 font-medium">Stock Level</th>
                <th className="px-6 py-4 font-medium">Expiry</th>
                <th className="px-6 py-4 font-medium">Demand</th>
                <th className="px-6 py-4 font-medium">Risk</th>
                <th className="px-6 py-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {enhancedData.map((rec) => (
                <tr key={rec.product_id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-900">{rec.product_name}</div>
                    <div className="text-xs text-slate-500">{rec.category}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">{rec.dark_store_id}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className={cn("h-full rounded-full", rec.current_stock > 100 ? "bg-emerald-500" : rec.current_stock > 20 ? "bg-yellow-500" : "bg-red-500")}
                          style={{ width: `${Math.min(100, (rec.current_stock / 500) * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-slate-700">{rec.current_stock}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">{rec.days_to_expiry} days</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{rec.demand_status}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{rec.stockout_risk_pct}%</td>
                  <td className="px-6 py-4">
                    <InventoryStatusBadge status={rec.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
