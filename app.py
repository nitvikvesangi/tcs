"""
app.py — Quick Commerce Promotion Recommender Dashboard
Powered by: quick_commerce_master_synthetic_dataset.csv + ml_engine (RandomForest) + ai_engine (Groq / NVIDIA LLM)
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Quick Commerce AI Platform",
    page_icon="🛒",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Load CSV Data & Engines
# ---------------------------------------------------------------------------
CSV_PATH = "quick_commerce_master_synthetic_dataset.csv"

@st.cache_data
def load_csv_data():
    if not os.path.exists(CSV_PATH):
        st.error(f"CSV file not found at {CSV_PATH}")
        return pd.DataFrame()
    df = pd.read_csv(CSV_PATH)
    return df

@st.cache_resource
def load_engines():
    errors = {}
    try:
        from ml_engine import predict_action
    except Exception as e:
        errors["ml_engine"] = str(e)
        predict_action = None

    try:
        from ai_engine import generate_explanation, generate_risk_flag, _call_llm
    except Exception as e:
        errors["ai_engine"] = str(e)
        generate_explanation = None
        generate_risk_flag = None
        _call_llm = None

    try:
        from promo_recommender import recommend_batch
    except Exception as e:
        errors["promo_recommender"] = str(e)
        recommend_batch = None

    return predict_action, generate_explanation, generate_risk_flag, _call_llm, recommend_batch, errors

df_master = load_csv_data()
predict_action, generate_explanation, generate_risk_flag, _call_llm, recommend_batch, load_errors = load_engines()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🛒 Quick Commerce AI & ML Platform")
st.caption(f"📁 Dataset: `{CSV_PATH}` ({len(df_master):,} records) | 🧠 RandomForest ML Model | 🤖 Groq / NVIDIA LLM")

if load_errors:
    for mod, err in load_errors.items():
        st.warning(f"⚠️ `{mod}`: {err}")

# ---------------------------------------------------------------------------
# Navigation Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Master Dataset & Live ML Engine",
    "🔬 One-Click CSV Product Predictor",
    "🤖 AI Retail Assistant (Chat)",
])

# ===========================================================================
# TAB 1: Master Dataset & Live ML Predictions
# ===========================================================================
with tab1:
    st.sidebar.header("🔍 Dataset Filters")

    if df_master.empty:
        st.error("No CSV data loaded.")
    else:
        cities = ["All"] + sorted(df_master["city"].dropna().unique().tolist())
        categories = ["All"] + sorted(df_master["category"].dropna().unique().tolist())
        actions = ["All"] + sorted(df_master["recommended_action"].dropna().unique().tolist())

        selected_city = st.sidebar.selectbox("City", cities)
        selected_category = st.sidebar.selectbox("Category", categories)
        selected_action = st.sidebar.selectbox("CSV Target Action", actions)
        search_query = st.sidebar.text_input("🔎 Search Product Name or ID", "")

        # Filter DataFrame
        filtered_df = df_master.copy()
        if selected_city != "All":
            filtered_df = filtered_df[filtered_df["city"] == selected_city]
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]
        if selected_action != "All":
            filtered_df = filtered_df[filtered_df["recommended_action"] == selected_action]
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df["product_name"].astype(str).str.lower().str.contains(q) |
                filtered_df["product_id"].astype(str).str.lower().str.contains(q)
            ]

        max_rows = st.sidebar.slider("Rows to display", 10, 500, 50)
        display_df = filtered_df.head(max_rows).copy()

        # Run ML engine predictions on the displayed slice
        if predict_action:
            ml_actions = []
            ml_confs = []
            for _, row in display_df.iterrows():
                row_dict = row.to_dict()
                res = predict_action(row_dict)
                ml_actions.append(res["action"])
                ml_confs.append(f"{res['confidence']*100:.1f}%")
            display_df["ml_predicted_action"] = ml_actions
            display_df["ml_confidence"] = ml_confs

        # KPI Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Matching Rows", f"{len(filtered_df):,}")
        col2.metric("Clearance Items", len(filtered_df[filtered_df["recommended_action"] == "CLEARANCE"]))
        col3.metric("Price Gap Items", len(filtered_df[filtered_df["recommended_action"] == "COMPETITIVE PRICE OFFER"]))
        col4.metric("Quality Review", len(filtered_df[filtered_df["recommended_action"] == "REVIEW PRODUCT QUALITY"]))
        col5.metric("No Promo (Restraint)", len(filtered_df[filtered_df["recommended_action"] == "NO PROMOTION"]))

        st.subheader("📋 Product Table (CSV Ground Truth vs Live ML Prediction)")

        cols_to_show = [
            "product_id", "product_name", "category", "city", "dark_store_id",
            "recommended_action", "ml_predicted_action", "ml_confidence",
            "current_stock", "days_to_expiry", "competitor_price_gap_pct",
            "product_rating", "negative_review_rate", "demand_trend_pct", "mrp"
        ]
        cols_to_show = [c for c in cols_to_show if c in display_df.columns]

        # Action highlighter
        def highlight_actions(val):
            if val == "CLEARANCE":
                return "background-color: #ff4d4f; color: white; font-weight: bold;"
            elif val == "COMPETITIVE PRICE OFFER":
                return "background-color: #faad14; color: black; font-weight: bold;"
            elif val == "REVIEW PRODUCT QUALITY":
                return "background-color: #fa8c16; color: white; font-weight: bold;"
            elif val == "REPLENISH / AVOID DISCOUNT":
                return "background-color: #1890ff; color: white; font-weight: bold;"
            elif val == "PROMOTE":
                return "background-color: #52c41a; color: white; font-weight: bold;"
            return ""

        styled_table = display_df[cols_to_show].style.map(
            highlight_actions,
            subset=[c for c in ["recommended_action", "ml_predicted_action"] if c in display_df.columns]
        )
        st.dataframe(styled_table, height=500, use_container_width=True)

# ===========================================================================
# TAB 2: One-Click Product Predictor & Simulator
# ===========================================================================
with tab2:
    st.subheader("🔬 Test ML Model & AI Explanations on Any Product from CSV")
    st.write("Pick any row directly from your 10,000-record CSV dataset, or tweak numbers to simulate new scenarios:")

    if df_master.empty:
        st.warning("Please load the dataset.")
    else:
        # Create friendly labels for dropdown
        df_master["display_label"] = (
            df_master["product_id"].astype(str) + " - " +
            df_master["product_name"].astype(str) + " (" +
            df_master["city"].astype(str) + " | " +
            df_master["category"].astype(str) + " | CSV Action: " +
            df_master["recommended_action"].astype(str) + ")"
        )

        selected_label = st.selectbox(
            "Select Product Record from CSV (10,000 options):",
            df_master["display_label"].tolist()
        )

        selected_row = df_master[df_master["display_label"] == selected_label].iloc[0].to_dict()

        st.divider()
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### ⚙️ Product Parameters (Loaded from CSV)")
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("Product Name", selected_row.get("product_name", ""))
                p_cat = st.text_input("Category", selected_row.get("category", ""))
                days_exp = st.number_input("Days to Expiry", 0, 365, int(selected_row.get("days_to_expiry", 30)))
                curr_stock = st.number_input("Current Stock", 0, 2000, int(selected_row.get("current_stock", 20)))
                min_stock = st.number_input("Minimum Stock", 0, 500, int(selected_row.get("minimum_stock", 10)))
                mrp_val = st.number_input("MRP (₹)", 0.0, 5000.0, float(selected_row.get("mrp", 100.0)))
            with c2:
                p_store = st.text_input("Dark Store ID", selected_row.get("dark_store_id", "DS-1"))
                p_city = st.text_input("City", selected_row.get("city", "Hyderabad"))
                comp_gap = st.number_input("Competitor Gap %", -50.0, 100.0, float(selected_row.get("competitor_price_gap_pct", 0.0)))
                p_rating = st.slider("Product Rating", 1.0, 5.0, float(selected_row.get("product_rating", 4.0)), 0.1)
                neg_rate = st.slider("Negative Review Rate", 0.0, 1.0, float(selected_row.get("negative_review_rate", 0.05)), 0.01)
                dem_trend = st.number_input("Demand Trend %", -100.0, 300.0, float(selected_row.get("demand_trend_pct", 0.0)))

        with col_right:
            st.markdown("### 🎯 Live Model Prediction")

            # Form full dictionary matching model requirements
            input_row = {**selected_row}
            input_row.update({
                "product_name": p_name,
                "category": p_cat,
                "days_to_expiry": days_exp,
                "current_stock": curr_stock,
                "minimum_stock": min_stock,
                "mrp": mrp_val,
                "dark_store_id": p_store,
                "city": p_city,
                "competitor_price_gap_pct": comp_gap,
                "product_rating": p_rating,
                "negative_review_rate": neg_rate,
                "demand_trend_pct": dem_trend,
            })

            if predict_action:
                ml_res = predict_action(input_row)
                action = ml_res["action"]
                confidence = ml_res["confidence"]

                action_colors = {
                    "CLEARANCE": "🔴",
                    "COMPETITIVE PRICE OFFER": "🟡",
                    "REVIEW PRODUCT QUALITY": "🟠",
                    "REPLENISH / AVOID DISCOUNT": "🔵",
                    "PROMOTE": "🟢",
                    "NO PROMOTION": "⚪",
                }
                icon = action_colors.get(action, "⚡")

                st.success(f"## {icon} Predicted Action: **{action}**")
                st.metric("Model Confidence Score", f"{confidence * 100:.1f}%")

                csv_ground_truth = selected_row.get("recommended_action", "N/A")
                st.info(f"📌 **Original CSV Label:** `{csv_ground_truth}` | **ML Match:** {'✅ Match' if action == csv_ground_truth else '⚠️ Alternative Recommendation'}")

                # Probabilities chart
                probs = ml_res.get("probabilities", {})
                if probs:
                    prob_df = pd.DataFrame(
                        [(k, v) for k, v in sorted(probs.items(), key=lambda x: -x[1])],
                        columns=["Action", "Probability"]
                    )
                    st.bar_chart(prob_df.set_index("Action"))

            # AI Explanation Button
            st.markdown("### ✨ AI Natural Language Reasoning")
            if st.button("Generate AI Explanation (LLM)", type="primary"):
                if generate_explanation:
                    with st.spinner("Generating reasoning via LLM..."):
                        explanation = generate_explanation(input_row)
                        st.markdown(f"**AI Manager Briefing:**\n\n{explanation}")
                        risk = generate_risk_flag(input_row) if generate_risk_flag else None
                        if risk:
                            st.warning(f"🚨 **Operational Risk Flag:** {risk}")
                else:
                    st.error("AI engine not loaded. Check API keys.")

# ===========================================================================
# TAB 3: AI Chat Assistant (with Live CSV Inventory Intelligence)
# ===========================================================================
with tab3:
    st.subheader("🤖 Quick Commerce AI Assistant (Connected to 10,000 CSV Products)")
    st.caption("Ask anything about your inventory, clearance items, dark-store performance, or specific products.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask: 'What products should I promote?', 'Which items in Bengaluru are expiring?', etc.")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing live CSV dataset and generating data-backed response..."):
                if _call_llm and not df_master.empty:
                    # Dynamically filter relevant products from CSV based on user query
                    q_lower = user_input.lower()
                    
                    # 1. Urgent clearance
                    clearance_df = df_master[df_master["recommended_action"] == "CLEARANCE"]
                    # 2. Promote / Growth
                    promote_df = df_master[df_master["recommended_action"] == "PROMOTE"]
                    # 3. Competitor price war
                    comp_df = df_master[df_master["recommended_action"] == "COMPETITIVE PRICE OFFER"]
                    # 4. Quality review
                    qual_df = df_master[df_master["recommended_action"] == "REVIEW PRODUCT QUALITY"]

                    # Filter by city if user mentioned one
                    for c in df_master["city"].dropna().unique():
                        if c.lower() in q_lower:
                            clearance_df = clearance_df[clearance_df["city"] == c]
                            promote_df = promote_df[promote_df["city"] == c]
                            comp_df = comp_df[comp_df["city"] == c]
                            qual_df = qual_df[qual_df["city"] == c]
                            break

                    clearance_sample = clearance_df[["product_id", "product_name", "city", "dark_store_id", "days_to_expiry", "current_stock", "mrp", "current_discount_pct"]].head(5).to_dict("records")
                    promote_sample = promote_df[["product_id", "product_name", "city", "dark_store_id", "demand_trend_pct", "current_stock", "mrp", "current_discount_pct"]].head(5).to_dict("records")
                    comp_sample = comp_df[["product_id", "product_name", "city", "dark_store_id", "competitor_price_gap_pct", "current_stock", "mrp"]].head(5).to_dict("records")
                    qual_sample = qual_df[["product_id", "product_name", "city", "dark_store_id", "product_rating", "negative_review_rate", "current_stock"]].head(3).to_dict("records")

                    inventory_context = f"""
