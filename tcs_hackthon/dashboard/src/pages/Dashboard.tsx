import React, { useEffect, useState } from 'react';
import { getRecommendations } from '../services/api';
import { Recommendation } from '../types/recommendation';
import { KPICard } from '../components/KPICard';
import { RecommendationCard } from '../components/RecommendationCard';
import { RecommendationTable } from '../components/RecommendationTable';
import { ProductDetailsModal } from '../components/ProductDetailsModal';
import { Package, TrendingUp, AlertTriangle, AlertOctagon, Tags, Percent } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { CardSkeleton, TableSkeleton } from '../components/LoadingSkeleton';
import { ChartCard } from '../components/ChartCard';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';

export const Dashboard: React.FC = () => {
  const { filters } = useAppContext();
  const [data, setData] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      const res = await getRecommendations(filters);
      setData(res);
      setLoading(false);
    };
    fetch();
  }, [filters]);

  // Calculations
  const totalProducts = data.length;
  const productsToPromote = data.filter(r => r.recommended_action.includes('PROMOTE')).length;
  const stockoutRisk = data.filter(r => r.stockout_risk_pct > 30).length;
  const overstock = data.filter(r => r.risk_flag?.toLowerCase().includes('overstock')).length;
  const nearExpiry = data.filter(r => r.days_to_expiry < 7).length;
  const avgDiscount = data.length ? Math.round(data.reduce((acc, r) => acc + r.discount_pct, 0) / data.length) : 0;

  // Chart Data
  const invHealthData = [
    { name: 'Healthy', value: totalProducts - stockoutRisk - overstock - nearExpiry, color: '#10b981' },
    { name: 'Stockout Risk', value: stockoutRisk, color: '#f59e0b' },
    { name: 'Overstock', value: overstock, color: '#8b5cf6' },
    { name: 'Near Expiry', value: nearExpiry, color: '#ef4444' }
  ].filter(d => d.value > 0);

  const demandData = data.slice(0, 10).map((r, i) => ({
    name: `T-${10-i}`,
    signal: r.demand_trend_pct
  }));

  const topOpportunities = [...data]
    .filter(r => r.recommended_action.includes('PROMOTE'))
    .sort((a, b) => b.discount_pct - a.discount_pct)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-slate-900">Good Morning, Retailer 👋</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">DEMO MODE • MOCK DATA</span>
          </div>
          <p className="text-slate-500">AI-powered insights for your quick-commerce operations</p>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <KPICard title="Total Products" value={totalProducts} icon={<Package size={20}/>} />
          <KPICard title="To Promote" value={productsToPromote} icon={<Tags size={20}/>} trend={{value: '12%', isPositive: true}} />
          <KPICard title="Stockout Risk" value={stockoutRisk} icon={<AlertTriangle size={20}/>} trend={{value: '3%', isPositive: false}} />
          <KPICard title="Overstock" value={overstock} icon={<Package size={20}/>} />
          <KPICard title="Near Expiry" value={nearExpiry} icon={<AlertOctagon size={20}/>} />
          <KPICard title="Avg Discount" value={`${avgDiscount}%`} icon={<Percent size={20}/>} />
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">AI Promotion Opportunities</h2>
          </div>
          
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...Array(4)].map((_, i) => <CardSkeleton key={i} />)}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {topOpportunities.map(rec => (
                <RecommendationCard key={rec.product_id} recommendation={rec} onClick={() => setSelectedRec(rec)} />
              ))}
            </div>
          )}

          <div className="pt-4">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Top Recommendations List</h2>
            {loading ? <TableSkeleton /> : <RecommendationTable data={data.slice(0, 5)} onRowClick={setSelectedRec} />}
          </div>
        </div>

        <div className="space-y-6">
          <ChartCard title="Inventory Health">
            <div className="h-[250px]">
              {loading ? <div className="w-full h-full animate-pulse bg-slate-100 rounded-lg"></div> : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={invHealthData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {invHealthData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="flex flex-wrap gap-4 justify-center mt-4">
              {invHealthData.map(d => (
                <div key={d.name} className="flex items-center gap-1.5 text-xs text-slate-600">
                  <div className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: d.color}}></div>
                  {d.name} ({d.value})
                </div>
              ))}
            </div>
          </ChartCard>

          <ChartCard title="Current Recommendation Demand Signals">
            <div className="h-[200px]">
              {loading ? <div className="w-full h-full animate-pulse bg-slate-100 rounded-lg"></div> : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={demandData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                    <Tooltip />
                    <Line type="monotone" dataKey="signal" stroke="#8b5cf6" strokeWidth={2} dot={{r: 4}} activeDot={{r: 6}} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>
      </div>

      <ProductDetailsModal isOpen={!!selectedRec} onClose={() => setSelectedRec(null)} rec={selectedRec} />
    </div>
  );
};
