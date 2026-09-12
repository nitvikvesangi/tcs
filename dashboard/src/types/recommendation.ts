export type DemandStatus = 'High' | 'Rising' | 'Stable' | 'Falling' | 'Low';
export type RecommendedAction = 'PROMOTE' | 'NO PROMOTION' | 'CLEARANCE PROMOTION' | 'LIMITED PROMOTION' | 'HIGH PRIORITY PROMOTION';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type InventoryStatus = 'HEALTHY' | 'LOW STOCK' | 'STOCKOUT RISK' | 'OVERSTOCKED' | 'NEAR EXPIRY';
export type UrgencyLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface RecommendationOption {
  discount_pct: number;
  expected_sales_units: number;
  expected_revenue: number;
  expected_profit: number;
  profit_impact_pct: number;
  inventory_reduction_pct: number;
  stockout_risk_pct: number;
  expiry_waste_reduction_pct: number;
  score: number;
}

export interface InventorySnapshot {
  stockout_urgency: UrgencyLevel | string;
  overstock_urgency: UrgencyLevel | string;
  expiry_urgency: UrgencyLevel | string;
  inventory_alert_score: number; // 0 - 100
}

export interface RecommendationDecision {
  action: RecommendedAction;
  discount_pct: number;
  objective: string;
}

export interface Recommendation {
  product_id: string;
  dark_store_id: string;
  
  // Recommendation details
  recommendation: RecommendationDecision;
  reasons: string[];
  risk_flag: string;
  options: RecommendationOption[];
  inventory_snapshot: InventorySnapshot;

  // Hyperlocal Product & Inventory Context
  product_name: string;
  category: string;
  city: string;
  current_stock: number;
  days_to_expiry: number;
  demand_status: DemandStatus;
  demand_trend_pct: number;
  trend_signal?: string;
  weather_condition?: string;
  time_of_day?: string;
  is_weekend?: boolean;
  gross_margin_before_promo?: number;
  competitor_price_gap_pct?: number;
  stockout_risk_pct: number;

  // Flattened aliases for fast access
  recommended_action: RecommendedAction;
  discount_pct: number;
  explanation: string;
}

export interface RecommendationFilters {
  city?: string;
  dark_store_id?: string;
  category?: string;
  demand_status?: DemandStatus;
  recommended_action?: RecommendedAction;
  risk_level?: RiskLevel;
  search_query?: string;
}
