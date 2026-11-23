import numpy as np
import pandas as pd
import yfinance as yf
import warnings
import time
import json
import streamlit as st
from datetime import datetime, timedelta
import pytz

import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# PLOTLY TEMPLATE
# ─────────────────────────────────────────────────────────
PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "#0B0F14",
    "font": {"family": "Inter, -apple-system, sans-serif",
             "color": "#E5E7EB", "size": 11},
    "xaxis": {"gridcolor": "#1F2937", "gridwidth": 0.5,
              "linecolor": "#1F2937", "zeroline": False,
              "tickfont": {"family": "JetBrains Mono, monospace",
                           "color": "#9CA3AF", "size": 10},
              "showspikes": False},
    "yaxis": {"gridcolor": "#1F2937", "gridwidth": 0.5,
              "linecolor": "#1F2937", "zeroline": False,
              "tickfont": {"family": "JetBrains Mono, monospace",
                           "color": "#9CA3AF", "size": 10},
              "showspikes": False},
    "hoverlabel": {"bgcolor": "#172030", "bordercolor": "#1F2937",
                   "font": {"family": "JetBrains Mono, monospace",
                            "color": "#E5E7EB", "size": 11}},
    "legend": {"bgcolor": "rgba(0,0,0,0)", "bordercolor": "#1F2937",
               "font": {"family": "Inter, sans-serif",
                        "color": "#9CA3AF", "size": 10}},
    "margin": {"l": 10, "r": 10, "t": 20, "b": 10},
    "showlegend": False,
    "hovermode": "x unified",
    "dragmode": "pan",
}

CANDLE_UP = "#22C55E"
CANDLE_DOWN = "#EF4444"
EMA_PRIMARY = "#00D1B2"
EMA_SECONDARY = "#C9A227"
SIGNAL_MARKER = "#C9A227"
L1_LINE_COLOR = "#F59E0B"

# ─────────────────────────────────────────────────────────
# BRANDING + MAPPING
# ─────────────────────────────────────────────────────────
BRAND_NAME = "FINTRIX ANALYTICS"
BRAND_TAG = "INSTITUTIONAL SIGNAL INTELLIGENCE"

QUOTES = [
    "In institutional finance, survival isn't luck—it is mathematical design.",
    "If you cannot identify where institutional liquidity sits, you are the liquidity.",
    "Retail traders react to price. Institutions engineer liquidity.",
    "Skillful risk control is the mark of the superior investor.",
]

LEVEL_LABEL = {"15m": "Level 1", "30m": "Level 2", "45m": "Level 3", "60m": "Level 4"}
LEVEL_ORDER = ["15m", "30m", "45m", "60m"]

TIER_COLORS = {"S": "#C9A227", "A": "#22C55E", "B": "#00D1B2", "C": "#9CA3AF"}

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fintrix Analytics · Signal Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
# INSTITUTIONAL CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-app:       #0B0F14;
    --bg-panel:     #121821;
    --bg-elevated:  #172030;
    --border:       #1F2937;
    --accent-teal:  #00D1B2;
    --accent-gold:  #C9A227;
    --bullish:      #22C55E;
    --bearish:      #EF4444;
    --warning:      #F59E0B;
    --text-primary: #E5E7EB;
    --text-muted:   #9CA3AF;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp { background: var(--bg-app); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px; }

.section-label {
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--text-muted);
    margin-bottom: 12px;
}

.land-wrap {
    max-width: 900px; margin: 80px auto 60px;
    text-align: center; padding: 0 24px;
}
.land-eyebrow {
    font-size: 11px; font-weight: 600; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--accent-gold);
    margin-bottom: 20px;
}
.land-title {
    font-size: 3.6rem; font-weight: 700; line-height: 1.05;
    color: var(--text-primary); margin: 0 0 8px 0;
    letter-spacing: -0.02em;
}
.land-title::after {
    content: ''; display: block; width: 64px; height: 2px;
    background: var(--accent-gold); margin: 20px auto 0;
}
.land-tagline {
    font-size: 1.05rem; color: var(--text-muted);
    font-weight: 500; letter-spacing: 0.04em;
    margin: 24px 0 12px 0;
}
.land-sub {
    color: var(--text-muted); font-size: 0.95rem; line-height: 1.7;
    max-width: 620px; margin: 0 auto;
}
.land-stats {
    display: flex; gap: 1px; justify-content: center;
    margin: 48px auto 0; flex-wrap: wrap;
    border: 1px solid var(--border); border-radius: 8px;
    overflow: hidden; background: var(--border);
    max-width: 560px;
}
.land-stat { background: var(--bg-panel); padding: 20px 40px; flex: 1; min-width: 150px; }
.land-stat .num {
    color: var(--text-primary); font-family: 'JetBrains Mono', monospace;
    font-size: 1.7rem; font-weight: 600; line-height: 1;
}
.land-stat .lbl {
    color: var(--text-muted); font-size: 10px; margin-top: 8px;
    letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600;
}
.land-features {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 1px; margin-top: 48px; text-align: left;
    background: var(--border); border: 1px solid var(--border);
    border-radius: 8px; overflow: hidden;
}
.land-feature { background: var(--bg-panel); padding: 24px; }
.land-feature h4 {
    color: var(--text-primary); font-size: 0.88rem;
    margin: 0 0 8px 0; font-weight: 600;
}
.land-feature p {
    color: var(--text-muted); font-size: 0.82rem;
    margin: 0; line-height: 1.6;
}

