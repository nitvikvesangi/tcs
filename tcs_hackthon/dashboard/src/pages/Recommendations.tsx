import React, { useEffect, useState } from 'react';
import { getRecommendations } from '../services/api';
import { Recommendation } from '../types/recommendation';
import { FilterBar } from '../components/FilterBar';
import { RecommendationTable } from '../components/RecommendationTable';
import { ProductDetailsModal } from '../components/ProductDetailsModal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { useAppContext } from '../context/AppContext';
import { EmptyState } from '../components/EmptyState';

export const Recommendations: React.FC = () => {
  const { filters, clearFilters } = useAppContext();
  const [data, setData] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);
  const [error, setError] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(false);
      const res = await getRecommendations(filters);
      setData(res);
    } catch (e) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">AI Recommendations</h1>
        <p className="text-slate-500 mt-1">AI-generated promotion decisions based on inventory, demand and market signals.</p>
      </div>

      <FilterBar />

      {error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl text-center">
          <p className="mb-4">Unable to load recommendations.</p>
          <button onClick={fetchData} className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">Retry</button>
        </div>
      ) : loading ? (
        <TableSkeleton />
      ) : data.length === 0 ? (
        <EmptyState actionLabel="Clear Filters" onAction={clearFilters} />
      ) : (
        <RecommendationTable data={data} onRowClick={setSelectedRec} />
      )}

      <ProductDetailsModal isOpen={!!selectedRec} onClose={() => setSelectedRec(null)} rec={selectedRec} />
    </div>
  );
};
