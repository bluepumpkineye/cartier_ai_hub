import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.llm_client import chat_completion, get_available_free_models, DEFAULT_MODEL

# ── Page Configuration ─────────────────────────────────────────
st.set_page_config(
    page_title="Cartier APAC Intelligence Hub",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Cartier APAC AI Intelligence Platform — Internal Use Only"}
)

# ── Brand CSS ──────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap');

    /* ══════════════════════════════════════════════
       GLOBAL
    ══════════════════════════════════════════════ */
    html, body, [class*="css"], .stApp {
        font-family: 'Jost', sans-serif !important;
        background-color: #FAF8F5 !important;
        color: #1C1C1C !important;
    }
    .stApp {
        background-color: #FAF8F5 !important;
    }
    .main .block-container {
        background-color: #FAF8F5 !important;
        padding-top: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 1400px !important;
    }

    /* ══════════════════════════════════════════════
       SIDEBAR — background and border
    ══════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E8E0D0 !important;
        box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stSidebar"] > div {
        background-color: #FFFFFF !important;
    }

    /* ── Sidebar: force ALL text dark ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #1C1C1C !important;
    }

    /* ══════════════════════════════════════════════
       SIDEBAR NAVIGATION — Radio buttons
       Fix: alignment, font size, remove bullet offset
    ══════════════════════════════════════════════ */

    /* Hide the default radio circle dots */
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* Radio container — remove gap causing misalignment */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0 !important;
        flex-direction: column !important;
    }

    /* Each radio option wrapper */
    [data-testid="stSidebar"] .stRadio label {
        display: flex !important;
        align-items: center !important;
        gap: 0 !important;
        padding: 10px 16px !important;
        margin: 0 !important;
        border-left: 2px solid transparent !important;
        border-radius: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        background: transparent !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: #FAF8F5 !important;
        border-left-color: #C5A028 !important;
    }

    /* The radio circle — hide it completely */
    [data-testid="stSidebar"] .stRadio label > div:first-child {
        display: none !important;
    }

    /* The text inside the radio label */
    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio label span {
        font-family: 'Jost', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #1C1C1C !important;
        letter-spacing: 0.2px !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
    }

    /* Selected nav item */
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio label[aria-checked="true"] {
        background-color: #FAF8F5 !important;
        border-left-color: #C5A028 !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] p,
    [data-testid="stSidebar"] .stRadio label[aria-checked="true"] p {
        color: #8B0000 !important;
        font-weight: 600 !important;
    }

    /* ══════════════════════════════════════════════
       SIDEBAR — System Status
       Fix: overlapping text at bottom
    ══════════════════════════════════════════════ */
    [data-testid="stSidebar"] .stMarkdown {
        overflow: visible !important;
        line-height: 1.6 !important;
    }

    /* ── Sidebar selectbox ── */
    [data-testid="stSidebar"] .stSelectbox label {
        font-size: 10px !important;
        color: #AAAAAA !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-family: 'Jost', sans-serif !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #FAF8F5 !important;
        border: 1px solid #E8E0D0 !important;
        border-radius: 0 !important;
        color: #1C1C1C !important;
        font-size: 12px !important;
        font-family: 'Jost', sans-serif !important;
    }
    [data-testid="stSidebar"] .stSelectbox svg {
        color: #1C1C1C !important;
        fill: #1C1C1C !important;
    }

    /* ══════════════════════════════════════════════
       TYPOGRAPHY
    ══════════════════════════════════════════════ */
    h1 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 2.8rem !important;
        font-weight: 300 !important;
        color: #1C1C1C !important;
        letter-spacing: 6px !important;
        text-transform: uppercase !important;
    }
    h2 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        color: #1C1C1C !important;
        letter-spacing: 2px !important;
        border-bottom: 1px solid #E8E0D0 !important;
        padding-bottom: 10px !important;
        margin-bottom: 20px !important;
    }
    h3 {
        font-family: 'Jost', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #888888 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }
    h4 {
        font-family: 'Jost', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #1C1C1C !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        margin-bottom: 12px !important;
    }
    p, li {
        font-family: 'Jost', sans-serif !important;
        color: #1C1C1C !important;
        font-size: 14px !important;
    }

    /* ══════════════════════════════════════════════
       METRIC CARDS
    ══════════════════════════════════════════════ */
    [data-testid="metric-container"] {
        background: #FFFFFF !important;
        border: none !important;
        border-top: 2px solid #E8E0D0 !important;
        border-radius: 0 !important;
        padding: 20px 16px 16px 0 !important;
        box-shadow: none !important;
    }
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        font-family: 'Jost', sans-serif !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        color: #888888 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 2.2rem !important;
        font-weight: 300 !important;
        color: #1C1C1C !important;
        line-height: 1.1 !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'Jost', sans-serif !important;
        font-size: 11px !important;
        color: #888 !important;
    }

    /* ══════════════════════════════════════════════
       BUTTONS
       Fix: black button with unreadable text
    ══════════════════════════════════════════════ */

    /* ALL buttons — base reset */
    .stButton > button {
        font-family: 'Jost', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 0 !important;
        padding: 12px 28px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }

    /* Primary button — dark background, light text */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #1C1C1C !important;
        color: #FAF8F5 !important;
        border: 1px solid #1C1C1C !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #8B0000 !important;
        border-color: #8B0000 !important;
        color: #FFFFFF !important;
    }

    /* Secondary / default button — light background, dark text */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
        background-color: #FFFFFF !important;
        color: #1C1C1C !important;
        border: 1px solid #1C1C1C !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover {
        background-color: #1C1C1C !important;
        color: #FFFFFF !important;
    }

    /* ══════════════════════════════════════════════
       FORM INPUTS — Text areas, text inputs
    ══════════════════════════════════════════════ */
    .stTextArea textarea,
    .stTextInput input {
        background: #FFFFFF !important;
        color: #1C1C1C !important;
        border: 1px solid #E8E0D0 !important;
        border-radius: 0 !important;
        font-family: 'Jost', sans-serif !important;
        font-size: 14px !important;
    }
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #C5A028 !important;
        box-shadow: 0 0 0 1px #C5A02833 !important;
    }

    /* ══════════════════════════════════════════════
       SELECTBOX — Fix black boxes with unreadable text
    ══════════════════════════════════════════════ */
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #1C1C1C !important;
        border: 1px solid #E8E0D0 !important;
        border-radius: 0 !important;
        font-family: 'Jost', sans-serif !important;
        font-size: 13px !important;
    }
    /* The dropdown option list */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1C1C1C !important;
    }
    /* Dropdown arrow icon */
    .stSelectbox svg {
        color: #1C1C1C !important;
        fill: #1C1C1C !important;
    }
    /* Selected value text */
    .stSelectbox [data-baseweb="select"] span {
        color: #1C1C1C !important;
        font-family: 'Jost', sans-serif !important;
        font-size: 13px !important;
    }
    /* Labels above selectboxes */
    .stSelectbox label {
        font-family: 'Jost', sans-serif !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        color: #888 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }

    /* ══════════════════════════════════════════════
       MULTISELECT — Fix black tag boxes
    ══════════════════════════════════════════════ */
    .stMultiSelect > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E0D0 !important;
        border-radius: 0 !important;
        color: #1C1C1C !important;
    }
    /* The input area */
    .stMultiSelect [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1C1C1C !important;
    }
    /* Selected tags (the black boxes with text) */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #F0EBE0 !important;
        color: #1C1C1C !important;
        border: 1px solid #E8E0D0 !important;
        border-radius: 2px !important;
        font-family: 'Jost', sans-serif !important;
        font-size: 11px !important;
        font-weight: 500 !important;
    }
    /* Tag text */
    .stMultiSelect [data-baseweb="tag"] span {
        color: #1C1C1C !important;
    }
    /* Tag close (X) button */
    .stMultiSelect [data-baseweb="tag"] [role="presentation"] {
        color: #888 !important;
    }
    /* Placeholder text */
    .stMultiSelect [data-baseweb="select"] input::placeholder {
        color: #AAAAAA !important;
        font-family: 'Jost', sans-serif !important;
    }
    /* Labels above multiselect */
    .stMultiSelect label {
        font-family: 'Jost', sans-serif !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        color: #888 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }
    /* Dropdown popover menu */
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    [data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    [data-baseweb="menu"] li {
        color: #1C1C1C !important;
        font-family: 'Jost', sans-serif !important;
        font-size: 13px !important;
        background-color: #FFFFFF !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #FAF8F5 !important;
    }
    /* Slider label */
    .stSlider label {
        font-family: 'Jost', sans-serif !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        color: #888 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }
    .stSlider [data-testid="stTickBar"] {
        color: #888 !important;
    }

    /* ══════════════════════════════════════════════
       TABS
    ══════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #E8E0D0 !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Jost', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        color: #888 !important;
        padding: 12px 20px !important;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1C1C1C !important;
        border-bottom: 2px solid #C5A028 !important;
        background: transparent !important;
    }

    /* ══════════════════════════════════════════════
       EXPANDERS
    ══════════════════════════════════════════════ */
    [data-testid="stExpander"] {
        border: 1px solid #E8E0D0 !important;
        border-radius: 0 !important;
        background: #FFFFFF !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'Jost', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        color: #1C1C1C !important;
        background: #FFFFFF !important;
        padding: 12px 16px !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: #FAF8F5 !important;
    }
    [data-testid="stExpander"] > div > div {
        background: #FDFCFA !important;
        padding: 16px !important;
    }

    /* ══════════════════════════════════════════════
       DATAFRAME
    ══════════════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border: 1px solid #E8E0D0 !important;
    }
    [data-testid="stDataFrame"] th {
        background: #F5F2EE !important;
        color: #888 !important;
        font-size: 10px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 600 !important;
    }

    /* ══════════════════════════════════════════════
       ALERTS
    ══════════════════════════════════════════════ */
    [data-testid="stAlert"],
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 0 !important;
        font-family: 'Jost', sans-serif !important;
        font-size: 13px !important;
    }
    .stSuccess {
        background: #F5FAF5 !important;
        border-color: #7BAE7F !important;
        color: #1C1C1C !important;
    }
    .stWarning {
        background: #FAF8F0 !important;
        border-color: #C5A028 !important;
        color: #1C1C1C !important;
    }
    .stError {
        background: #FAF0F0 !important;
        border-color: #8B0000 !important;
        color: #1C1C1C !important;
    }

    /* ══════════════════════════════════════════════
       MISC
    ══════════════════════════════════════════════ */
    hr { border-color: #E8E0D0 !important; margin: 24px 0 !important; }

    .stCaption {
        font-family: 'Jost', sans-serif !important;
        color: #AAAAAA !important;
        font-size: 11px !important;
    }

    .js-plotly-plot, .plotly, .plot-container {
        background: transparent !important;
    }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #FAF8F5; }
    ::-webkit-scrollbar-thumb { background: #C5A028; border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)


inject_css()

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    # ── Brand Header ──
    st.markdown("""
    <div style='padding: 28px 20px 20px 20px;
                border-bottom: 1px solid #E8E0D0;
                margin-bottom: 8px;'>
        <div style='font-family:"Cormorant Garamond",serif;
                    font-size: 18px;
                    color: #1C1C1C;
                    letter-spacing: 6px;
                    font-weight: 400;
                    text-transform: uppercase;'>
            Cartier
        </div>
        <div style='font-family:"Jost",sans-serif;
                    font-size: 9px;
                    color: #AAAAAA;
                    letter-spacing: 3px;
                    text-transform: uppercase;
                    margin-top: 4px;'>
            APAC Intelligence Hub
        </div>
        <div style='width: 24px;
                    height: 1px;
                    background: #C5A028;
                    margin-top: 14px;'>
        </div>
        <div style='font-family:"Jost",sans-serif;
                    font-size: 9px;
                    color: #CCCCCC;
                    letter-spacing: 1px;
                    margin-top: 10px;'>
            Internal Use Only · Confidential
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigation ──
    pages = {
        "Executive Dashboard":       "dashboard",
        "CRM & RAG Assistant":       "crm",
        "Sales & Revenue Analytics": "sales",
        "Marketing Intelligence":    "marketing",
        "Demand & Supply Planning":  "supply",
        "LLMOps & Model Monitor":    "llmops",
        "Prompt Laboratory":         "prompt",
    }

    selected = st.radio(
        "Navigation",
        list(pages.keys()),
        label_visibility="collapsed"
    )
    page = pages[selected]

    st.markdown("""
    <div style='height:1px;background:#E8E0D0;margin:12px 0;'></div>
    """, unsafe_allow_html=True)

    # ── Model Selector ──
    st.markdown("""
    <div style='font-family:"Jost",sans-serif;
                font-size: 9px;
                color: #AAAAAA;
                text-transform: uppercase;
                letter-spacing: 2px;
                padding: 8px 16px 6px 16px;'>
        AI Model Selection
    </div>
    """, unsafe_allow_html=True)

    free_models         = get_available_free_models()
    model_display_names = list(free_models.keys())

    selected_model_name = st.selectbox(
        "Active Model",
        model_display_names,
        index=0,
        help="All models are free via OpenRouter",
        label_visibility="collapsed"
    )
    st.session_state["active_model"] = free_models[selected_model_name]

    st.markdown(
        f'<div style="font-family:\'Jost\',sans-serif;font-size:10px;'
        f'color:#AAAAAA;padding:2px 16px 8px 16px;">'
        f'Free tier · OpenRouter</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style='height:1px;background:#E8E0D0;margin:4px 0 12px 0;'></div>
    """, unsafe_allow_html=True)

    # ── System Status ──
    # NOTE: Using st.markdown with simple block layout (no absolute positioning)
    # This fixes the overlapping text issue
    st.markdown("""
    <div style='font-family:"Jost",sans-serif;
                font-size: 9px;
                color: #AAAAAA;
                text-transform: uppercase;
                letter-spacing: 2px;
                padding: 0 16px 10px 16px;'>
        System Status
    </div>
    """, unsafe_allow_html=True)

    status_items = [
        ("LLM API",       "Operational", "#7BAE7F"),
        ("Vector Store",  "Operational", "#7BAE7F"),
        ("Data Pipeline", "Operational", "#7BAE7F"),
        ("Guardrails",    "Active",      "#C5A028"),
    ]
    for name, status, color in status_items:
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:center;'
            f'font-size:12px;'
            f'padding:5px 16px;'
            f'font-family:\'Jost\',sans-serif;'
            f'line-height:1.8;">'
            f'<span style="color:#555555;">{name}</span>'
            f'<span style="color:{color};font-size:11px;">● {status}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("""
    <div style='height:1px;background:#E8E0D0;margin:12px 0;'></div>
    """, unsafe_allow_html=True)

    # ── Footer — normal flow (not absolute) ──
    st.markdown("""
    <div style='font-family:"Jost",sans-serif;
                font-size:10px;
                color:#CCCCCC;
                padding: 0 16px;
                line-height: 2;'>
        Platform v2.4 · GenAI Stack<br>
        OpenRouter · LangChain · FAISS
    </div>
    """, unsafe_allow_html=True)


# ── Executive Dashboard ────────────────────────────────────────
def render_dashboard():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 32px 0;
                border-bottom: 1px solid #E8E0D0; margin-bottom: 36px;'>
        <div style='font-family:"Cormorant Garamond",serif;
                    font-size: 13px;
                    color: #AAAAAA;
                    letter-spacing: 5px;
                    text-transform: uppercase;
                    margin-bottom: 12px;
                    font-weight: 400;'>
            Asia Pacific
        </div>
        <div style='font-family:"Cormorant Garamond",serif;
                    font-size: 42px;
                    color: #1C1C1C;
                    letter-spacing: 10px;
                    font-weight: 300;
                    text-transform: uppercase;
                    line-height: 1;'>
            Cartier APAC
        </div>
        <div style='width: 40px;
                    height: 1px;
                    background: #C5A028;
                    margin: 18px auto;'>
        </div>
        <div style='font-family:"Jost",sans-serif;
                    font-size: 10px;
                    color: #AAAAAA;
                    letter-spacing: 4px;
                    text-transform: uppercase;'>
            Executive Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load Data ──
    try:
        kpis     = json.load(open("data/kpis.json"))
        sales_df = pd.read_csv("data/sales_data.csv")
        crm_df   = pd.read_csv("data/crm_data.csv")
    except FileNotFoundError:
        st.error("⚠️ Data files not found. Please run: python data/generate_data.py")
        st.code("python data/generate_data.py", language="bash")
        return

    # ── KPI Row 1 ──
    st.markdown("### Key Performance Indicators · YTD 2024")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(
        "YTD Revenue",
        f"${kpis['total_revenue_ytd_usd']/1e6:.0f}M",
        delta=f"+{kpis['revenue_vs_target_pct']}% vs target"
    )
    k2.metric("Gross Margin",  f"{kpis['gross_margin_pct']}%")
    k3.metric("APAC Clients",  f"{kpis['total_clients_apac']:,}")
    k4.metric("NPS Score",     f"{kpis['nps_score']}")
    k5.metric(
        "Digital Share",
        f"{kpis['digital_revenue_share_pct']}%",
        delta=f"+{kpis['travel_retail_growth_pct']}% Travel Retail"
    )

    st.markdown("---")

    # ── KPI Row 2 ──
    k6, k7, k8, k9 = st.columns(4)
    k6.metric("New Clients YTD",  f"{kpis['new_clients_ytd']:,}")
    k7.metric("VIP Clients",      f"{kpis['vip_clients']:,}")
    k8.metric("Avg Transaction",  f"${kpis['avg_transaction_value_usd']:,}")
    k9.metric(
        "Client Retention",
        f"{kpis['client_retention_rate']*100:.1f}%"
    )

    st.markdown("---")

    # ── Charts Row 1 ──
    COLORS =["#8B0000", "#C5A028", "#9B8B6E", "#D4C5A9", "#4A3728", "#C5A028"]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### Revenue by Market")
        mkt = (
            sales_df.groupby("market")["revenue_usd"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig = px.bar(
            mkt, x="market", y="revenue_usd",
            color="market",
            color_discrete_sequence=COLORS,
            labels={"revenue_usd": "Revenue (USD)", "market": ""}
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C",
            showlegend=False,
            yaxis_tickformat="$,.0f",
            xaxis_tickangle=-35,
            height=300,
            margin=dict(t=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Revenue by Category")
        cat = sales_df.groupby("category")["revenue_usd"].sum().reset_index()
        fig = px.pie(
            cat, values="revenue_usd", names="category",
            color_discrete_sequence=COLORS,
            hole=0.5
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C",
            height=300,
            margin=dict(t=10),
            legend=dict(font=dict(size=10, color="#E8E0D0"))
        )
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        st.markdown("#### Client Segment Mix")
        seg = crm_df.groupby("segment").size().reset_index(name="count")
        fig = px.pie(
            seg, values="count", names="segment",
            color_discrete_sequence=COLORS,
            hole=0.5
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1C1C1C",
            height=300,
            margin=dict(t=10),
            legend=dict(font=dict(size=10, color="#E8E0D0"))
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Revenue Trend ──
    st.markdown("#### Monthly Revenue Trend · All APAC")
    sales_df["date"] = pd.to_datetime(sales_df["date"])
    trend = (
        sales_df.groupby(sales_df["date"].dt.to_period("M"))["revenue_usd"]
        .sum()
        .reset_index()
    )
    trend["date"] = trend["date"].astype(str)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["date"],
        y=trend["revenue_usd"],
        fill="tozeroy",
        name="Revenue",
        line=dict(color="#8B0000", width=2.5),
        fillcolor="rgba(139,0,0,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=trend["date"],
        y=[kpis["total_revenue_ytd_usd"] / len(trend) * 1.05] * len(trend),
        name="Target Line",
        line=dict(color="#C5A028", width=1.5, dash="dot")
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#1C1C1C",
        yaxis_tickformat="$,.0f",
        legend=dict(font=dict(color="#1C1C1C", size=11)),
        height=280,
        margin=dict(t=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── AI Morning Brief ──
    st.markdown("---")
    st.markdown("### 🤖 AI Executive Briefing")

    if st.button("Generate Morning Intelligence Brief", type="primary"):
        active_model = st.session_state.get("active_model", DEFAULT_MODEL)
        summary = f"""
        YTD Revenue: ${kpis['total_revenue_ytd_usd']/1e6:.0f}M
        vs Target: +{kpis['revenue_vs_target_pct']}%
        Top Market: {kpis['top_market']}
        Top Category: {kpis['top_category']}
        NPS: {kpis['nps_score']}
        Client Retention: {kpis['client_retention_rate']*100:.1f}%
        Digital Revenue Share: {kpis['digital_revenue_share_pct']}%
        VIP Clients: {kpis['vip_clients']:,} of {kpis['total_clients_apac']:,} total
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Chief AI Officer for Cartier APAC. "
                    "Generate a crisp executive morning intelligence brief in 3 paragraphs: "
                    "(1) Performance Headline, (2) Key Opportunities, (3) Risk Watch. "
                    "Use sophisticated business language befitting the Maison. Max 200 words."
                )
            },
            {
                "role": "user",
                "content": f"APAC Performance Data:\n{summary}"
            }
        ]

        with st.spinner("Generating executive brief..."):
            brief = chat_completion(
                messages,
                model=active_model,
                temperature=0.35,
                max_tokens=400
            )

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1A1A1A,#141414);
                    border:1px solid #C5A028;border-radius:8px;
                    padding:24px;margin-top:12px;'>
            <div style='font-family:"Playfair Display",serif;color:#C5A028;
                        font-size:14px;margin-bottom:16px;letter-spacing:2px;'>
                ◆ MORNING INTELLIGENCE BRIEF
            </div>
            <div style='color:#E8E0D0;line-height:1.8;font-size:14px;'>
                {brief}
            </div>
            <div style='color:#555;font-size:10px;margin-top:16px;letter-spacing:1px;'>
                AI-GENERATED · CONFIDENTIAL · FOR INTERNAL USE ONLY
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Page Routing ───────────────────────────────────────────────
if page == "dashboard":
    render_dashboard()

elif page == "crm":
    from modules.crm_rag import render_crm_rag
    render_crm_rag()

elif page == "sales":
    from modules.sales_analytics import render_sales_analytics
    render_sales_analytics()

elif page == "marketing":
    from modules.marketing_budget import render_marketing_budget
    render_marketing_budget()

elif page == "supply":
    from modules.demand_planning import render_demand_planning
    render_demand_planning()

elif page == "llmops":
    from modules.llmops_monitor import render_llmops
    render_llmops()

elif page == "prompt":
    from modules.prompt_lab import render_prompt_lab
    render_prompt_lab()