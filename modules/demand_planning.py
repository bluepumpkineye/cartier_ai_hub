import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from utils.llm_client import chat_completion
from utils.llm_client import chat_completion, DEFAULT_MODEL

def render_demand_planning():
    st.markdown("## 📦 Demand & Supply Planning Intelligence")
    
    try:
        df = pd.read_csv("data/supply_data.csv")
    except FileNotFoundError:
        st.error("Supply data not found. Please run the data generator.")
        return

    # ── Filters ──
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_cat = st.selectbox("Category", ["All"] + df["category"].unique().tolist())
    with col2:
        sel_mkt = st.selectbox("Market", ["All"] + df["market"].unique().tolist())
    with col3:
        sel_risk = st.multiselect("Stockout Risk", ["High", "Medium", "Low"],
                                  default=["High", "Medium", "Low"])

    filtered = df.copy()
    if sel_cat != "All": filtered = filtered[filtered["category"] == sel_cat]
    if sel_mkt != "All": filtered = filtered[filtered["market"] == sel_mkt]
    filtered = filtered[filtered["stockout_risk"].isin(sel_risk)]

    # ── KPI Row ──
    high_stockout = len(df[df["stockout_risk"] == "High"])
    high_overstock = len(df[df["overstock_risk"] == "High"])
    avg_cover = df["stock_cover_weeks"].mean()
    avg_lead  = df["lead_time_days"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("High Stockout Risk SKUs",   f"{high_stockout}",   delta="Needs attention", delta_color="inverse")
    k2.metric("High Overstock Risk SKUs",  f"{high_overstock}",  delta="Capital tied up",  delta_color="inverse")
    k3.metric("Avg Stock Cover",           f"{avg_cover:.1f} wks")
    k4.metric("Avg Lead Time",             f"{avg_lead:.0f} days")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Forecast vs Actual Demand by Category")
        cat_comp = df.groupby("category")[["forecast_demand", "actual_demand"]].mean().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Forecast", x=cat_comp["category"], 
                              y=cat_comp["forecast_demand"], marker_color="#2C2C2C"))
        fig.add_trace(go.Bar(name="Actual",   x=cat_comp["category"], 
                              y=cat_comp["actual_demand"],   marker_color="#8B0000"))
        fig.update_layout(
            barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", legend=dict(font=dict(color="#1C1C1C", size=11))
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Stockout Risk Distribution by Market")
        risk_mkt = df.groupby(["market", "stockout_risk"]).size().reset_index(name="count")
        fig = px.bar(risk_mkt, x="market", y="count", color="stockout_risk",
                     color_discrete_map={"High": "#8B0000", "Medium": "#C5A028", "Low": "#2C6B35"},
                     barmode="stack",
                     labels={"count": "SKU Count", "stockout_risk": "Risk Level"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", legend=dict(font=dict(color="#1C1C1C", size=11)),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Simple ML Forecast ──
    st.markdown("#### 📈 Demand Forecasting — 6-Month Projection")
    st.caption("Linear trend model applied to historical demand patterns per category")

    forecast_results = []
    for cat in df["category"].unique():
        cat_df = df[df["category"] == cat].copy()
        cat_df["time_idx"] = range(len(cat_df))
        
        X = cat_df["time_idx"].values.reshape(-1, 1)
        y = cat_df["actual_demand"].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_idx   = np.arange(len(cat_df), len(cat_df) + 6).reshape(-1, 1)
        future_preds = model.predict(future_idx)
        
        for i, pred in enumerate(future_preds, 1):
            forecast_results.append({
                "category": cat,
                "month_ahead": f"M+{i}",
                "forecasted_demand": max(0, round(pred, 0))
            })

    forecast_df = pd.DataFrame(forecast_results)
    fig = px.line(forecast_df, x="month_ahead", y="forecasted_demand",
                  color="category", color_discrete_sequence=["#8B0000","#C5A028","#2C6B35","#4A4A6A","#6B4E2D"],
                  labels={"forecasted_demand": "Forecasted Units", "month_ahead": "Forecast Period"},
                  markers=True)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#1C1C1C", legend=dict(font=dict(color="#1C1C1C", size=11))
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Critical Items Table ──
    st.markdown("#### ⚠️ Critical Inventory Alerts")
    critical = df[df["stockout_risk"] == "High"][
        ["product", "market", "category", "stock_available", 
         "forecast_demand", "stock_cover_weeks", "lead_time_days"]
    ].sort_values("stock_cover_weeks").head(15)
    
    st.dataframe(
        critical.style
        .highlight_between(subset=["stock_cover_weeks"], left=0, right=4, color="#8B000055")
        .format({"stock_cover_weeks": "{:.1f}", "lead_time_days": "{:.0f}"}),
        use_container_width=True, height=350
    )

    # ── AI Supply Intelligence ──
    st.markdown("---")
    if st.button("🤖 Generate Supply Chain Intelligence", type="primary"):
        with st.spinner("Analysing supply chain data..."):
            summary = {
                "high_stockout_skus":  high_stockout,
                "high_overstock_skus": high_overstock,
                "avg_stock_cover_wks": round(avg_cover, 1),
                "avg_lead_time_days":  round(avg_lead, 0),
                "worst_category":      df.groupby("category")["stockout_risk"].apply(
                    lambda x: (x == "High").mean()
                ).idxmax(),
                "worst_market":        df.groupby("market")["stockout_risk"].apply(
                    lambda x: (x == "High").mean()
                ).idxmax(),
            }
            messages = [
                {"role": "system", "content":
                 "You are Cartier APAC's VP of Supply Chain. Provide executive-level supply chain "
                 "risk analysis with 3 actionable recommendations to optimise inventory and "
                 "reduce stockout risk while minimising working capital. Be specific."},
                {"role": "user", "content": f"Supply chain data:\n{summary}"}
            ]
            # AFTER (uses sidebar model selector)
            active_model = st.session_state.get("active_model", DEFAULT_MODEL)
            insight      = chat_completion(messages, model=active_model, temperature=0.3)
        st.markdown("#### 💡 Supply Chain Intelligence")
        st.markdown(insight)