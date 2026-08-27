import { Recommendation, RecommendationFilters } from '../types/recommendation';

const API_BASE_URL = '';

export const getRecommendations = async (filters?: RecommendationFilters): Promise<Recommendation[]> => {
  try {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.city) params.append('city', filters.city);
      if (filters.dark_store_id) params.append('dark_store_id', filters.dark_store_id);
      if (filters.category) params.append('category', filters.category);
      if (filters.demand_status) params.append('demand_status', filters.demand_status);
      if (filters.search_query) params.append('search_query', filters.search_query);
    }
    
    const url = `${API_BASE_URL}/recommendations${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Client-side filtering for fields the backend doesn't support filtering on yet (like risk_level)
    let results = data;
    if (filters?.risk_level) {
      results = results.filter((r: Recommendation) => {
        const risk = r.stockout_risk_pct;
        if (filters.risk_level === 'LOW') return risk <= 10;
        if (filters.risk_level === 'MEDIUM') return risk > 10 && risk <= 30;
        if (filters.risk_level === 'HIGH') return risk > 30 && risk <= 60;
        if (filters.risk_level === 'CRITICAL') return risk > 60;
        return true;
      });
    }
    
    return results;
  } catch (error) {
    console.error("Failed to fetch recommendations from backend:", error);
    // Fallback to empty array if backend is down to avoid React crashing
    return [];
  }
};