.hero-wrap {
    background: linear-gradient(180deg, #121821 0%, #0E131A 100%);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 24px 28px; margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
}
.hero-eyebrow {
    font-size: 10px; font-weight: 600; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--accent-gold);
    margin-bottom: 8px;
}
.hero-title {
    font-size: 22px; font-weight: 600;
    color: var(--text-primary); margin: 0 0 6px 0;
    letter-spacing: -0.005em; line-height: 1.3;
}
.hero-title::after {
    content: ''; display: block; width: 48px; height: 1px;
    background: var(--accent-gold); margin-top: 10px;
}
.hero-sub {
    color: var(--text-muted); font-size: 12px;
    margin: 12px 0 0 0; letter-spacing: 0.02em;
}
.hero-quote {
    margin: 16px 0 0 0; padding-top: 14px;
    border-top: 1px solid var(--border);
    font-size: 12px; font-style: italic;
    color: var(--accent-gold);
    letter-spacing: 0.02em; line-height: 1.55;
    opacity: 0.92;
}
.status-pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 5px 12px; border-radius: 4px;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    margin-top: 14px;
}
.status-live {
    background: rgba(34, 197, 94, 0.1); color: var(--bullish);
    border: 1px solid rgba(34, 197, 94, 0.35);
}
.status-closed {
    background: rgba(245, 158, 11, 0.08); color: var(--warning);
    border: 1px solid rgba(245, 158, 11, 0.35);
}
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot-live { background: var(--bullish); box-shadow: 0 0 6px var(--bullish); }
.dot-closed { background: var(--warning); }

.control-card {
    background: var(--bg-panel);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 22px 26px; margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
}
.control-title {
    color: var(--text-muted); font-size: 11px; letter-spacing: 0.08em;
    font-weight: 600; text-transform: uppercase;
    margin-bottom: 18px; padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

[data-testid="stMetric"] {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-top: 1px solid var(--border);
    border-radius: 8px; padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
    transition: border-top-color 150ms ease, box-shadow 150ms ease;
}
[data-testid="stMetric"]:hover {
    border-top-color: var(--accent-teal);
    box-shadow: 0 1px 6px rgba(0, 209, 178, 0.1);
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 1.6rem !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important; font-weight: 500 !important;
}

.stButton > button {
    border-radius: 6px; font-weight: 600; font-size: 12px;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 0.65rem 1.2rem;
    transition: all 150ms ease;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-primary) !important;
}
.stButton > button:hover {
    border-color: var(--accent-teal);
    color: var(--accent-teal) !important;
    background: rgba(0, 209, 178, 0.04);
}
.stButton > button[kind="primary"] {
    background: var(--accent-teal);
    color: #0B0F14 !important;
    border: 1px solid var(--accent-teal);
    font-weight: 700;
}
.stButton > button[kind="primary"]:hover {
    background: #00E5C4;
    border-color: #00E5C4;
    color: #0B0F14 !important;
    box-shadow: 0 0 20px rgba(0, 209, 178, 0.35);
}
.stDownloadButton > button {
    border-radius: 6px; font-weight: 600; font-size: 12px;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 0.65rem 1.2rem;
    background: transparent;
    color: var(--accent-teal) !important;
    border: 1px solid var(--accent-teal);
}
.stDownloadButton > button:hover {
    background: rgba(0, 209, 178, 0.08);
    box-shadow: 0 0 16px rgba(0, 209, 178, 0.2);
}

.stSelectbox label, .stMultiSelect label,
.stSlider label, .stRadio label, .stTextInput label {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    font-size: 11px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
[data-baseweb="select"] > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent-teal) !important;
    box-shadow: 0 0 0 2px rgba(0, 209, 178, 0.15) !important;
}
[data-baseweb="tag"] {
    background: rgba(0, 209, 178, 0.15) !important;
    color: var(--accent-teal) !important;
    border: 1px solid rgba(0, 209, 178, 0.3) !important;
}
[data-baseweb="tag"] span { color: var(--accent-teal) !important; }
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--accent-teal) !important;
    border: 2px solid var(--bg-panel) !important;
    box-shadow: 0 0 0 1px var(--accent-teal) !important;
}
.stRadio [role="radiogroup"] label {
    text-transform: none !important; letter-spacing: 0 !important;
    font-size: 13px !important;
    color: var(--text-primary) !important;
}
.stRadio [role="radiogroup"] label[data-checked="true"] {
    color: var(--accent-teal) !important;
}
.stCheckbox label {
    color: var(--text-primary) !important;
    font-size: 13px !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0; border-bottom: 1px solid var(--border);
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted); font-weight: 600;
    font-size: 11px; letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 12px 20px;
    border-bottom: 2px solid transparent;
    transition: color 150ms ease, border-color 150ms ease;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); }
