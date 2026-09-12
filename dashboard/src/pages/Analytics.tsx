import React, { useEffect, useState } from 'react';
import { getRecommendations } from '../services/api';
import { Recommendation } from '../types/recommendation';
import { useAppContext } from '../context/AppContext';
import { ChartCard } from '../components/ChartCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TableSkeleton } from '../components/LoadingSkeleton';

export const Analytics: React.FC = () => {
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

  // Data aggregations
  const demandDist = data.reduce((acc, curr) => {
    acc[curr.demand_status] = (acc[curr.demand_status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const demandData = Object.entries(demandDist).map(([name, value]) => ({ name, value }));

  const actionDist = data.reduce((acc, curr) => {
    acc[curr.recommended_action] = (acc[curr.recommended_action] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const actionData = Object.entries(actionDist).map(([name, value]) => ({ name, value }));

  const discountDist = data.reduce((acc, curr) => {
    const key = `${curr.discount_pct}%`;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const discountData = Object.entries(discountDist).map(([name, value]) => ({ name, value }));

  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">DEMO ANALYTICS</span>
        </div>
        <p className="text-slate-500 mt-1">Understand demand, inventory and AI promotion signals based on current data.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => <TableSkeleton key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <ChartCard title="Demand Signal Distribution">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={demandData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={12} />
                  <YAxis axisLine={false} tickLine={false} fontSize={12} />
                  <RechartsTooltip cursor={{fill: '#f8fafc'}} />
                  <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Promotion Action Distribution">
            <div className="h-64 flex">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={actionData} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value" label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {actionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Discount Distribution">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={discountData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={12} />
                  <YAxis axisLine={false} tickLine={false} fontSize={12} />
                  <RechartsTooltip cursor={{fill: '#f8fafc'}} />
                  <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Stockout Risk by Store">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={data.reduce((acc, curr) => {
                    const store = acc.find(a => a.name === curr.dark_store_id);
                    if (store) {
                      store.riskSum += curr.stockout_risk_pct;
                      store.count += 1;
                    } else {
                      acc.push({ name: curr.dark_store_id, riskSum: curr.stockout_risk_pct, count: 1 });
                    }
                    return acc;
                  }, [] as any[]).map(s => ({ name: s.name, value: Math.round(s.riskSum / s.count) }))} 
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                  <XAxis type="number" axisLine={false} tickLine={false} fontSize={12} />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} fontSize={12} width={80} />
                  <RechartsTooltip cursor={{fill: '#f8fafc'}} />
                  <Bar dataKey="value" fill="#f59e0b" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

        </div>
      )}
    </div>
  );
};
