import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
from utils.llm_client import chat_completion, DEFAULT_MODEL

def render_llmops():
    st.markdown("## ⚙️ LLMOps — Model Monitoring & Governance")
    st.caption("Internal AI platform observability dashboard — demonstrating MLOps/LLMOps capabilities")

    np.random.seed(42)
    
    # ── Synthetic Model Metrics ──
    models = {
        "gpt-4o (CRM Assistant)":       {"latency": 1.24, "uptime": 99.8, "cost_day": 42.50, "queries": 284, "version": "v2.1"},
        "gpt-4o (Sales Insights)":       {"latency": 1.41, "uptime": 99.6, "cost_day": 31.20, "queries": 198, "version": "v1.8"},
        "text-embedding-3-small (RAG)":  {"latency": 0.18, "uptime": 99.9, "cost_day": 8.40,  "queries": 892, "version": "v1.0"},
        "Forecast ML (sklearn)":         {"latency": 0.04, "uptime": 100,  "cost_day": 0,     "queries": 56,  "version": "v3.2"},
    }

    # ── Model Status Cards ──
    st.markdown("### Model Registry & Health")
    cols = st.columns(len(models))
    for col, (model_name, metrics) in zip(cols, models.items()):
        status_color = "🟢" if metrics["uptime"] > 99.5 else "🟡"
        col.markdown(f"""
        <div style='background:#1A1A1A;border:1px solid #8B0000;border-radius:8px;padding:12px;margin:4px 0;'>
        <div style='color:#C5A028;font-size:11px;font-weight:bold;'>{status_color} {model_name}</div>
        <div style='color:#E8E0D0;font-size:10px;margin-top:8px;'>Version: {metrics['version']}</div>
        <div style='color:#E8E0D0;font-size:10px;'>Latency: {metrics['latency']}s</div>
        <div style='color:#E8E0D0;font-size:10px;'>Uptime: {metrics['uptime']}%</div>
        <div style='color:#E8E0D0;font-size:10px;'>Queries/day: {metrics['queries']}</div>
        <div style='color:#C5A028;font-size:10px;'>Cost/day: ${metrics['cost_day']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Query Volume — Last 14 Days")
        dates  = [datetime.now() - timedelta(days=i) for i in range(14, 0, -1)]
        volume = [random.randint(120, 520) for _ in dates]
        fig = go.Figure(go.Scatter(
            x=[d.strftime("%b %d") for d in dates], y=volume,
            fill="tozeroy", line=dict(color="#8B0000", width=2),
            fillcolor="rgba(139,0,0,0.15)"
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", showlegend=False,
            yaxis_title="Queries"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Guardrail Events — Last 14 Days")
        categories = ["Input Blocked", "Output Flagged", "PII Detected", "Off-Brand Tone"]
        values     = [random.randint(0, 8) for _ in categories]
        fig = px.bar(x=categories, y=values,
                     color=values, color_continuous_scale=["#2C6B35", "#C5A028", "#8B0000"],
                     labels={"x": "Guardrail Type", "y": "Events"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### Avg Response Latency (ms) by Model")
        model_names = [m.split("(")[0].strip() for m in models.keys()]
        latencies   = [v["latency"] * 1000 for v in models.values()]
        fig = px.bar(x=model_names, y=latencies,
                     color=latencies, color_continuous_scale=["#2C6B35", "#C5A028", "#8B0000"],
                     labels={"x": "Model", "y": "Latency (ms)"})
        fig.add_hline(y=2000, line_dash="dash", line_color="#E8E0D0",
                      annotation_text="SLA Threshold", annotation_position="top right")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown("#### Daily AI Cost Breakdown (USD)")
        cost_data = {m.split("(")[0].strip(): v["cost_day"] 
                     for m, v in models.items() if v["cost_day"] > 0}
        fig = px.pie(values=list(cost_data.values()), names=list(cost_data.keys()),
                     color_discrete_sequence=["#8B0000", "#C5A028", "#2C2C2C", "#6B4E2D"],
                     hole=0.4)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C", legend=dict(font=dict(color="#1C1C1C", size=11))
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Prompt Evaluation Log ──
    st.markdown("#### Prompt Evaluation Log (Sample)")
    eval_data = pd.DataFrame({
        "Timestamp":     [datetime.now() - timedelta(hours=i*3) for i in range(8)],
        "Module":        ["CRM RAG", "Sales Insights", "Marketing", "Supply Chain",
                          "CRM RAG", "Sales Insights", "CRM RAG", "Marketing"],
        "Tokens_In":     [random.randint(800, 2400) for _ in range(8)],
        "Tokens_Out":    [random.randint(200, 800) for _ in range(8)],
        "Latency_s":     [round(random.uniform(0.8, 2.4), 2) for _ in range(8)],
        "Guardrail_Pass":[True, True, True, True, False, True, True, True],
        "Quality_Score": [round(random.uniform(7.5, 9.8), 1) for _ in range(8)],
    })
    eval_data["Timestamp"] = eval_data["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    eval_data["Cost_USD"]  = (eval_data["Tokens_In"] * 0.000005 + 
                               eval_data["Tokens_Out"] * 0.000015).round(4)
    
    st.dataframe(
        eval_data.style
        .apply(lambda x: ["background-color: #8B000033" if not v else "" 
                           for v in x], subset=["Guardrail_Pass"])
        .format({"Cost_USD": "${:.4f}", "Quality_Score": "{:.1f}"}),
        use_container_width=True, height=280
    )

    # ── Architecture Overview ──
    st.markdown("---")
    st.markdown("#### 🏗️ GenAI Platform Architecture")
    arch_md = """
    ```
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    CARTIER APAC AI PLATFORM                         │
    │                                                                     │
    │  ┌──────────────┐   ┌────────────────┐   ┌─────────────────────┐  │
    │  │  Streamlit   │   │   LangChain    │   │   FAISS Vector DB   │  │
    │  │  Frontend    │──▶│  Orchestration │──▶│   (RAG Retrieval)   │  │
    │  └──────────────┘   └────────────────┘   └─────────────────────┘  │
    │          │                   │                       │             │
    │          │           ┌───────▼────────┐              │             │
    │          │           │  Guardrails    │              │             │
    │          │           │  - Input check │              │             │
    │          │           │  - PII filter  │              │             │
    │          │           │  - Brand safe  │              │             │
    │          │           └───────┬────────┘              │             │
    │          │                   │                       │             │
    │          │           ┌───────▼────────┐    ┌────────▼──────────┐ │
    │          └──────────▶│  OpenAI GPT-4o │    │  Embeddings API   │ │
    │                      │  (Completions) │    │  text-embed-3-sm  │ │
    │                      └───────┬────────┘    └───────────────────┘ │
    │                              │                                     │
    │                      ┌───────▼────────┐                           │
    │                      │   LLMOps Mon.  │                           │
    │                      │  - Latency     │                           │
    │                      │  - Cost track  │                           │
    │                      │  - Eval scores │                           │
    │                      └────────────────┘                           │
    └─────────────────────────────────────────────────────────────────────┘
    ```
    """
    st.markdown(arch_md)