.stTabs [aria-selected="true"] {
    color: var(--accent-teal) !important;
    border-bottom: 2px solid var(--accent-teal) !important;
    background: transparent !important;
}

h2, h3, h4 {
    color: var(--text-primary) !important;
    letter-spacing: -0.01em; font-weight: 600 !important;
}
h2 { font-size: 16px !important; margin-top: 1.4rem !important;
     padding-bottom: 10px; border-bottom: 1px solid var(--border); }
h3 { font-size: 14px !important; }
h4 { font-size: 13px !important; }

[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: var(--bg-panel) !important;
}
[data-testid="stDataFrame"] [role="columnheader"] {
    background: var(--bg-elevated) !important;
    color: var(--text-muted) !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 10px 12px !important;
}
[data-testid="stDataFrame"] [role="gridcell"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: var(--text-primary) !important;
    padding: 8px 12px !important;
    border-bottom: 1px solid rgba(31, 41, 55, 0.5) !important;
}
[data-testid="stDataFrame"] [role="row"]:nth-child(even) [role="gridcell"] {
    background: #0F141C !important;
}
[data-testid="stDataFrame"] [role="row"]:nth-child(odd) [role="gridcell"] {
    background: var(--bg-panel) !important;
}
[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {
    background: var(--bg-elevated) !important;
}

div[data-testid="stAlert"] {
    border-radius: 6px;
    border: 1px solid var(--border);
    border-left-width: 3px;
    background: var(--bg-panel);
}
div[data-testid="stAlert"] p {
    color: var(--text-primary) !important;
    font-size: 13px !important;
    line-height: 1.6;
}

.stProgress > div > div > div > div { background: var(--accent-teal) !important; }
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 11px !important;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-app); }
::-webkit-scrollbar-thumb {
    background: #334155; border-radius: 4px;
    transition: background 150ms ease;
}
::-webkit-scrollbar-thumb:hover { background: var(--accent-teal); }

.fintrix-footer {
    text-align: center; margin-top: 56px;
    padding: 32px 20px 16px;
    border-top: 1px solid var(--border);
}
.fintrix-footer .brand {
    font-size: 12px; font-weight: 700;
    letter-spacing: 0.20em; text-transform: uppercase;
    color: var(--accent-gold); margin-bottom: 6px;
}
.fintrix-footer .tag {
    color: var(--text-muted); font-size: 10px;
    letter-spacing: 0.16em; text-transform: uppercase;
    font-weight: 500;
}

