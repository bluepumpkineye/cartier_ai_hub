import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.llm_client import chat_completion
from utils.llm_client import chat_completion, DEFAULT_MODEL

CARTIER_COLORS = ["#8B0000", "#C5A028", "#2C2C2C", "#E8E0D0", "#6B4E2D", "#4A4A6A"]

def render_marketing_budget():
    st.markdown("## 📢 Marketing Investment — Budget vs Actual")
    
    try:
        df = pd.read_csv("data/marketing_data.csv")
    except FileNotFoundError:
        st.error("Marketing data not found. Please run the data generator.")
        return

    # ── Filters ──
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_markets = st.multiselect("Markets", df["market"].unique().tolist(),
                                     default=df["market"].unique().tolist()[:3])
    with col2:
        sel_quarters = st.multiselect("Quarter", df["quarter"].unique().tolist(),
                                      default=df["quarter"].unique().tolist())
    with col3:
        sel_status = st.multiselect("Status", df["status"].unique().tolist(),
                                    default=df["status"].unique().tolist())

    filtered = df[
        df["market"].isin(sel_markets) &
        df["quarter"].isin(sel_quarters) &
        df["status"].isin(sel_status)
    ]

    # ── KPI Row ──
    total_budget   = filtered["budget_usd"].sum()
    total_actual   = filtered["actual_usd"].sum()
    total_variance = total_actual - total_budget
    avg_roi        = filtered["roi"].mean()
    total_rev_attr = filtered["revenue_attributed"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Budget",    f"${total_budget/1e6:.1f}M")
    k2.metric("Total Actual",    f"${total_actual/1e6:.1f}M")
    delta_color = "inverse" if total_variance > 0 else "normal"
    k3.metric("Variance",        f"${total_variance/1e6:.1f}M",
              delta=f"{total_variance/total_budget*100:.1f}%", delta_color=delta_color)
    k4.metric("Avg ROI",         f"{avg_roi:.0f}%")
    k5.metric("Revenue Attributed", f"${total_rev_attr/1e6:.1f}M")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Budget vs Actual by Campaign")
        camp_data = filtered.groupby("campaign")[["budget_usd", "actual_usd"]].sum().reset_index()
        camp_data = camp_data.sort_values("budget_usd", ascending=False).head(8)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Budget",  x=camp_data["campaign"], 
                              y=camp_data["budget_usd"],  marker_color="#2C2C2C"))
        fig.add_trace(go.Bar(name="Actual",  x=camp_data["campaign"], 
                              y=camp_data["actual_usd"],   marker_color="#8B0000"))
        fig.update_layout(
            barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", legend=dict(font=dict(color="#1C1C1C", size=11)),
            yaxis_tickformat="$,.0f", xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### ROI by Media Type")
        media_roi = filtered.groupby("media_type")["roi"].mean().reset_index().sort_values("roi")
        colors    = ["#8B0000" if v < 0 else "#C5A028" for v in media_roi["roi"]]
        fig = px.bar(media_roi, x="roi", y="media_type", orientation="h",
                     labels={"roi": "Avg ROI (%)", "media_type": "Media Type"},
                     color="roi", color_continuous_scale=["#8B0000", "#C5A028"])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### Spend Variance by Market")
        mkt_var = filtered.groupby("market")[["budget_usd", "actual_usd"]].sum()
        mkt_var["variance_pct"] = (mkt_var["actual_usd"] - mkt_var["budget_usd"]) / mkt_var["budget_usd"] * 100
        mkt_var = mkt_var.reset_index().sort_values("variance_pct")
        colors  = ["#8B0000" if v > 5 else "#C5A028" if v > 0 else "#2C6B35" 
                   for v in mkt_var["variance_pct"]]
        fig = px.bar(mkt_var, x="market", y="variance_pct",
                     labels={"variance_pct": "Variance (%)", "market": "Market"},
                     color="variance_pct",
                     color_continuous_scale=["#2C6B35", "#C5A028", "#8B0000"])
        fig.add_hline(y=0, line_dash="dash", line_color="#E8E0D0", opacity=0.5)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown("#### Impressions vs Revenue Attributed")
        scatter_data = filtered.groupby("campaign").agg(
            impressions=("impressions", "sum"),
            revenue_attributed=("revenue_attributed", "sum"),
            roi=("roi", "mean")
        ).reset_index()
        fig = px.scatter(scatter_data, x="impressions", y="revenue_attributed",
                         size="roi", color="roi",
                         color_continuous_scale=["#2C2C2C", "#8B0000", "#C5A028"],
                         hover_data=["campaign"],
                         labels={"impressions": "Total Impressions",
                                  "revenue_attributed": "Revenue Attributed ($)"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Detailed Table ──
    st.markdown("#### Campaign Detail")
    display_cols = ["campaign", "market", "media_type", "budget_usd", 
                    "actual_usd", "variance_pct", "roi", "status"]
    st.dataframe(
        filtered[display_cols]
        .sort_values("roi", ascending=False)
        .style
        .format({"budget_usd": "${:,.0f}", "actual_usd": "${:,.0f}",
                 "variance_pct": "{:.1f}%",   "roi": "{:.0f}%"})
        .background_gradient(subset=["roi"], cmap="RdYlGn"),
        use_container_width=True, height=350
    )

    # ── AI Commentary ──
    st.markdown("---")
    if st.button("🤖 Generate Marketing Intelligence Report", type="primary"):
        summary = {
            "total_budget":     f"${total_budget/1e6:.1f}M",
            "total_actual":     f"${total_actual/1e6:.1f}M",
            "variance":         f"${total_variance/1e6:.1f}M ({total_variance/total_budget*100:.1f}%)",
            "avg_roi":          f"{avg_roi:.0f}%",
            "best_media":       filtered.groupby("media_type")["roi"].mean().idxmax(),
            "worst_media":      filtered.groupby("media_type")["roi"].mean().idxmin(),
            "over_budget_mkts": filtered[filtered["variance_pct"] > 0]["market"].unique().tolist(),
        }
        with st.spinner("Analysing marketing performance..."):
            messages = [
                {"role": "system", "content":
                 "You are Cartier APAC's CMO advisor. Provide an executive marketing performance "
                 "analysis with 3 optimisation recommendations for reallocation of budget. "
                 "Be specific, data-driven, and brand-appropriate."},
                {"role": "user", "content": f"Marketing performance data:\n{summary}"}
            ]
            active_model = st.session_state.get("active_model", DEFAULT_MODEL)
            insight      = chat_completion(messages, model=active_model, temperature=0.3)

        st.markdown("#### 💡 Marketing Intelligence")
        st.markdown(insight)