import { Recommendation } from '../types/recommendation';

export const mockRecommendations: Recommendation[] = [
  {
    product_id: 'P0165',
    product_name: 'Pet Food Large',
    category: 'Pet Care',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS2',
    current_stock: 8,
    days_to_expiry: 98,
    demand_status: 'Stable',
    demand_trend_pct: -1.89,
    trend_signal: 'Normal',
    weather_condition: 'Clear/Cloudy',
    time_of_day: 'Morning',
    is_weekend: false,
    gross_margin_before_promo: 11.21,
    competitor_price_gap_pct: 8.99,
    stockout_risk_pct: 6.5,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Protect low-stock inventory and preserve margin baseline'
    },
    reasons: [
      'Inventory count (8 units) is insufficient to absorb promotional velocity.',
      'Gross margin before promo is already narrow at 11.21%.',
      'Stable organic demand ensures natural depletion without price discounting.'
    ],
    risk_flag: 'Low Stock Buffer',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 6,
        expected_revenue: 3594,
        expected_profit: 403,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 75.0,
        stockout_risk_pct: 6.5,
        expiry_waste_reduction_pct: 0.0,
        score: 92.4
      },
      {
        discount_pct: 10,
        expected_sales_units: 8,
        expected_revenue: 4312,
        expected_profit: 52,
        profit_impact_pct: -87.1,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 95.0,
        expiry_waste_reduction_pct: 0.0,
        score: 41.2
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'MEDIUM',
      overstock_urgency: 'LOW',
      expiry_urgency: 'LOW',
      inventory_alert_score: 28
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Inventory availability and local demand indicate a suitable hold. Low inventory buffer prevents promotional discounting.'
  },
  {
    product_id: 'P0201',
    product_name: 'Organic Milk 1L',
    category: 'Dairy',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS1',
    current_stock: 45,
    days_to_expiry: 2,
    demand_status: 'Falling',
    demand_trend_pct: -5.4,
    trend_signal: 'Downtrend',
    weather_condition: 'Rainy',
    time_of_day: 'Evening',
    is_weekend: true,
    gross_margin_before_promo: 15.0,
    competitor_price_gap_pct: 2.1,
    stockout_risk_pct: 2.0,
    recommendation: {
      action: 'CLEARANCE PROMOTION',
      discount_pct: 25,
      objective: 'Maximize salvage recovery before 48-hour spoilage window'
    },
    reasons: [
      'Product expires within 2 days with 45 units remaining in BLR-DS1.',
      'Organic milk category experiences 94% dump risk post-expiry.',
      '25% discount drives 3.8x velocity to exhaust batch before 24h cutoff.'
    ],
    risk_flag: 'Near Expiry',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 12,
        expected_revenue: 960,
        expected_profit: -1650,
        profit_impact_pct: -150.0,
        inventory_reduction_pct: 26.7,
        stockout_risk_pct: 0.5,
        expiry_waste_reduction_pct: 20.0,
        score: 18.5
      },
      {
        discount_pct: 15,
        expected_sales_units: 28,
        expected_revenue: 1904,
        expected_profit: -420,
        profit_impact_pct: -35.0,
        inventory_reduction_pct: 62.2,
        stockout_risk_pct: 1.0,
        expiry_waste_reduction_pct: 65.0,
        score: 68.0
      },
      {
        discount_pct: 25,
        expected_sales_units: 44,
        expected_revenue: 2640,
        expected_profit: 132,
        profit_impact_pct: 8.5,
        inventory_reduction_pct: 97.8,
        stockout_risk_pct: 2.0,
        expiry_waste_reduction_pct: 98.0,
        score: 95.8
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'HIGH',
      expiry_urgency: 'CRITICAL',
      inventory_alert_score: 96
    },
    recommended_action: 'CLEARANCE PROMOTION',
    discount_pct: 25,
    explanation: 'Product is nearing expiry in 2 days. High clearance discount recommended to liquidate stock before spoilage.'
  },
  {
    product_id: 'P0342',
    product_name: 'Spicy Potato Chips',
    category: 'Snacks',
    city: 'Mumbai',
    dark_store_id: 'MUM-DS1',
    current_stock: 12,
    days_to_expiry: 180,
    demand_status: 'High',
    demand_trend_pct: 12.5,
    trend_signal: 'Surge',
    weather_condition: 'Clear',
    time_of_day: 'Evening',
    is_weekend: true,
    gross_margin_before_promo: 35.5,
    competitor_price_gap_pct: -5.0,
    stockout_risk_pct: 85.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Prevent immediate stockout during peak weekend evening surge'
    },
    reasons: [
      'High stockout risk (85%) with only 12 units available in dark store.',
      'Evening weekend surge is accelerating depletion at 4.2 units/hr.',
      'Promotion would exhaust SKU within 90 minutes causing unmet basket churn.'
    ],
    risk_flag: 'Critical Stockout Risk',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 12,
        expected_revenue: 600,
        expected_profit: 213,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 85.0,
        expiry_waste_reduction_pct: 0.0,
        score: 89.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 12,
        expected_revenue: 540,
        expected_profit: 153,
        profit_impact_pct: -28.2,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 98.0,
        expiry_waste_reduction_pct: 0.0,
        score: 32.0
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'CRITICAL',
      overstock_urgency: 'LOW',
      expiry_urgency: 'LOW',
      inventory_alert_score: 91
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Extremely high demand and low stock. Promotion would exacerbate stockout risk. Restock immediately.'
  },
  {
    product_id: 'P0871',
    product_name: 'Cold Coffee 250ml',
    category: 'Beverages',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS1',
    current_stock: 350,
    days_to_expiry: 45,
    demand_status: 'Rising',
    demand_trend_pct: 8.2,
    trend_signal: 'Uptrend',
    weather_condition: 'Hot',
    time_of_day: 'Afternoon',
    is_weekend: false,
    gross_margin_before_promo: 40.0,
    competitor_price_gap_pct: 1.5,
    stockout_risk_pct: 12.0,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 10,
      objective: 'Capitalize on hot afternoon weather trend to maximize revenue velocity'
    },
    reasons: [
      'Healthy inventory (350 units) supports 2.5x volume expansion.',
      'Afternoon beverage demand surge triggered by +3°C local weather index.',
      '40% gross margin provides strong profit headroom for 10% discount.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 65,
        expected_revenue: 3900,
        expected_profit: 1560,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 18.6,
        stockout_risk_pct: 4.0,
        expiry_waste_reduction_pct: 10.0,
        score: 74.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 145,
        expected_revenue: 7830,
        expected_profit: 2610,
        profit_impact_pct: +67.3,
        inventory_reduction_pct: 41.4,
        stockout_risk_pct: 12.0,
        expiry_waste_reduction_pct: 40.0,
        score: 96.5
      },
      {
        discount_pct: 20,
        expected_sales_units: 210,
        expected_revenue: 10080,
        expected_profit: 2016,
        profit_impact_pct: +29.2,
        inventory_reduction_pct: 60.0,
        stockout_risk_pct: 35.0,
        expiry_waste_reduction_pct: 60.0,
        score: 81.2
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'LOW',
      inventory_alert_score: 34
    },
    recommended_action: 'PROMOTE',
    discount_pct: 10,
    explanation: 'High local demand combined with healthy inventory makes this a strong promotion opportunity to capture market share.'
  },
  {
    product_id: 'P0992',
    product_name: 'Whole Wheat Bread',
    category: 'Bakery',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS2',
    current_stock: 80,
    days_to_expiry: 4,
    demand_status: 'Stable',
    demand_trend_pct: 1.2,
    trend_signal: 'Normal',
    weather_condition: 'Cloudy',
    time_of_day: 'Morning',
    is_weekend: false,
    gross_margin_before_promo: 20.0,
    competitor_price_gap_pct: 0.5,
    stockout_risk_pct: 15.0,
    recommendation: {
      action: 'LIMITED PROMOTION',
      discount_pct: 10,
      objective: 'Accelerate sell-through ahead of short 4-day shelf life'
    },
    reasons: [
      'Shelf life countdown: 80 units with 4 days until expiration.',
      'Morning breakfast peak offers optimal conversion window.',
      '10% discount stimulates multi-pack add-ons without margin collapse.'
    ],
    risk_flag: 'Approaching Expiry',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 35,
        expected_revenue: 1400,
        expected_profit: 280,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 43.8,
        stockout_risk_pct: 5.0,
        expiry_waste_reduction_pct: 30.0,
        score: 65.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 68,
        expected_revenue: 2448,
        expected_profit: 340,
        profit_impact_pct: +21.4,
        inventory_reduction_pct: 85.0,
        stockout_risk_pct: 15.0,
        expiry_waste_reduction_pct: 88.0,
        score: 93.1
      },
      {
        discount_pct: 20,
        expected_sales_units: 80,
        expected_revenue: 2560,
        expected_profit: 0,
        profit_impact_pct: -100.0,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 45.0,
        expiry_waste_reduction_pct: 100.0,
        score: 52.4
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'HIGH',
      inventory_alert_score: 71
    },
    recommended_action: 'LIMITED PROMOTION',
    discount_pct: 10,
    explanation: 'Approaching expiry window. A limited promotion will ensure sell-through without sacrificing too much margin.'
  },
  {
    product_id: 'P1120',
    product_name: 'Instant Noodles Pack',
    category: 'Ready to Eat',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS3',
    current_stock: 450,
    days_to_expiry: 240,
    demand_status: 'Stable',
    demand_trend_pct: 0.5,
    trend_signal: 'Normal',
    weather_condition: 'Rainy',
    time_of_day: 'Night',
    is_weekend: true,
    gross_margin_before_promo: 18.0,
    competitor_price_gap_pct: -2.0,
    stockout_risk_pct: 5.0,
    recommendation: {
      action: 'HIGH PRIORITY PROMOTION',
      discount_pct: 15,
      objective: 'Clear excessive warehouse space and unlock tied working capital'
    },
    reasons: [
      'Severe inventory overhang (450 units) consuming 18% of dry aisle capacity.',
      'Rainy night pattern correlates with 45% lift in comfort food attach rate.',
      '15% promotional pricing generates volume lift of +110%.'
    ],
    risk_flag: 'Severe Overstock',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 40,
        expected_revenue: 1600,
        expected_profit: 288,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 8.9,
        stockout_risk_pct: 1.0,
        expiry_waste_reduction_pct: 5.0,
        score: 55.0
      },
      {
        discount_pct: 15,
        expected_sales_units: 195,
        expected_revenue: 6630,
        expected_profit: 741,
        profit_impact_pct: +157.3,
        inventory_reduction_pct: 43.3,
        stockout_risk_pct: 5.0,
        expiry_waste_reduction_pct: 25.0,
        score: 97.2
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'CRITICAL',
      expiry_urgency: 'LOW',
      inventory_alert_score: 84
    },
    recommended_action: 'HIGH PRIORITY PROMOTION',
    discount_pct: 15,
    explanation: 'Significant overstock situation. High priority promotion recommended to free up warehouse space and improve capital turnover.'
  },
  {
    product_id: 'P0455',
    product_name: 'Fresh Apples 1kg',
    category: 'Fruits & Vegetables',
    city: 'Mumbai',
    dark_store_id: 'MUM-DS1',
    current_stock: 25,
    days_to_expiry: 5,
    demand_status: 'Rising',
    demand_trend_pct: 6.7,
    trend_signal: 'Uptrend',
    weather_condition: 'Clear',
    time_of_day: 'Morning',
    is_weekend: true,
    gross_margin_before_promo: 22.5,
    competitor_price_gap_pct: 4.0,
    stockout_risk_pct: 45.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Allow organic morning demand to deplete batch at full price'
    },
    reasons: [
      'Demand velocity (+6.7%) is already high without promotional incentives.',
      'Inventory (25 units) will deplete within 14 hours at current run-rate.',
      'Zero discount preserves full 22.5% unit gross profit.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 24,
        expected_revenue: 3600,
        expected_profit: 810,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 96.0,
        stockout_risk_pct: 45.0,
        expiry_waste_reduction_pct: 95.0,
        score: 91.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 25,
        expected_revenue: 3375,
        expected_profit: 487,
        profit_impact_pct: -39.8,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 78.0,
        expiry_waste_reduction_pct: 100.0,
        score: 48.0
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'HIGH',
      overstock_urgency: 'LOW',
      expiry_urgency: 'MEDIUM',
      inventory_alert_score: 52
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Demand is naturally rising. Stock is sufficient but will deplete naturally. Margin preservation is optimal.'
  },
  {
    product_id: 'P0566',
    product_name: 'Floor Cleaner 1L',
    category: 'Household',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS1',
    current_stock: 120,
    days_to_expiry: 720,
    demand_status: 'Low',
    demand_trend_pct: -2.5,
    trend_signal: 'Downtrend',
    weather_condition: 'Clear',
    time_of_day: 'Afternoon',
    is_weekend: false,
    gross_margin_before_promo: 28.0,
    competitor_price_gap_pct: 10.5,
    stockout_risk_pct: 1.0,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 15,
      objective: 'Neutralize 10.5% competitor price premium and stimulate sales'
    },
    reasons: [
      'Competitor is pricing similar SKU 10.5% lower, causing demand migration.',
      'Ample stock (120 units) and long 2-year shelf life provide stability.',
      '15% discount matches competitor parity + gives instant cart incentive.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 14,
        expected_revenue: 2100,
        expected_profit: 588,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 11.7,
        stockout_risk_pct: 0.5,
        expiry_waste_reduction_pct: 0.0,
        score: 58.2
      },
      {
        discount_pct: 15,
        expected_sales_units: 52,
        expected_revenue: 6630,
        expected_profit: 962,
        profit_impact_pct: +63.6,
        inventory_reduction_pct: 43.3,
        stockout_risk_pct: 1.0,
        expiry_waste_reduction_pct: 0.0,
        score: 94.7
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'LOW',
      inventory_alert_score: 35
    },
    recommended_action: 'PROMOTE',
    discount_pct: 15,
    explanation: 'Competitor price gap is high causing low demand. A 15% discount will bridge the gap and move stagnant inventory.'
  },
  {
    product_id: 'P0788',
    product_name: 'Greek Yogurt Vanilla',
    category: 'Dairy',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS2',
    current_stock: 15,
    days_to_expiry: 3,
    demand_status: 'High',
    demand_trend_pct: 9.0,
    trend_signal: 'Surge',
    weather_condition: 'Hot',
    time_of_day: 'Morning',
    is_weekend: true,
    gross_margin_before_promo: 30.0,
    competitor_price_gap_pct: -1.5,
    stockout_risk_pct: 65.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Prevent critical stockout during morning breakfast rush'
    },
    reasons: [
      'High demand velocity combined with low stock (15 units).',
      'Stockout probability reaches 65% by noon without replenishments.',
      'Pricing discount would immediately wipe out remaining inventory.'
    ],
    risk_flag: 'Critical Stockout Risk',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 15,
        expected_revenue: 1200,
        expected_profit: 360,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 65.0,
        expiry_waste_reduction_pct: 90.0,
        score: 87.0
      },
      {
        discount_pct: 15,
        expected_sales_units: 15,
        expected_revenue: 1020,
        expected_profit: 180,
        profit_impact_pct: -50.0,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 95.0,
        expiry_waste_reduction_pct: 100.0,
        score: 36.5
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'CRITICAL',
      overstock_urgency: 'LOW',
      expiry_urgency: 'HIGH',
      inventory_alert_score: 88
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Critical stockout risk with high demand. Do not promote. Focus on replenishment.'
  },
  {
    product_id: 'P0899',
    product_name: 'Premium Basmati Rice 5kg',
    category: 'Groceries',
    city: 'Mumbai',
    dark_store_id: 'MUM-DS1',
    current_stock: 210,
    days_to_expiry: 365,
    demand_status: 'Stable',
    demand_trend_pct: 1.1,
    trend_signal: 'Normal',
    weather_condition: 'Clear',
    time_of_day: 'Evening',
    is_weekend: true,
    gross_margin_before_promo: 15.0,
    competitor_price_gap_pct: 5.0,
    stockout_risk_pct: 2.5,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 5,
      objective: 'Increase weekend household basket sizes with minimal margin dilution'
    },
    reasons: [
      'Stable staple demand with strong 210-unit stock holding.',
      'Mild 5% discount triggers basket threshold rewards.',
      'Expected net revenue expands by +32%.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 25,
        expected_revenue: 12500,
        expected_profit: 1875,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 11.9,
        stockout_risk_pct: 1.0,
        expiry_waste_reduction_pct: 0.0,
        score: 72.0
      },
      {
        discount_pct: 5,
        expected_sales_units: 42,
        expected_revenue: 19950,
        expected_profit: 2095,
        profit_impact_pct: +11.7,
        inventory_reduction_pct: 20.0,
        stockout_risk_pct: 2.5,
        expiry_waste_reduction_pct: 0.0,
        score: 93.4
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'LOW',
      inventory_alert_score: 30
    },
    recommended_action: 'PROMOTE',
    discount_pct: 5,
    explanation: 'Healthy inventory levels. A small promotional push will increase volume without heavily impacting absolute margin.'
  },
  {
    product_id: 'P1002',
    product_name: 'Shampoo Anti-Dandruff 200ml',
    category: 'Personal Care',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS1',
    current_stock: 85,
    days_to_expiry: 500,
    demand_status: 'Falling',
    demand_trend_pct: -4.5,
    trend_signal: 'Downtrend',
    weather_condition: 'Humid',
    time_of_day: 'Evening',
    is_weekend: false,
    gross_margin_before_promo: 45.0,
    competitor_price_gap_pct: 12.0,
    stockout_risk_pct: 4.0,
    recommendation: {
      action: 'LIMITED PROMOTION',
      discount_pct: 20,
      objective: 'Regain lost category share caused by 12% competitor price gap'
    },
    reasons: [
      'Demand declining by 4.5% due to competitor aggressive bundle promotions.',
      'High gross margin (45%) absorbs 20% promotional discount easily.',
      'Limited duration creates purchasing urgency among repeat buyers.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 8,
        expected_revenue: 1600,
        expected_profit: 720,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 9.4,
        stockout_risk_pct: 1.0,
        expiry_waste_reduction_pct: 0.0,
        score: 51.0
      },
      {
        discount_pct: 20,
        expected_sales_units: 36,
        expected_revenue: 5760,
        expected_profit: 1800,
        profit_impact_pct: +150.0,
        inventory_reduction_pct: 42.4,
        stockout_risk_pct: 4.0,
        expiry_waste_reduction_pct: 0.0,
        score: 95.0
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'LOW',
      inventory_alert_score: 42
    },
    recommended_action: 'LIMITED PROMOTION',
    discount_pct: 20,
    explanation: 'High margin item with falling demand and significant price gap. Aggressive limited promotion to regain traction.'
  },
  {
    product_id: 'P1113',
    product_name: 'Sparkling Water 500ml',
    category: 'Beverages',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS2',
    current_stock: 320,
    days_to_expiry: 120,
    demand_status: 'Rising',
    demand_trend_pct: 15.2,
    trend_signal: 'Surge',
    weather_condition: 'Hot',
    time_of_day: 'Afternoon',
    is_weekend: true,
    gross_margin_before_promo: 55.0,
    competitor_price_gap_pct: 0.0,
    stockout_risk_pct: 22.0,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 10,
      objective: 'Drive bulk pack attachments during weekend afternoon heat index'
    },
    reasons: [
      'Exceptional margin headroom (55%) allows risk-free pricing experimentation.',
      'Trending +15.2% demand velocity during high afternoon temperatures.',
      'Inventory buffer (320 units) easily supports 2.2x sales uplift.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 45,
        expected_revenue: 2250,
        expected_profit: 1238,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 14.1,
        stockout_risk_pct: 5.0,
        expiry_waste_reduction_pct: 10.0,
        score: 72.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 110,
        expected_revenue: 4950,
        expected_profit: 2475,
        profit_impact_pct: +99.9,
        inventory_reduction_pct: 34.4,
        stockout_risk_pct: 22.0,
        expiry_waste_reduction_pct: 35.0,
        score: 96.8
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'HIGH',
      expiry_urgency: 'LOW',
      inventory_alert_score: 45
    },
    recommended_action: 'PROMOTE',
    discount_pct: 10,
    explanation: 'Capitalize on trending demand and hot weather. High margin allows for a 10% discount to drive bulk purchases.'
  },
  {
    product_id: 'P1224',
    product_name: 'Chocolate Chip Cookies',
    category: 'Snacks',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS3',
    current_stock: 45,
    days_to_expiry: 60,
    demand_status: 'Stable',
    demand_trend_pct: 0.2,
    trend_signal: 'Normal',
    weather_condition: 'Rainy',
    time_of_day: 'Night',
    is_weekend: true,
    gross_margin_before_promo: 32.0,
    competitor_price_gap_pct: 3.5,
    stockout_risk_pct: 18.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Maintain balanced equilibrium without unnecessary price erosion'
    },
    reasons: [
      'Equilibrium stock-to-demand ratio of 4.5 days.',
      'Competitor pricing is within acceptable 3.5% corridor.',
      'Current sales rate depletes batch comfortably within 60-day expiry.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 18,
        expected_revenue: 900,
        expected_profit: 288,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 40.0,
        stockout_risk_pct: 18.0,
        expiry_waste_reduction_pct: 20.0,
        score: 88.0
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'LOW',
      expiry_urgency: 'LOW',
      inventory_alert_score: 18
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Inventory matches expected demand pattern. No intervention needed.'
  },
  {
    product_id: 'P1335',
    product_name: 'Cat Litter 5kg',
    category: 'Pet Care',
    city: 'Mumbai',
    dark_store_id: 'MUM-DS1',
    current_stock: 18,
    days_to_expiry: 1000,
    demand_status: 'High',
    demand_trend_pct: 5.5,
    trend_signal: 'Uptrend',
    weather_condition: 'Clear',
    time_of_day: 'Morning',
    is_weekend: false,
    gross_margin_before_promo: 25.0,
    competitor_price_gap_pct: -2.0,
    stockout_risk_pct: 55.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Conserve stock for core recurring pet owners'
    },
    reasons: [
      'High repeat purchase rate category with low inventory (18 units).',
      'Stockout risk is elevated at 55%.',
      'Preserving availability for scheduled recurring carts protects user retention.'
    ],
    risk_flag: 'High Stockout Risk',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 12,
        expected_revenue: 3600,
        expected_profit: 900,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 66.7,
        stockout_risk_pct: 55.0,
        expiry_waste_reduction_pct: 0.0,
        score: 86.4
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'HIGH',
      overstock_urgency: 'LOW',
      expiry_urgency: 'LOW',
      inventory_alert_score: 62
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'High stockout risk. Promotion will lead to unmet demand and poor customer experience.'
  },
  {
    product_id: 'P1446',
    product_name: 'Almond Milk Unsweetened 1L',
    category: 'Dairy',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS1',
    current_stock: 65,
    days_to_expiry: 14,
    demand_status: 'Stable',
    demand_trend_pct: 1.8,
    trend_signal: 'Normal',
    weather_condition: 'Clear',
    time_of_day: 'Morning',
    is_weekend: true,
    gross_margin_before_promo: 28.0,
    competitor_price_gap_pct: 6.0,
    stockout_risk_pct: 10.0,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 10,
      objective: 'Stimulate weekend specialty dairy conversions'
    },
    reasons: [
      '14-day expiry window warrants healthy turn acceleration.',
      'Competitor is pricing 6% lower; 10% discount captures price advantage.',
      '28% gross margin retains profitable unit unit economics.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 20,
        expected_revenue: 4000,
        expected_profit: 1120,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 30.8,
        stockout_risk_pct: 3.0,
        expiry_waste_reduction_pct: 20.0,
        score: 68.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 45,
        expected_revenue: 8100,
        expected_profit: 1710,
        profit_impact_pct: +52.7,
        inventory_reduction_pct: 69.2,
        stockout_risk_pct: 10.0,
        expiry_waste_reduction_pct: 80.0,
        score: 94.2
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'MEDIUM',
      inventory_alert_score: 48
    },
    recommended_action: 'PROMOTE',
    discount_pct: 10,
    explanation: 'Moderate inventory with slightly high price gap. 10% discount aligns price and drives volume.'
  },
  {
    product_id: 'P1557',
    product_name: 'Washing Machine Liquid 2L',
    category: 'Household',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS2',
    current_stock: 180,
    days_to_expiry: 600,
    demand_status: 'Low',
    demand_trend_pct: -3.2,
    trend_signal: 'Downtrend',
    weather_condition: 'Cloudy',
    time_of_day: 'Afternoon',
    is_weekend: false,
    gross_margin_before_promo: 22.0,
    competitor_price_gap_pct: 8.5,
    stockout_risk_pct: 2.0,
    recommendation: {
      action: 'HIGH PRIORITY PROMOTION',
      discount_pct: 20,
      objective: 'Liquidate bulky heavy stock to recover high-cost floor pallet space'
    },
    reasons: [
      'Heavy bulky product (180 units) blocks 3 full pallet positions.',
      'Sluggish demand trend (-3.2%) ties up capital and dark store bin capacity.',
      '20% discount is projected to double weekly run-rate.'
    ],
    risk_flag: 'Overstock',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 15,
        expected_revenue: 5250,
        expected_profit: 1155,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 8.3,
        stockout_risk_pct: 0.5,
        expiry_waste_reduction_pct: 0.0,
        score: 45.0
      },
      {
        discount_pct: 20,
        expected_sales_units: 75,
        expected_revenue: 21000,
        expected_profit: 2520,
        profit_impact_pct: +118.2,
        inventory_reduction_pct: 41.7,
        stockout_risk_pct: 2.0,
        expiry_waste_reduction_pct: 0.0,
        score: 96.1
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'CRITICAL',
      expiry_urgency: 'LOW',
      inventory_alert_score: 79
    },
    recommended_action: 'HIGH PRIORITY PROMOTION',
    discount_pct: 20,
    explanation: 'Slow moving heavy item taking up valuable dark store space. Aggressive promotion needed to clear space.'
  },
  {
    product_id: 'P1668',
    product_name: 'Fresh Spinach 250g',
    category: 'Fruits & Vegetables',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS2',
    current_stock: 12,
    days_to_expiry: 1,
    demand_status: 'Low',
    demand_trend_pct: -8.0,
    trend_signal: 'Downtrend',
    weather_condition: 'Rainy',
    time_of_day: 'Evening',
    is_weekend: false,
    gross_margin_before_promo: 40.0,
    competitor_price_gap_pct: 0.0,
    stockout_risk_pct: 5.0,
    recommendation: {
      action: 'CLEARANCE PROMOTION',
      discount_pct: 25,
      objective: 'Complete inventory liquidation before 24h freshness write-off'
    },
    reasons: [
      'Perishable greens reach total spoilage within 24 hours (1 day expiry).',
      'Rainy evening slows walk-in conversion; app push discount is essential.',
      '25% discount provides immediate price hook for dinner recipe prep.'
    ],
    risk_flag: 'Critical Expiry',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 3,
        expected_revenue: 90,
        expected_profit: -270,
        profit_impact_pct: -150.0,
        inventory_reduction_pct: 25.0,
        stockout_risk_pct: 0.5,
        expiry_waste_reduction_pct: 25.0,
        score: 22.0
      },
      {
        discount_pct: 25,
        expected_sales_units: 12,
        expected_revenue: 270,
        expected_profit: 54,
        profit_impact_pct: +120.0,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 5.0,
        expiry_waste_reduction_pct: 100.0,
        score: 98.4
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'HIGH',
      expiry_urgency: 'CRITICAL',
      inventory_alert_score: 98
    },
    recommended_action: 'CLEARANCE PROMOTION',
    discount_pct: 25,
    explanation: 'Critical expiry risk (1 day left). Maximize salvage value with deep clearance discount.'
  },
  {
    product_id: 'P1779',
    product_name: 'Frozen Pizza Margherita',
    category: 'Ready to Eat',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS1',
    current_stock: 55,
    days_to_expiry: 90,
    demand_status: 'Rising',
    demand_trend_pct: 14.5,
    trend_signal: 'Surge',
    weather_condition: 'Rainy',
    time_of_day: 'Night',
    is_weekend: true,
    gross_margin_before_promo: 35.0,
    competitor_price_gap_pct: 2.5,
    stockout_risk_pct: 28.0,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 15,
      objective: 'Capture high-conversion weekend rainy night dinner orders'
    },
    reasons: [
      'Strong surge signal (+14.5%) during rainy weekend dinner hours.',
      'Frozen storage capacity allows quick turnaround.',
      '15% discount drives pairing with cold beverages and snacks.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 16,
        expected_revenue: 4000,
        expected_profit: 1400,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 29.1,
        stockout_risk_pct: 8.0,
        expiry_waste_reduction_pct: 10.0,
        score: 71.0
      },
      {
        discount_pct: 15,
        expected_sales_units: 38,
        expected_revenue: 8075,
        expected_profit: 2180,
        profit_impact_pct: +55.7,
        inventory_reduction_pct: 69.1,
        stockout_risk_pct: 28.0,
        expiry_waste_reduction_pct: 50.0,
        score: 95.3
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'MEDIUM',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'LOW',
      inventory_alert_score: 38
    },
    recommended_action: 'PROMOTE',
    discount_pct: 15,
    explanation: 'Weather and time-of-day signals indicate high conversion probability. 15% discount will maximize cart attachments.'
  },
  {
    product_id: 'P1880',
    product_name: 'Peanut Butter Creamy 500g',
    category: 'Groceries',
    city: 'Mumbai',
    dark_store_id: 'MUM-DS1',
    current_stock: 42,
    days_to_expiry: 180,
    demand_status: 'Stable',
    demand_trend_pct: -0.5,
    trend_signal: 'Normal',
    weather_condition: 'Clear',
    time_of_day: 'Morning',
    is_weekend: false,
    gross_margin_before_promo: 26.0,
    competitor_price_gap_pct: -1.0,
    stockout_risk_pct: 12.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Maintain stable price margin without discounting'
    },
    reasons: [
      'Steady staple consumption rate of 2.1 units per day.',
      'Competitor is pricing 1% higher; no risk of share loss.',
      'Inventory buffer (42 units) is ideal for next 20 days.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 14,
        expected_revenue: 2800,
        expected_profit: 728,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 33.3,
        stockout_risk_pct: 12.0,
        expiry_waste_reduction_pct: 0.0,
        score: 90.0
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'LOW',
      expiry_urgency: 'LOW',
      inventory_alert_score: 15
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Steady performance with good margin. Price is competitive. No promotion required.'
  },
  {
    product_id: 'P1991',
    product_name: 'Toothpaste Double Action 150g',
    category: 'Personal Care',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS3',
    current_stock: 210,
    days_to_expiry: 400,
    demand_status: 'Low',
    demand_trend_pct: -1.2,
    trend_signal: 'Normal',
    weather_condition: 'Clear',
    time_of_day: 'Morning',
    is_weekend: false,
    gross_margin_before_promo: 48.0,
    competitor_price_gap_pct: 5.5,
    stockout_risk_pct: 1.5,
    recommendation: {
      action: 'LIMITED PROMOTION',
      discount_pct: 10,
      objective: 'Stimulate pantry restocking with minor promotional incentive'
    },
    reasons: [
      'High gross margin (48%) provides generous headroom.',
      '210 units in dark store represents 35 days of forward cover.',
      '10% promotional tag attracts search clicks on essential care queries.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 18,
        expected_revenue: 1620,
        expected_profit: 777,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 8.6,
        stockout_risk_pct: 0.5,
        expiry_waste_reduction_pct: 0.0,
        score: 64.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 55,
        expected_revenue: 4455,
        expected_profit: 1881,
        profit_impact_pct: +142.1,
        inventory_reduction_pct: 26.2,
        stockout_risk_pct: 1.5,
        expiry_waste_reduction_pct: 0.0,
        score: 93.8
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'HIGH',
      expiry_urgency: 'LOW',
      inventory_alert_score: 46
    },
    recommended_action: 'LIMITED PROMOTION',
    discount_pct: 10,
    explanation: 'High margin allows for promotional testing to stimulate sluggish demand without risking profitability.'
  },
  {
    product_id: 'P2002',
    product_name: 'Energy Drink 250ml',
    category: 'Beverages',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS1',
    current_stock: 8,
    days_to_expiry: 150,
    demand_status: 'High',
    demand_trend_pct: 18.0,
    trend_signal: 'Surge',
    weather_condition: 'Hot',
    time_of_day: 'Afternoon',
    is_weekend: false,
    gross_margin_before_promo: 42.0,
    competitor_price_gap_pct: -3.0,
    stockout_risk_pct: 75.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Avoid fast out-of-stock failure during peak demand surge'
    },
    reasons: [
      'Critically low inventory of 8 cans with demand surging +18%.',
      'Stockout risk is 75% without immediate warehouse re-allocation.',
      'Discounting would exhaust store stock in less than 45 minutes.'
    ],
    risk_flag: 'Critical Stockout Risk',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 8,
        expected_revenue: 880,
        expected_profit: 370,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 100.0,
        stockout_risk_pct: 75.0,
        expiry_waste_reduction_pct: 0.0,
        score: 88.5
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'CRITICAL',
      overstock_urgency: 'LOW',
      expiry_urgency: 'LOW',
      inventory_alert_score: 92
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Stock is critically low relative to surging demand. Promotion would guarantee stockout.'
  },
  {
    product_id: 'P2113',
    product_name: 'Mixed Fruit Jam 500g',
    category: 'Groceries',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS1',
    current_stock: 130,
    days_to_expiry: 120,
    demand_status: 'Stable',
    demand_trend_pct: 0.8,
    trend_signal: 'Normal',
    weather_condition: 'Clear',
    time_of_day: 'Morning',
    is_weekend: true,
    gross_margin_before_promo: 24.0,
    competitor_price_gap_pct: 4.5,
    stockout_risk_pct: 6.0,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 5,
      objective: 'Drive breakfast bundling with bakery products'
    },
    reasons: [
      '130 units current stock represents slight overstock against run-rate.',
      'Weekend breakfast orders increase pairing propensity with bread & butter.',
      '5% discount optimizes sales volume while preserving 20%+ margin.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 15,
        expected_revenue: 2250,
        expected_profit: 540,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 11.5,
        stockout_risk_pct: 2.0,
        expiry_waste_reduction_pct: 0.0,
        score: 70.0
      },
      {
        discount_pct: 5,
        expected_sales_units: 38,
        expected_revenue: 5415,
        expected_profit: 1045,
        profit_impact_pct: +93.5,
        inventory_reduction_pct: 29.2,
        stockout_risk_pct: 6.0,
        expiry_waste_reduction_pct: 0.0,
        score: 94.6
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'LOW',
      inventory_alert_score: 32
    },
    recommended_action: 'PROMOTE',
    discount_pct: 5,
    explanation: 'Mild overstock. A small 5% promotion will help normalize inventory levels over the weekend.'
  },
  {
    product_id: 'P2224',
    product_name: 'Dog Food Small Breeds 1kg',
    category: 'Pet Care',
    city: 'Bengaluru',
    dark_store_id: 'BLR-DS2',
    current_stock: 35,
    days_to_expiry: 80,
    demand_status: 'Falling',
    demand_trend_pct: -6.5,
    trend_signal: 'Downtrend',
    weather_condition: 'Cloudy',
    time_of_day: 'Evening',
    is_weekend: false,
    gross_margin_before_promo: 18.0,
    competitor_price_gap_pct: 7.0,
    stockout_risk_pct: 4.0,
    recommendation: {
      action: 'LIMITED PROMOTION',
      discount_pct: 15,
      objective: 'Re-engage pet parents with competitive discount matching'
    },
    reasons: [
      'Demand slowdown of -6.5% linked to 7% competitor price advantage.',
      '35 units is manageable, but needs activation to avoid stale inventory.',
      '15% promotional pricing projects +85% conversion recovery.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 6,
        expected_revenue: 2700,
        expected_profit: 486,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 17.1,
        stockout_risk_pct: 1.0,
        expiry_waste_reduction_pct: 0.0,
        score: 54.0
      },
      {
        discount_pct: 15,
        expected_sales_units: 19,
        expected_revenue: 7267,
        expected_profit: 654,
        profit_impact_pct: +34.6,
        inventory_reduction_pct: 54.3,
        stockout_risk_pct: 4.0,
        expiry_waste_reduction_pct: 0.0,
        score: 91.5
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'MEDIUM',
      expiry_urgency: 'LOW',
      inventory_alert_score: 39
    },
    recommended_action: 'LIMITED PROMOTION',
    discount_pct: 15,
    explanation: 'Falling demand and competitive pricing pressure. 15% discount recommended to prevent inventory stagnation.'
  },
  {
    product_id: 'P2335',
    product_name: 'Fresh Tomatoes 1kg',
    category: 'Fruits & Vegetables',
    city: 'Mumbai',
    dark_store_id: 'MUM-DS1',
    current_stock: 85,
    days_to_expiry: 3,
    demand_status: 'High',
    demand_trend_pct: 4.0,
    trend_signal: 'Normal',
    weather_condition: 'Rainy',
    time_of_day: 'Morning',
    is_weekend: true,
    gross_margin_before_promo: 20.0,
    competitor_price_gap_pct: 2.0,
    stockout_risk_pct: 25.0,
    recommendation: {
      action: 'PROMOTE',
      discount_pct: 10,
      objective: 'Accelerate fresh lot rotation within 72-hour peak freshness'
    },
    reasons: [
      '85kg fresh lot must clear within 3 days to avoid soft fruit rejection.',
      'Weekend kitchen cooking demand is strong (+4.0%).',
      '10% discount ensures full lot clears with zero write-off.'
    ],
    risk_flag: 'Approaching Expiry',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 45,
        expected_revenue: 2250,
        expected_profit: 450,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 52.9,
        stockout_risk_pct: 10.0,
        expiry_waste_reduction_pct: 50.0,
        score: 72.0
      },
      {
        discount_pct: 10,
        expected_sales_units: 80,
        expected_revenue: 3600,
        expected_profit: 440,
        profit_impact_pct: -2.2,
        inventory_reduction_pct: 94.1,
        stockout_risk_pct: 25.0,
        expiry_waste_reduction_pct: 98.0,
        score: 95.2
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'HIGH',
      expiry_urgency: 'HIGH',
      inventory_alert_score: 77
    },
    recommended_action: 'PROMOTE',
    discount_pct: 10,
    explanation: 'Highly perishable item approaching expiry. Moderate discount will ensure sell-through during peak weekend demand.'
  },
  {
    product_id: 'P2446',
    product_name: 'Brown Eggs 6 Pcs',
    category: 'Dairy',
    city: 'Hyderabad',
    dark_store_id: 'HYD-DS2',
    current_stock: 40,
    days_to_expiry: 10,
    demand_status: 'Stable',
    demand_trend_pct: 1.5,
    trend_signal: 'Normal',
    weather_condition: 'Clear',
    time_of_day: 'Morning',
    is_weekend: false,
    gross_margin_before_promo: 16.0,
    competitor_price_gap_pct: -1.0,
    stockout_risk_pct: 14.0,
    recommendation: {
      action: 'NO PROMOTION',
      discount_pct: 0,
      objective: 'Preserve grocery basket staple baseline margins'
    },
    reasons: [
      'Consistent organic consumption of 4.5 packs/day.',
      'Gross margin of 16% is tightly optimized.',
      'Inventory buffer (40 units) covers 9 days cleanly.'
    ],
    risk_flag: '',
    options: [
      {
        discount_pct: 0,
        expected_sales_units: 18,
        expected_revenue: 1620,
        expected_profit: 259,
        profit_impact_pct: 0.0,
        inventory_reduction_pct: 45.0,
        stockout_risk_pct: 14.0,
        expiry_waste_reduction_pct: 0.0,
        score: 91.0
      }
    ],
    inventory_snapshot: {
      stockout_urgency: 'LOW',
      overstock_urgency: 'LOW',
      expiry_urgency: 'LOW',
      inventory_alert_score: 19
    },
    recommended_action: 'NO PROMOTION',
    discount_pct: 0,
    explanation: 'Consistent staple product performing normally. Margins are tight, preserve full price.'
  }
];