@media (max-width: 768px) {
    .block-container { padding-left: 0.85rem; padding-right: 0.85rem; padding-top: 1rem; }
    .land-wrap { margin: 40px auto 30px; padding: 0 16px; }
    .land-title { font-size: 2.2rem !important; }
    .land-title::after { margin-top: 14px; width: 44px; }
    .land-tagline { font-size: 0.9rem !important; margin: 20px 0 10px 0; }
    .land-sub { font-size: 0.85rem !important; line-height: 1.6 !important; }
    .land-eyebrow { font-size: 10px !important; margin-bottom: 16px; }
    .land-stats { margin-top: 32px; max-width: 100%; }
    .land-stat { padding: 16px 20px; min-width: 100px; }
    .land-stat .num { font-size: 1.4rem; }
    .land-stat .lbl { font-size: 9px; }
    .land-features { grid-template-columns: 1fr; margin-top: 32px; }
    .land-feature { padding: 18px; }
    .hero-wrap { padding: 18px 20px !important; }
    .hero-title { font-size: 18px !important; }
    .hero-eyebrow { font-size: 9px !important; }
    .hero-sub { font-size: 11px !important; }
    .hero-quote { font-size: 11px !important; padding-top: 12px !important; }
    .status-pill { font-size: 9px !important; padding: 4px 10px !important; }
    .control-card { padding: 16px 18px !important; }
    .control-title { font-size: 10px !important; margin-bottom: 14px !important; }
    [data-testid="stMetric"] { padding: 12px 14px !important; }
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    [data-testid="stMetricLabel"] { font-size: 9px !important; }
    .stButton > button { padding: 0.7rem 1rem !important; font-size: 11px !important;
                         min-height: 42px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 10px !important; padding: 9px 10px !important; }
    h2 { font-size: 14px !important; }
    h3 { font-size: 13px !important; }
    h4 { font-size: 12px !important; }
    [data-testid="stDataFrame"] [role="gridcell"] { font-size: 11px !important; }
    .fintrix-footer { margin-top: 40px; padding-top: 24px; }
    .fintrix-footer .brand { font-size: 10px; letter-spacing: 0.16em; }
    .fintrix-footer .tag { font-size: 9px; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# INSTRUMENT UNIVERSES
# ─────────────────────────────────────────────────────────
STANDARD_SYMBOLS = [
    "AARTIIND.NS", "ABB.NS", "ABBOTINDIA.NS", "ABCAPITAL.NS", "ABFRL.NS",
    "ACC.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIENSOL.NS",
    "ADANIPOWER.NS", "ALKEM.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "APOLLOTYRE.NS",
    "ASHOKLEY.NS", "ASIANPAINT.NS", "ASTRAL.NS", "ATUL.NS", "AUBANK.NS",
    "AUROPHARMA.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS",
    "BALKRISIND.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BATAINDIA.NS",
    "BEL.NS", "BERGEPAINT.NS", "BHARATFORG.NS", "BHARTIARTL.NS", "BHEL.NS",
    "BIOCON.NS", "BOSCHLTD.NS", "BPCL.NS", "BRITANNIA.NS", "BSOFT.NS",
    "CANBK.NS", "CANFINHOME.NS", "CHAMBLFERT.NS", "CHOLAFIN.NS", "CIPLA.NS",
    "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "COROMANDEL.NS",
    "CROMPTON.NS", "CUMMINSIND.NS", "CYIENT.NS", "DABUR.NS", "DALBHARAT.NS",
    "DEEPAKNTR.NS", "DELHIVERY.NS", "DIVISLAB.NS", "DLF.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "ESCORTS.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "FORTIS.NS",
    "GAIL.NS", "GLENMARK.NS", "GMRINFRA.NS", "GODREJCP.NS", "GODREJPROP.NS",
    "GRANULES.NS", "GRASIM.NS", "GUJGASLTD.NS", "HAL.NS", "HAVELLS.NS",
    "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS",
    "HINDCOPPER.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ICICIGI.NS",
    "ICICIPRULI.NS", "IDEA.NS", "IDFCFIRSTB.NS", "IEX.NS", "IGL.NS",
    "INDHOTEL.NS", "INDIACEM.NS", "INDIAMART.NS", "INDIGO.NS", "INDUSINDBK.NS",
    "INDUSTOWER.NS", "INFY.NS", "IOC.NS", "IPCALAB.NS", "IRCTC.NS",
    "IRFC.NS", "ITC.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JKCEMENT.NS",
    "JSWENERGY.NS", "JSWSTEEL.NS", "JUBLFOOD.NS", "KALYANKJIL.NS", "KEI.NS",
    "KFINTECH.NS", "KOTAKBANK.NS", "KPITTECH.NS", "LALPATHLAB.NS", "LICHSGFIN.NS",
    "LICI.NS", "LTIM.NS", "LT.NS", "LTTS.NS", "LUPIN.NS",
    "M&M.NS", "M&MFIN.NS", "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS",
    "MAXHEALTH.NS", "METROBRAND.NS", "MCX.NS", "MOTHERSON.NS", "MPHASIS.NS",
    "MRF.NS", "MUTHOOTFIN.NS", "NATIONALUM.NS", "NAUKRI.NS", "NAVINFLUOR.NS",
    "NESTLEIND.NS", "NHPC.NS", "NMDC.NS", "NTPC.NS", "OBEROIRLTY.NS",
    "OFSS.NS", "OIL.NS", "ONGC.NS", "PAGEIND.NS", "PAYTM.NS",
    "PEL.NS", "PERSISTENT.NS", "PETRONET.NS", "PFC.NS", "PHOENIXLTD.NS",
    "PIDILITIND.NS", "PIIND.NS", "PNB.NS", "POLYCAB.NS", "POWERGRID.NS",
    "PRESTIGE.NS", "PVRINOX.NS", "RAMCOCEM.NS", "RBLBANK.NS", "RECLTD.NS",
    "RELIANCE.NS", "RVNL.NS", "SAIL.NS", "SBICARD.NS", "SBILIFE.NS",
    "SBIN.NS", "SHREECEM.NS", "SHRIRAMFIN.NS", "SIEMENS.NS", "SOLARINDS.NS",
    "SONACOMS.NS", "SRF.NS", "SUNPHARMA.NS", "SUNTV.NS", "SUPREMEIND.NS",
    "SUZLON.NS", "SYNGENE.NS", "TATACOMM.NS", "TATACONSUM.NS", "TATAELXSI.NS",
    "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS",
    "TIINDIA.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS",
    "TRIDENT.NS", "TVSMOTOR.NS", "UBL.NS", "ULTRACEMCO.NS", "UNIONBANK.NS",
    "UNOMINDA.NS", "UPL.NS", "VBL.NS", "VEDL.NS", "VOLTAS.NS",
    "WIPRO.NS", "YESBANK.NS", "ZEEL.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
]

HIGH_VOL_SYMBOLS = [
    "BSE.NS", "MCX.NS", "RVNL.NS", "MAZDOCK.NS", "BHEL.NS",
    "GODREJPROP.NS", "PRESTIGE.NS", "DLF.NS", "PFC.NS", "RECLTD.NS",
    "SUZLON.NS", "IDEA.NS", "ZOMATO.NS", "PAYTM.NS", "IRFC.NS",
    "GMRINFRA.NS", "SAIL.NS", "TATACOMM.NS", "MOTHERSON.NS", "ADANIENT.NS",
    "ADANIPOWER.NS", "ADANIGREEN.NS", "ADANIENSOL.NS", "NATIONALUM.NS", "HINDCOPPER.NS",
    "IRB.NS", "INDUSTOWER.NS", "BANDHANBNK.NS", "PNB.NS", "BANKBARODA.NS",
    "CANBK.NS", "IDFCFIRSTB.NS", "RBLBANK.NS", "UNIONBANK.NS", "ABCAPITAL.NS",
    "JIOFIN.NS", "GVT&D.NS", "INOXWIND.NS", "VOLTAS.NS", "CHOLAFIN.NS",
    "SHRIRAMFIN.NS", "TRENT.NS", "HAL.NS", "BEL.NS", "COCHINSHIP.NS",
    "TATAMOTORS.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "HINDALCO.NS",
    "JINDALSTEL.NS", "JSWENERGY.NS", "POLYCAB.NS", "KEI.NS", "KPITTECH.NS",
    "COFORGE.NS", "EXIDEIND.NS", "FORTIS.NS", "GLENMARK.NS", "BIOCON.NS"
]

ALL_SYMBOLS = list(dict.fromkeys(
    [t.replace(".NS", "") for t in (STANDARD_SYMBOLS + HIGH_VOL_SYMBOLS)]
))

TIMEFRAME_MAP = {"15m": "15min", "30m": "30min", "45m": "45min", "60m": "60min"}


# ─────────────────────────────────────────────────────────
# INDICATOR HELPERS
# ─────────────────────────────────────────────────────────
def ta_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def ta_sma(series, length):
    return series.rolling(window=length).mean()

def ta_rma(series, length):
    alpha = 1 / length
    rma = np.full(len(series), np.nan)
    if len(series) >= length:
        rma[length - 1] = series.iloc[:length].mean()
        for i in range(length, len(series)):
            rma[i] = alpha * series.iloc[i] + (1 - alpha) * rma[i - 1]
    return pd.Series(rma, index=series.index)

def ta_stdev_pop(series, length):
    return series.rolling(window=length).std(ddof=0)


# ─────────────────────────────────────────────────────────
# CORE DETECTION ENGINE (extended with L1 staging + boosters)
# ─────────────────────────────────────────────────────────
def detect_signals(df, l1_threshold=-2.0):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(c).lower() for c in df.columns]
    results = df.copy()

    results["ema_value"] = ta_ema(results["close"], 20)
    results["distance_pct"] = ((results["close"] - results["ema_value"]) / results["ema_value"]) * 100
    results["dist_stdev"] = ta_stdev_pop(results["distance_pct"], 100)
    results["exhaustion_band"] = -(results["dist_stdev"] * 2.5)

    results["vol_ma"] = ta_sma(results["volume"], 20)
    results["is_vol_surge"] = results["volume"] > (results["vol_ma"] * 2.0)

    dp = results["distance_pct"]
    results["is_turning_up"] = (dp > dp.shift(1)) & (dp.shift(1) < dp.shift(2))
    results["is_deep_exhaust"] = results["distance_pct"] <= results["exhaustion_band"]

    results["option_bottom_confirmed"] = (
        results["is_deep_exhaust"] & results["is_turning_up"] & results["is_vol_surge"]
    )

    di_len = 100
    high, low, close = results["high"], results["low"], results["close"]

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    tr = pd.concat([high - low, (high - close.shift(1)).abs(),
                    (low - close.shift(1)).abs()], axis=1).max(axis=1)

    tr_rma = ta_rma(tr, di_len)
    plus_dm_rma = ta_rma(pd.Series(plus_dm, index=results.index), di_len)
    minus_dm_rma = ta_rma(pd.Series(minus_dm, index=results.index), di_len)

    plus_di = np.where(tr_rma != 0, 100 * plus_dm_rma / tr_rma, 0.0)
    minus_di = np.where(tr_rma != 0, 100 * minus_dm_rma / tr_rma, 0.0)
    results["raw_di_diff"] = plus_di - minus_di

    # ─── Level 1 detection ───
    results["is_L1"] = results["distance_pct"] <= l1_threshold
    # L1 occurred in the last ~18 bars but at least 2 bars ago (excludes gap-downs)
    results["L1_recent"] = (
        results["is_L1"].shift(2)
        .rolling(18, min_periods=1).max()
        .fillna(0).astype(bool)
    )

    # ─── Volume footprint: L1 dry-up → L2 surge ───
    results["is_L1_dry"] = results["is_L1"] & (results["volume"] < results["vol_ma"])
    results["L1_dry_recent"] = (
        results["is_L1_dry"].shift(2)
        .rolling(18, min_periods=1).max()
        .fillna(0).astype(bool)
    )
    results["vol_footprint"] = results["L1_dry_recent"] & results["is_vol_surge"]

    # ─── Candle strength ───
    rng = (results["high"] - results["low"]).replace(0, np.nan)
    results["candle_pos"] = (results["close"] - results["low"]) / rng
    results["candle_strong"] = results["candle_pos"] >= 0.4

    # ─── Momentum deceleration ───
    ret1 = results["close"].pct_change()
    results["mom_decel"] = ret1 > ret1.shift(1)

    # ─── Swing support proximity ───
    results["atr"] = (results["high"] - results["low"]).rolling(14, min_periods=1).mean()
    results["low_100"] = results["low"].rolling(100, min_periods=50).min()
    dist_low_atr = (results["close"] - results["low_100"]) / results["atr"].replace(0, np.nan)
    results["dist_to_low_atr"] = dist_low_atr
    results["near_support"] = dist_low_atr <= 1.5

    # ─── Core vs Final signal ───
    results["signal_core"] = (
        results["option_bottom_confirmed"] & (results["raw_di_diff"] < -10)
    )
    results["signal_final"] = results["signal_core"] & results["L1_recent"]
    return results


# ─────────────────────────────────────────────────────────
# BATCH FETCH
# ─────────────────────────────────────────────────────────
def batch_fetch(tickers, period="60d", interval="15m"):
    symbols = [f"{t}.NS" if not t.endswith(".NS") else t for t in tickers]
    try:
        raw = yf.download(
            symbols, period=period, interval=interval,
            progress=False, auto_adjust=True, threads=True,
            group_by="ticker",
        )
    except Exception as e:
        return {}, f"Download error: {e}"

    if raw is None or raw.empty:
        return {}, "No data returned by provider"

    out = {}
    if isinstance(raw.columns, pd.MultiIndex):
        available = raw.columns.get_level_values(0).unique()
        for sym in symbols:
            if sym not in available:
                continue
            df = raw[sym].dropna(how="all")
            if df.empty:
                continue
            df.columns = [str(c).lower() for c in df.columns]
            out[sym.replace(".NS", "")] = df
    else:
        if len(symbols) == 1 and not raw.dropna(how="all").empty:
            df = raw.dropna(how="all")
            df.columns = [str(c).lower() for c in df.columns]
            out[symbols[0].replace(".NS", "")] = df

    return out, None


# ─────────────────────────────────────────────────────────
# CONFLUENCE SCORING
# ─────────────────────────────────────────────────────────
def compute_base_quality(row):
    vol_ma = row.get("vol_ma", np.nan)
    vol_ratio = float(row["volume"] / vol_ma) if (vol_ma and vol_ma > 0) else 0.0
    dev = float(row["distance_pct"])
    bias = float(row["raw_di_diff"])
    vol_score = min(100.0, max(0.0, (vol_ratio - 2.0) / 4.0 * 100))
    dev_score = min(100.0, abs(dev) / 12.0 * 100)
    bias_score = min(100.0, abs(bias) / 35.0 * 100)
    quality = round(0.30 * vol_score + 0.35 * dev_score + 0.35 * bias_score)
    return quality


def assess_mtf_agreement(tf_scanned, sig_idx, sig_tf):
    """Count of OTHER timeframes showing oversold state at sig_idx."""
    agree = 0
    details = {}
    for other_tf, other in tf_scanned.items():
        if other_tf == sig_tf or other is None:
            continue
        pos = other.index.searchsorted(sig_idx, side="right") - 1
        if pos < 0:
            details[other_tf] = {"dev": None, "di": None, "oversold": False}
            continue
        bar = other.iloc[pos]
        dev = float(bar["distance_pct"])
        di = float(bar["raw_di_diff"])
        oversold = (dev <= -1.0) and (di < -5)
        details[other_tf] = {"dev": round(dev, 2), "di": round(di, 2),
                              "oversold": oversold}
        if oversold:
            agree += 1
    return agree, details


def compute_conviction(base_quality, mtf_agree, vol_footprint,
                        candle_strong, mom_decel, near_support):
    score = 0
    score += min(20, base_quality * 0.20)
    score += 25 if mtf_agree >= 2 else (15 if mtf_agree == 1 else 0)
    score += 15 if vol_footprint else 0
    score += 15 if candle_strong else 0
    score += 10 if mom_decel else 0
    score += 15 if near_support else 0
    return round(score)


def score_to_tier(booster_pts):
    if booster_pts >= 6: return "S"
    if booster_pts >= 5: return "A"
    if booster_pts >= 4: return "B"
    if booster_pts >= 3: return "C"
    return "—"


def compute_outcome(scanned, sig_pos, holding_bars=20):
    """Simple outcome: entry=signal close, stop=bar low-0.5 ATR, target=entry+1R."""
    if sig_pos + holding_bars >= len(scanned):
        return {"status": "Pending", "r": None}
    try:
        entry = float(scanned.iloc[sig_pos]["close"])
        atr = float(scanned.iloc[sig_pos].get("atr", np.nan))
        if pd.isna(atr) or atr <= 0:
            atr = entry * 0.01
        stop = float(scanned.iloc[sig_pos]["low"]) - 0.5 * atr
        risk = entry - stop
        if risk <= 0:
            return {"status": "Invalid", "r": None}

        window = scanned.iloc[sig_pos + 1: sig_pos + holding_bars + 1]
        if window.empty:
            return {"status": "Pending", "r": None}

        max_high = float(window["high"].max())
        min_low = float(window["low"].min())

        if min_low <= stop:
            return {"status": "Stop Hit", "r": -1.0}

        target = entry + risk  # 1R
        if max_high >= target:
            return {"status": "Target Hit", "r": round((max_high - entry) / risk, 2)}

        return {"status": "Open",
                "r": round((max_high - entry) / risk, 2) if max_high > entry else 0.0}
    except Exception:
        return {"status": "Pending", "r": None}


# ─────────────────────────────────────────────────────────
# PROCESS BATCH
# ─────────────────────────────────────────────────────────
def process_batch(batch_data, timeframes, days_back=10, l1_threshold=-2.0,
                  min_boosters=3, progress_cb=None, ticker_cb=None):
    t0 = time.time()
    tf_map = [(tf, TIMEFRAME_MAP[tf]) for tf in timeframes if tf in TIMEFRAME_MAP]

    all_results = []
    errors = []
    diag_total = {"empty_data": 0, "stage_core": 0, "stage_final": 0,
                  "tier_counts": {"S": 0, "A": 0, "B": 0, "C": 0}}

    ist = pytz.timezone("Asia/Kolkata")
    cutoff = (datetime.now(ist) - timedelta(days=days_back)).date()

    now_ist = datetime.now(ist)
    is_live_market = (now_ist.weekday() < 5) and (
        (now_ist.hour > 9 or (now_ist.hour == 9 and now_ist.minute >= 15))
        and (now_ist.hour < 15 or (now_ist.hour == 15 and now_ist.minute <= 30))
    )

    items = list(batch_data.items())
    total = max(len(items), 1)

    for i, (ticker, raw) in enumerate(items, 1):
        try:
            if raw is None or raw.empty:
                diag_total["empty_data"] += 1
                if ticker_cb: ticker_cb(ticker, 0)
                if progress_cb: progress_cb(i / total)
                continue

            if not isinstance(raw.index, pd.DatetimeIndex):
                raw.index = pd.to_datetime(raw.index)
            if raw.index.tz is None:
                raw.index = raw.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
            else:
                raw.index = raw.index.tz_convert("Asia/Kolkata")

            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            raw.columns = [str(c).lower() for c in raw.columns]

            if "volume" not in raw.columns:
                errors.append((ticker, "missing volume column"))
                if ticker_cb: ticker_cb(ticker, 0)
                if progress_cb: progress_cb(i / total)
                continue

            raw = raw[raw["volume"] > 0]
            if len(raw) < 100:
                if ticker_cb: ticker_cb(ticker, 0)
                if progress_cb: progress_cb(i / total)
                continue

            # Pre-scan all selected TFs once
            tf_scanned = {}
            for tf_name, resample_rule in tf_map:
                try:
                    resampled = raw.resample(
                        resample_rule, origin="start_day", offset="9h15min",
                        label="left", closed="left",
                    ).agg({
                        "open": "first", "high": "max",
                        "low": "min", "close": "last", "volume": "sum",
                    }).dropna()

                    if len(resampled) < 100:
                        tf_scanned[tf_name] = None
                        continue
                    if is_live_market and len(resampled) > 1:
                        resampled = resampled.iloc[:-1]
                    tf_scanned[tf_name] = detect_signals(resampled, l1_threshold)
                except Exception:
                    tf_scanned[tf_name] = None

            ticker_signals = 0
            for tf_name, scanned in tf_scanned.items():
                if scanned is None:
                    continue

                diag_total["stage_core"] += int(scanned["signal_core"].sum())
                diag_total["stage_final"] += int(scanned["signal_final"].sum())

                sigs = scanned[scanned["signal_final"]].copy()
                if sigs.empty:
                    continue

                for sig_idx in sigs.index:
                    sig_row = scanned.loc[sig_idx]
                    try:
                        sig_pos = scanned.index.get_loc(sig_idx)
                    except Exception:
                        continue

                    base_q = compute_base_quality(sig_row)
                    mtf_agree, mtf_details = assess_mtf_agreement(
                        tf_scanned, sig_idx, tf_name
                    )

                    vol_fp = bool(sig_row["vol_footprint"])
                    candle_strong = bool(sig_row["candle_strong"])
                    mom_decel = bool(sig_row["mom_decel"])
                    near_sup = bool(sig_row["near_support"])

                    booster_pts = (
                        (2 if mtf_agree >= 2 else (1 if mtf_agree == 1 else 0)) +
                        (1 if vol_fp else 0) +
                        (1 if candle_strong else 0) +
                        (1 if mom_decel else 0) +
                        (1 if near_sup else 0)
                    )
                    tier = score_to_tier(booster_pts)

                    if tier == "—" or booster_pts < min_boosters:
                        continue

                    conviction = compute_conviction(
                        base_q, mtf_agree, vol_fp, candle_strong, mom_decel, near_sup
                    )

                    outcome = compute_outcome(scanned, sig_pos)
                    diag_total["tier_counts"][tier] += 1

                    all_results.append({
                        "datetime": sig_idx,
                        "ticker": ticker,
                        "timeframe": tf_name,
                        "close": float(sig_row["close"]),
                        "distance_pct": float(sig_row["distance_pct"]),
                        "raw_di_diff": float(sig_row["raw_di_diff"]),
                        "tier": tier,
                        "conviction": int(conviction),
                        "booster_pts": int(booster_pts),
                        "base_quality": int(base_q),
                        "mtf_agree": int(mtf_agree),
                        "vol_footprint": vol_fp,
                        "candle_strong": candle_strong,
                        "mom_decel": mom_decel,
                        "near_support": near_sup,
                        "mtf_details": json.dumps(mtf_details),
                        "outcome_status": outcome["status"],
                        "outcome_r": outcome["r"],
                    })
                    ticker_signals += 1

            if ticker_cb: ticker_cb(ticker, ticker_signals)

        except Exception as e:
            errors.append((ticker, str(e)))

        if progress_cb: progress_cb(i / total)

    elapsed = round(time.time() - t0, 1)

    if all_results:
        df = pd.DataFrame(all_results)
        df = df[df["datetime"].dt.date >= cutoff]
        df = df.sort_values("datetime", ascending=False).reset_index(drop=True)
    else:
        df = pd.DataFrame(columns=[
            "datetime", "ticker", "timeframe", "close", "distance_pct",
            "raw_di_diff", "tier", "conviction", "booster_pts", "base_quality",
            "mtf_agree", "vol_footprint", "candle_strong", "mom_decel",
            "near_support", "mtf_details", "outcome_status", "outcome_r"
        ])

    return {
        "results_df": df,
        "diag": diag_total,
        "errors": errors,
        "scan_time_s": elapsed,
        "cutoff": cutoff,
        "tickers_processed": len(items),
    }


# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────
def market_status():
    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    if now.weekday() >= 5:
        return False, "SESSION CLOSED"
    in_session = (
        (now.hour > 9 or (now.hour == 9 and now.minute >= 15))
        and (now.hour < 15 or (now.hour == 15 and now.minute <= 30))
    )
    return (True, "SESSION LIVE") if in_session else (False, "SESSION CLOSED")


def to_csv_bytes(df):
    """Export: Stock Name, Dev %, Bias only (as requested)."""
    if df is None or df.empty:
        return b""
    exp = df[["ticker", "distance_pct", "raw_di_diff"]].copy()
    exp.columns = ["Stock Name", "Dev %", "Bias"]
    return exp.to_csv(index=False).encode("utf-8")


@st.cache_data(ttl=600, show_spinner=False)
def cached_batch(tickers_tuple):
    return batch_fetch(list(tickers_tuple), period="60d", interval="15m")


# ─────────────────────────────────────────────────────────
# SIGNAL CONTEXT (for CHART tab)
# ─────────────────────────────────────────────────────────
def compute_signal_context(scanned, row):
    sig_dt = row["datetime"]
    if sig_dt in scanned.index:
        sig_pos = scanned.index.get_loc(sig_dt)
    else:
        sig_pos = int(scanned.index.get_indexer([sig_dt], method="nearest")[0])

    bar = scanned.iloc[sig_pos]
    vol_ma = bar.get("vol_ma", np.nan)
    vol_ratio = float(bar["volume"] / vol_ma) if (vol_ma and vol_ma > 0) else 0.0
    dev = float(bar["distance_pct"])
    bias = float(bar["raw_di_diff"])

    vol_score = min(100.0, max(0.0, (vol_ratio - 2.0) / 4.0 * 100))
    dev_score = min(100.0, abs(dev) / 12.0 * 100)
    bias_score = min(100.0, abs(bias) / 35.0 * 100)
    quality = round(0.30 * vol_score + 0.35 * dev_score + 0.35 * bias_score)

    if quality >= 80:   label = "Exceptional"
    elif quality >= 65: label = "Strong"
    elif quality >= 50: label = "Moderate"
    elif quality >= 35: label = "Weak"
    else:               label = "Marginal"

    lookback = scanned.iloc[max(0, sig_pos - 100):sig_pos + 1]
    recent_high = float(lookback["high"].max())
    recent_low = float(lookback["low"].min())
    dist_from_high = (float(bar["close"]) - recent_high) / recent_high * 100
    dist_from_low = (float(bar["close"]) - recent_low) / recent_low * 100

    bars_since = len(scanned) - 1 - sig_pos
    if sig_pos < len(scanned) - 1:
        current_close = float(scanned.iloc[-1]["close"])
        change_since = (current_close - float(bar["close"])) / float(bar["close"]) * 100
    else:
        change_since = 0.0

    # Booster checklist info (recompute for display)
    candle_pos = float(bar.get("candle_pos", np.nan))
    mom_decel = bool(bar.get("mom_decel", False))
    near_support = bool(bar.get("near_support", False))
    vol_fp = bool(bar.get("vol_footprint", False))
    dist_low_atr = float(bar.get("dist_to_low_atr", np.nan))

    return {
        "vol_ratio": vol_ratio, "vol_score": vol_score,
        "dev": dev, "bias": bias,
        "quality": quality, "quality_label": label,
        "dist_from_high": dist_from_high, "dist_from_low": dist_from_low,
        "bars_since": int(bars_since), "change_since": float(change_since),
        "sig_pos": int(sig_pos), "bar": bar,
        "recent_high": recent_high, "recent_low": recent_low,
        "candle_pos": candle_pos,
        "mom_decel": mom_decel,
        "near_support": near_support,
        "vol_footprint": vol_fp,
        "dist_to_low_atr": dist_low_atr,
    }


def get_current_mtf_state(raw, l1_threshold=-2.0):
    result = {}
    for tf_name, rule in TIMEFRAME_MAP.items():
        try:
            rs = raw.res