LIVE REAL-TIME INVENTORY SNAPSHOT FROM COMPANY CSV:
[URGENT EXPIRY CLEARANCE PRODUCTS (days_to_expiry <= 2)]:
{clearance_sample}

[TOP PROMOTE / DEMAND GROWTH CANDIDATES]:
{promote_sample}

[COMPETITOR PRICE GAP DISCOUNTS]:
{comp_sample}

[QUALITY REVIEW REQUIRED (High Negative Reviews / Low Rating)]:
{qual_sample}
"""

                    system_prompt = f"""You are an intelligent retail AI operations assistant for a Quick Commerce dark-store network.
You have direct access to the real-time company dataset ({len(df_master):,} records).

{inventory_context}

STRICT INSTRUCTIONS:
1. NEVER give generic boilerplate or placeholder text like "Bananas, Eggs, Bread" unless they are in the snapshot.
2. ALWAYS cite specific REAL products from the inventory snapshot above with their exact Product Name, Product ID (e.g. P0059), Dark Store ID (e.g. BEN-DS4), current stock, days to expiry, and rupee (₹) pricing.
3. Structure your answer with clear bold headers, bullet points, and specific action items a store manager can execute in 30 seconds.
"""
                    llm_msgs = [{"role": "system", "content": system_prompt}] + [
                        {"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history
                    ]
                    response = _call_llm(llm_msgs, temperature=0.3, max_tokens=700)
                elif _call_llm:
                    response = _call_llm([{"role": "user", "content": user_input}])
                else:
                    response = "LLM provider is not configured. Please set GROQ_API_KEY or NVIDIA_API_KEY."

            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

    if st.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()