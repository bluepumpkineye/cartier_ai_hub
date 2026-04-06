import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.llm_client import chat_completion
from utils.llm_client import chat_completion, DEFAULT_MODEL

CARTIER_COLORS =["#8B0000", "#C5A028", "#9B8B6E", "#D4C5A9", "#4A3728", "#C5A028"]

def render_sales_analytics():
    st.markdown("## 📊 Sales Channel & Revenue Optimisation")
    
    try:
        df = pd.read_csv("data/sales_data.csv")
        df["date"] = pd.to_datetime(df["date"])
    except FileNotFoundError:
        st.error("Sales data not found. Please run the data generator.")
        return

    # ── Filters ──
    with st.expander("🔧 Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            markets = st.multiselect("Markets", df["market"].unique().tolist(),
                                     default=df["market"].unique().tolist())
        with col2:
            channels = st.multiselect("Channels", df["channel"].unique().tolist(),
                                      default=df["channel"].unique().tolist())
        with col3:
            categories = st.multiselect("Categories", df["category"].unique().tolist(),
                                        default=df["category"].unique().tolist())
        with col4:
            years = st.multiselect("Years", sorted(df["year"].unique().tolist()),
                                   default=sorted(df["year"].unique().tolist()))

    mask = (
        df["market"].isin(markets) &
        df["channel"].isin(channels) &
        df["category"].isin(categories) &
        df["year"].isin(years)
    )
    filtered = df[mask]

    if filtered.empty:
        st.warning("No data matches the selected filters.")
        return

    # ── KPI Row ──
    total_rev   = filtered["revenue_usd"].sum()
    total_gp    = filtered["gross_profit"].sum()
    avg_margin  = filtered["gross_margin"].mean()
    total_units = filtered["units_sold"].sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Revenue",   f"${total_rev/1e6:.1f}M")
    k2.metric("Gross Profit",    f"${total_gp/1e6:.1f}M")
    k3.metric("Avg Gross Margin",f"{avg_margin:.1f}%")
    k4.metric("Units Sold",      f"{total_units:,}")

    st.markdown("---")

    # ── Row 1 Charts ──
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Revenue by Channel")
        ch_data = filtered.groupby("channel")["revenue_usd"].sum().reset_index()
        fig = px.bar(ch_data, x="channel", y="revenue_usd",
                     color="channel", color_discrete_sequence=CARTIER_COLORS,
                     labels={"revenue_usd": "Revenue (USD)", "channel": "Channel"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", showlegend=False,
            yaxis_tickformat="$,.0f"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Revenue by Market")
        mk_data = filtered.groupby("market")["revenue_usd"].sum().reset_index().sort_values(
            "revenue_usd", ascending=True
        )
        fig = px.bar(mk_data, x="revenue_usd", y="market", orientation="h",
                     color="revenue_usd", color_continuous_scale=["#2C2C2C", "#8B0000", "#C5A028"],
                     labels={"revenue_usd": "Revenue (USD)", "market": "Market"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", showlegend=False,
            xaxis_tickformat="$,.0f", coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2 ──
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### Monthly Revenue Trend")
        trend = filtered.groupby(
            filtered["date"].dt.to_period("M")
        )["revenue_usd"].sum().reset_index()
        trend["date"] = trend["date"].astype(str)
        fig = px.line(trend, x="date", y="revenue_usd",
                      color_discrete_sequence=["#C5A028"],
                      labels={"revenue_usd": "Revenue (USD)", "date": "Month"})
        fig.update_traces(line_width=2.5)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", yaxis_tickformat="$,.0f"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown("#### Category Revenue Mix")
        cat_data = filtered.groupby("category")["revenue_usd"].sum().reset_index()
        fig = px.pie(cat_data, values="revenue_usd", names="category",
                     color_discrete_sequence=CARTIER_COLORS, hole=0.45)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C",
            legend=dict(font=dict(color="#1C1C1C", size=11))
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Margin Heatmap ──
    st.markdown("#### Gross Margin Heatmap — Market × Channel")
    heatmap = filtered.groupby(["market", "channel"])["gross_margin"].mean().reset_index()
    heatmap_pivot = heatmap.pivot(index="market", columns="channel", values="gross_margin")
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns.tolist(),
        y=heatmap_pivot.index.tolist(),
        colorscale=[[0, "#F5F0E8"], [0.5, "#C5A028"], [1, "#8B0000"]],
        text=[[f"{v:.1f}%" for v in row] for row in heatmap_pivot.values],
        texttemplate="%{text}", textfont={"size": 12},
        showscale=True
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#1C1C1C", height=320
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── AI Commentary ──
    st.markdown("---")
    if st.button("🤖 Generate AI Revenue Insights", type="primary"):
        summary = {
            "top_market":    filtered.groupby("market")["revenue_usd"].sum().idxmax(),
            "top_channel":   filtered.groupby("channel")["revenue_usd"].sum().idxmax(),
            "top_category":  filtered.groupby("category")["revenue_usd"].sum().idxmax(),
            "total_revenue": f"${total_rev/1e6:.1f}M",
            "avg_margin":    f"{avg_margin:.1f}%",
            "lowest_margin_market": filtered.groupby("market")["gross_margin"].mean().idxmin(),
        }
        with st.spinner("Generating executive insights..."):
            messages = [
                {"role": "system", "content": 
                 "You are the Cartier APAC Head of Revenue Strategy. Provide concise, "
                 "executive-level insights and 3 specific optimisation recommendations "
                 "based on the sales data summary provided. Use sophisticated business language."},
                {"role": "user", "content": 
                 f"Analyse this Cartier APAC sales performance data and provide strategic insights:\n{summary}"}
            ]
            active_model = st.session_state.get("active_model", DEFAULT_MODEL)
            insight      = chat_completion(messages, model=active_model, temperature=0.3)

        st.markdown("#### 💡 AI Revenue Intelligence")
        st.markdown(insight)