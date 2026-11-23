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
SIGNAL_MARKER = "#C9A227"
L1_LINE_COLOR = "#F59E0B"

# ─────────────────────────────────────────────────────────
# BRANDING
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
# PAGE CONFIG + CSS
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fintrix Analytics · Signal Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
:root {
    --bg-app:#0B0F14; --bg-panel:#121821; --bg-elevated:#172030;
    --border:#1F2937; --accent-teal:#00D1B2; --accent-gold:#C9A227;
    --bullish:#22C55E; --bearish:#EF4444; --warning:#F59E0B;
    --text-primary:#E5E7EB; --text-muted:#9CA3AF;
}
html,body,[class*="css"]{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;}
.stApp{background:var(--bg-app);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1.5rem;padding-bottom:2rem;max-width:1500px;}
.section-label{font-size:11px;font-weight:600;letter-spacing:0.08em;
    text-transform:uppercase;color:var(--text-muted);margin-bottom:12px;}
.land-wrap{max-width:900px;margin:80px auto 60px;text-align:center;padding:0 24px;}
.land-eyebrow{font-size:11px;font-weight:600;letter-spacing:0.16em;
    text-transform:uppercase;color:var(--accent-gold);margin-bottom:20px;}
.land-title{font-size:3.6rem;font-weight:700;line-height:1.05;
    color:var(--text-primary);margin:0 0 8px 0;letter-spacing:-0.02em;}
.land-title::after{content:'';display:block;width:64px;height:2px;
    background:var(--accent-gold);margin:20px auto 0;}
.land-tagline{font-size:1.05rem;color:var(--text-muted);font-weight:500;
    letter-spacing:0.04em;margin:24px 0 12px 0;}
.land-sub{color:var(--text-muted);font-size:0.95rem;line-height:1.7;
    max-width:620px;margin:0 auto;}
.land-stats{display:flex;gap:1px;justify-content:center;margin:48px auto 0;
    flex-wrap:wrap;border:1px solid var(--border);border-radius:8px;
    overflow:hidden;background:var(--border);max-width:560px;}
.land-stat{background:var(--bg-panel);padding:20px 40px;flex:1;min-width:150px;}
.land-stat .num{color:var(--text-primary);font-family:'JetBrains Mono',monospace;
    font-size:1.7rem;font-weight:600;line-height:1;}
.land-stat .lbl{color:var(--text-muted);font-size:10px;margin-top:8px;
    letter-spacing:0.08em;text-transform:uppercase;font-weight:600;}
.land-features{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;
    margin-top:48px;text-align:left;background:var(--border);
    border:1px solid var(--border);border-radius:8px;overflow:hidden;}
.land-feature{background:var(--bg-panel);padding:24px;}
.land-feature h4{color:var(--text-primary);font-size:0.88rem;
    margin:0 0 8px 0;font-weight:600;}
.land-feature p{color:var(--text-muted);font-size:0.82rem;margin:0;line-height:1.6;}
.hero-wrap{background:linear-gradient(180deg,#121821 0%,#0E131A 100%);
    border:1px solid var(--border);border-radius:8px;padding:24px 28px;
    margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.4);}
.hero-eyebrow{font-size:10px;font-weight:600;letter-spacing:0.16em;
    text-transform:uppercase;color:var(--accent-gold);margin-bottom:8px;}
.hero-title{font-size:22px;font-weight:600;color:var(--text-primary);
    margin:0 0 6px 0;letter-spacing:-0.005em;line-height:1.3;}
.hero-title::after{content:'';display:block;width:48px;height:1px;
    background:var(--accent-gold);margin-top:10px;}
.hero-sub{color:var(--text-muted);font-size:12px;margin:12px 0 0 0;
    letter-spacing:0.02em;}
.hero-quote{margin:16px 0 0 0;padding-top:14px;border-top:1px solid var(--border);
    font-size:12px;font-style:italic;color:var(--accent-gold);
    letter-spacing:0.02em;line-height:1.55;opacity:0.92;}
.status-pill{display:inline-flex;align-items:center;gap:8px;padding:5px 12px;
    border-radius:4px;font-size:10px;font-weight:600;letter-spacing:0.08em;
    text-transform:uppercase;margin-top:14px;}
.status-live{background:rgba(34,197,94,0.1);color:var(--bullish);
    border:1px solid rgba(34,197,94,0.35);}
.status-closed{background:rgba(245,158,11,0.08);color:var(--warning);
    border:1px solid rgba(245,158,11,0.35);}
.dot{width:6px;height:6px;border-radius:50%;}
.dot-live{background:var(--bullish);box-shadow:0 0 6px var(--bullish);}
.dot-closed{background:var(--warning);}
.control-card{background:var(--bg-panel);border:1px solid var(--border);
    border-radius:8px;padding:22px 26px;margin-bottom:18px;
    box-shadow:0 1px 3px rgba(0,0,0,0.4);}
.control-title{color:var(--text-muted);font-size:11px;letter-spacing:0.08em;
    font-weight:600;text-transform:uppercase;margin-bottom:18px;
    padding-bottom:12px;border-bottom:1px solid var(--border);}
[data-testid="stMetric"]{background:var(--bg-panel);border:1px solid var(--border);
    border-top:1px solid var(--border);border-radius:8px;padding:16px 18px;
    box-shadow:0 1px 3px rgba(0,0,0,0.4);
    transition:border-top-color 150ms ease,box-shadow 150ms ease;}
[data-testid="stMetric"]:hover{border-top-color:var(--accent-teal);
    box-shadow:0 1px 6px rgba(0,209,178,0.1);}
[data-testid="stMetricLabel"]{color:var(--text-muted)!important;
    font-size:10px!important;letter-spacing:0.08em!important;
    text-transform:uppercase!important;font-weight:600!important;}
[data-testid="stMetricValue"]{color:var(--text-primary)!important;
    font-family:'JetBrains Mono',monospace!important;font-weight:600!important;
    font-size:1.6rem!important;}
[data-testid="stMetricDelta"]{font-family:'JetBrains Mono',monospace!important;
    font-size:11px!important;font-weight:500!important;}
.stButton>button{border-radius:6px;font-weight:600;font-size:12px;
    letter-spacing:0.06em;text-transform:uppercase;padding:0.65rem 1.2rem;
    transition:all 150ms ease;border:1px solid var(--border);background:transparent;
    color:var(--text-primary)!important;}
.stButton>button:hover{border-color:var(--accent-teal);
    color:var(--accent-teal)!important;background:rgba(0,209,178,0.04);}
.stButton>button[kind="primary"]{background:var(--accent-teal);
    color:#0B0F14!important;border:1px solid var(--accent-teal);font-weight:700;}
.stButton>button[kind="primary"]:hover{background:#00E5C4;border-color:#00E5C4;
    color:#0B0F14!important;box-shadow:0 0 20px rgba(0,209,178,0.35);}
.stDownloadButton>button{border-radius:6px;font-weight:600;font-size:12px;
    letter-spacing:0.06em;text-transform:uppercase;padding:0.65rem 1.2rem;
    background:transparent;color:var(--accent-teal)!important;
    border:1px solid var(--accent-teal);}
.stDownloadButton>button:hover{background:rgba(0,209,178,0.08);
    box-shadow:0 0 16px rgba(0,209,178,0.2);}
.stSelectbox label,.stMultiSelect label,.stSlider label,.stRadio label,
.stTextInput label{color:var(--text-muted)!important;font-weight:500!important;
    font-size:11px!important;letter-spacing:0.06em!important;
    text-transform:uppercase!important;}
[data-baseweb="select"]>div{background:var(--bg-elevated)!important;
    border:1px solid var(--border)!important;border-radius:6px!important;
    color:var(--text-primary)!important;}
[data-baseweb="select"]>div:focus-within{border-color:var(--accent-teal)!important;
    box-shadow:0 0 0 2px rgba(0,209,178,0.15)!important;}
[data-baseweb="tag"]{background:rgba(0,209,178,0.15)!important;
    color:var(--accent-teal)!important;
    border:1px solid rgba(0,209,178,0.3)!important;}
[data-baseweb="tag"] span{color:var(--accent-teal)!important;}
.stSlider [data-baseweb="slider"] [role="slider"]{background:var(--accent-teal)!important;
    border:2px solid var(--bg-panel)!important;
    box-shadow:0 0 0 1px var(--accent-teal)!important;}
.stRadio [role="radiogroup"] label{text-transform:none!important;
    letter-spacing:0!important;font-size:13px!important;
    color:var(--text-primary)!important;}
.stRadio [role="radiogroup"] label[data-checked="true"]{
    color:var(--accent-teal)!important;}
.stCheckbox label{color:var(--text-primary)!important;font-size:13px!important;
    text-transform:none!important;letter-spacing:0!important;}
.stTabs [data-baseweb="tab-list"]{gap:0;border-bottom:1px solid var(--border);
    padding-bottom:0;}
.stTabs [data-baseweb="tab"]{color:var(--text-muted);font-weight:600;
    font-size:11px;letter-spacing:0.08em;text-transform:uppercase;
    padding:12px 20px;border-bottom:2px solid transparent;
    transition:color 150ms ease,border-color 150ms ease;}
.stTabs [data-baseweb="tab"]:hover{color:var(--text-primary);}
.stTabs [aria-selected="true"]{color:var(--accent-teal)!important;
    border-bottom:2px solid var(--accent-teal)!important;
    background:transparent!important;}
h2,h3,h4{color:var(--text-primary)!important;letter-spacing:-0.01em;
    font-weight:600!important;}
h2{font-size:16px!important;margin-top:1.4rem!important;padding-bottom:10px;
    border-bottom:1px solid var(--border);}
h3{font-size:14px!important;} h4{font-size:13px!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;
    border-radius:8px!important;overflow:hidden!important;
    background:var(--bg-panel)!important;}
[data-testid="stDataFrame"] [role="columnheader"]{background:var(--bg-elevated)!important;
    color:var(--text-muted)!important;font-size:10px!important;
    font-weight:600!important;letter-spacing:0.08em!important;
    text-transform:uppercase!important;border-bottom:1px solid var(--border)!important;
    padding:10px 12px!important;}
[data-testid="stDataFrame"] [role="gridcell"]{
    font-family:'JetBrains Mono',monospace!important;font-size:12px!important;
    color:var(--text-primary)!important;padding:8px 12px!important;
    border-bottom:1px solid rgba(31,41,55,0.5)!important;}
[data-testid="stDataFrame"] [role="row"]:nth-child(even) [role="gridcell"]{
    background:#0F141C!important;}
[data-testid="stDataFrame"] [role="row"]:nth-child(odd) [role="gridcell"]{
    background:var(--bg-panel)!important;}
[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"]{
    background:var(--bg-elevated)!important;}
div[data-testid="stAlert"]{border-radius:6px;border:1px solid var(--border);
    border-left-width:3px;background:var(--bg-panel);}
div[data-testid="stAlert"] p{color:var(--text-primary)!important;
    font-size:13px!important;line-height:1.6;}
.stProgress>div>div>div>div{background:var(--accent-teal)!important;}
.stCaption,[data-testid="stCaptionContainer"]{color:var(--text-muted)!important;
    font-size:11px!important;}
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--bg-app);}
::-webkit-scrollbar-thumb{background:#334155;border-radius:4px;
    transition:background 150ms ease;}
::-webkit-scrollbar-thumb:hover{background:var(--accent-teal);}
.fintrix-footer{text-align:center;margin-top:56px;padding:32px 20px 16px;
    border-top:1px solid var(--border);}
.fintrix-footer .brand{font-size:12px;font-weight:700;letter-spacing:0.20em;
    text-transform:uppercase;color:var(--accent-gold);margin-bottom:6px;}
.fintrix-footer .tag{color:var(--text-muted);font-size:10px;
    letter-spacing:0.16em;text-transform:uppercase;font-weight:500;}
@media (max-width:768px){
    .block-container{padding-left:0.85rem;padding-right:0.85rem;padding-top:1rem;}
    .land-wrap{margin:40px auto 30px;padding:0 16px;}
    .land-title{font-size:2.2rem!important;}
    .land-title::after{margin-top:14px;width:44px;}
    .land-tagline{font-size:0.9rem!important;margin:20px 0 10px 0;}
    .land-sub{font-size:0.85rem!important;line-height:1.6!important;}
    .land-eyebrow{font-size:10px!important;margin-bottom:16px;}
    .land-stats{margin-top:32px;max-width:100%;}
    .land-stat{padding:16px 20px;min-width:100px;}
    .land-stat .num{font-size:1.4rem;}
    .land-stat .lbl{font-size:9px;}
    .land-features{grid-template-columns:1fr;margin-top:32px;}
    .land-feature{padding:18px;}
    .hero-wrap{padding:18px 20px!important;}
    .hero-title{font-size:18px!important;}
    .hero-eyebrow{font-size:9px!important;}
    .hero-sub{font-size:11px!important;}
    .hero-quote{font-size:11px!important;padding-top:12px!important;}
    .status-pill{font-size:9px!important;padding:4px 10px!important;}
    .control-card{padding:16px 18px!important;}
    .control-title{font-size:10px!important;margin-bottom:14px!important;}
    [data-testid="stMetric"]{padding:12px 14px!important;}
    [data-testid="stMetricValue"]{font-size:1.3rem!important;}
    [data-testid="stMetricLabel"]{font-size:9px!important;}
    .stButton>button{padding:0.7rem 1rem!important;font-size:11px!important;
        min-height:42px!important;}
    .stTabs [data-baseweb="tab"]{font-size:10px!important;padding:9px 10px!important;}
    h2{font-size:14px!important;} h3{font-size:13px!important;}
    h4{font-size:12px!important;}
    [data-testid="stDataFrame"] [role="gridcell"]{font-size:11px!important;}
    .fintrix-footer{margin-top:40px;padding-top:24px;}
    .fintrix-footer .brand{font-size:10px;letter-spacing:0.16em;}
    .fintrix-footer .tag{font-size:9px;}
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
# CORE DETECTION
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

    # L1 staging
    results["is_L1"] = results["distance_pct"] <= l1_threshold
    results["L1_recent"] = (results["is_L1"].shift(2)
                            .rolling(18, min_periods=1).max()
                            .fillna(0).astype(bool))
    results["is_L1_dry"] = results["is_L1"] & (results["volume"] < results["vol_ma"])
    results["L1_dry_recent"] = (results["is_L1_dry"].shift(2)
                                .rolling(18, min_periods=1).max()
                                .fillna(0).astype(bool))
    results["vol_footprint"] = results["L1_dry_recent"] & results["is_vol_surge"]

    rng = (results["high"] - results["low"]).replace(0, np.nan)
    results["candle_pos"] = (results["close"] - results["low"]) / rng
    results["candle_strong"] = results["candle_pos"] >= 0.4

    ret1 = results["close"].pct_change()
    results["mom_decel"] = ret1 > ret1.shift(1)

    results["atr"] = (results["high"] - results["low"]).rolling(14, min_periods=1).mean()
    results["low_100"] = results["low"].rolling(100, min_periods=50).min()
    dist_low_atr = (results["close"] - results["low_100"]) / results["atr"].replace(0, np.nan)
    results["dist_to_low_atr"] = dist_low_atr
    results["near_support"] = dist_low_atr <= 1.5

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
        raw = yf.download(symbols, period=period, interval=interval,
                          progress=False, auto_adjust=True, threads=True,
                          group_by="ticker")
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
# SCORING HELPERS
# ─────────────────────────────────────────────────────────
def compute_base_quality(row):
    vol_ma = row.get("vol_ma", np.nan)
    vol_ratio = float(row["volume"] / vol_ma) if (vol_ma and vol_ma > 0) else 0.0
    dev = float(row["distance_pct"])
    bias = float(row["raw_di_diff"])
    vol_score = min(100.0, max(0.0, (vol_ratio - 2.0) / 4.0 * 100))
    dev_score = min(100.0, abs(dev) / 12.0 * 100)
    bias_score = min(100.0, abs(bias) / 35.0 * 100)
    return round(0.30 * vol_score + 0.35 * dev_score + 0.35 * bias_score)


def assess_mtf_agreement(tf_scanned, sig_idx, sig_tf):
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
        target = entry + risk
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

            tf_scanned = {}
            for tf_name, resample_rule in tf_map:
                try:
                    resampled = raw.resample(
                        resample_rule, origin="start_day", offset="9h15min",
                        label="left", closed="left",
                    ).agg({"open": "first", "high": "max",
                           "low": "min", "close": "last", "volume": "sum"}).dropna()
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
                    mtf_agree, mtf_details = assess_mtf_agreement(tf_scanned, sig_idx, tf_name)
                    vol_fp = bool(sig_row["vol_footprint"])
                    candle_strong = bool(sig_row["candle_strong"])
                    mom_decel = bool(sig_row["mom_decel"])
                    near_sup = bool(sig_row["near_support"])
                    booster_pts = (
                        (2 if mtf_agree >= 2 else (1 if mtf_agree == 1 else 0)) +
                        (1 if vol_fp else 0) + (1 if candle_strong else 0) +
                        (1 if mom_decel else 0) + (1 if near_sup else 0)
                    )
                    tier = score_to_tier(booster_pts)
                    if tier == "—" or booster_pts < min_boosters:
                        continue
                    conviction = compute_conviction(base_q, mtf_agree, vol_fp,
                                                     candle_strong, mom_decel, near_sup)
                    outcome = compute_outcome(scanned, sig_pos)
                    diag_total["tier_counts"][tier] += 1
                    all_results.append({
                        "datetime": sig_idx, "ticker": ticker, "timeframe": tf_name,
                        "close": float(sig_row["close"]),
                        "distance_pct": float(sig_row["distance_pct"]),
                        "raw_di_diff": float(sig_row["raw_di_diff"]),
                        "tier": tier, "conviction": int(conviction),
                        "booster_pts": int(booster_pts),
                        "base_quality": int(base_q), "mtf_agree": int(mtf_agree),
                        "vol_footprint": vol_fp, "candle_strong": candle_strong,
                        "mom_decel": mom_decel, "near_support": near_sup,
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
        "results_df": df, "diag": diag_total, "errors": errors,
        "scan_time_s": elapsed, "cutoff": cutoff,
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
    if df is None or df.empty:
        return b""
    exp = df[["ticker", "distance_pct", "raw_di_diff"]].copy()
    exp.columns = ["Stock Name", "Dev %", "Bias"]
    return exp.to_csv(index=False).encode("utf-8")


@st.cache_data(ttl=600, show_spinner=False)
def cached_batch(tickers_tuple):
    return batch_fetch(list(tickers_tuple), period="60d", interval="15m")


# ─────────────────────────────────────────────────────────
# SIGNAL CONTEXT + CHART HELPERS
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
    return {
        "vol_ratio": vol_ratio, "vol_score": vol_score,
        "dev": dev, "bias": bias,
        "quality": quality, "quality_label": label,
        "dist_from_high": dist_from_high, "dist_from_low": dist_from_low,
        "bars_since": int(bars_since), "change_since": float(change_since),
        "sig_pos": int(sig_pos), "bar": bar,
        "recent_high": recent_high, "recent_low": recent_low,
        "candle_pos": float(bar.get("candle_pos", np.nan)),
        "mom_decel": bool(bar.get("mom_decel", False)),
        "near_support": bool(bar.get("near_support", False)),
        "vol_footprint": bool(bar.get("vol_footprint", False)),
        "dist_to_low_atr": float(bar.get("dist_to_low_atr", np.nan)),
    }


def get_current_mtf_state(raw, l1_threshold=-2.0):
    result = {}
    for tf_name, rule in TIMEFRAME_MAP.items():
        try:
            rs = raw.resample(rule, origin="start_day", offset="9h15min",
                              label="left", closed="left").agg({
                                  "open": "first", "high": "max", "low": "min",
                                  "close": "last", "volume": "sum"}).dropna()
            if len(rs) < 100:
                result[tf_name] = None
                continue
            scanned = detect_signals(rs, l1_threshold)
            last = scanned.iloc[-1]
            vma = last.get("vol_ma", np.nan)
            vol_ratio = float(last["volume"] / vma) if (vma and vma > 0) else 0.0
            vol_score = min(100.0, max(0.0, (vol_ratio - 2.0) / 4.0 * 100))
            if bool(last["signal_final"]):
                status = "Active"
            elif bool(last["option_bottom_confirmed"]):
                status = "Exhaustion"
            elif float(last["raw_di_diff"]) < -10:
                status = "Bias Only"
            else:
                status = "Quiet"
            result[tf_name] = {
                "status": status, "signal": bool(last["signal_final"]),
                "bias": float(last["raw_di_diff"]),
                "dev": float(last["distance_pct"]),
                "vol_ratio": vol_ratio, "vol_score": vol_score,
            }
        except Exception:
            result[tf_name] = None
    return result


def build_pro_chart(scanned, row, ctx, l1_threshold=-2.0, window_days=7):
    sig_dt = row["datetime"]
    start = sig_dt - pd.Timedelta(days=window_days)
    end = sig_dt + pd.Timedelta(days=2)
    win = scanned.loc[(scanned.index >= start) & (scanned.index <= end)].copy()
    if win.empty:
        return None

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, row_heights=[0.74, 0.26])

    fig.add_trace(go.Candlestick(
        x=win.index, open=win["open"], high=win["high"],
        low=win["low"], close=win["close"], name="Price",
        increasing_line_color=CANDLE_UP, decreasing_line_color=CANDLE_DOWN,
        increasing_fillcolor="rgba(34,197,94,0.35)",
        decreasing_fillcolor="rgba(239,68,68,0.35)",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=win.index, y=win["ema_value"], name="Baseline",
        line=dict(color=EMA_PRIMARY, width=1.5), opacity=0.9,
        hovertemplate="Baseline: %{y:.2f}<extra></extra>",
    ), row=1, col=1)

    win["L1_price"] = win["ema_value"] * (1 + l1_threshold / 100.0)
    fig.add_trace(go.Scatter(
        x=win.index, y=win["L1_price"], name="L1 Threshold",
        line=dict(color=L1_LINE_COLOR, width=1.1, dash="dash"), opacity=0.65,
        hovertemplate=f"L1 ({l1_threshold:.1f}%): %{{y:.2f}}<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[sig_dt], y=[float(ctx["bar"]["close"])],
        mode="markers",
        marker=dict(symbol="diamond", size=14, color=SIGNAL_MARKER,
                    line=dict(color="#E5E7EB", width=1.5)),
        name="Signal", hoverinfo="skip", showlegend=False,
    ), row=1, col=1)

    colors = [CANDLE_UP if c >= o else CANDLE_DOWN
              for o, c in zip(win["open"], win["close"])]
    fig.add_trace(go.Bar(
        x=win.index, y=win["volume"], name="Volume",
        marker_color=colors, marker_line_width=0, opacity=0.65,
    ), row=2, col=1)

    fig.update_layout(height=520, **PLOTLY_LAYOUT)
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig


def build_signal_timeline(ticker_df):
    fig = go.Figure()
    level_colors = {"15m": "#00D1B2", "30m": "#22C55E",
                    "45m": "#C9A227", "60m": "#9CA3AF"}
    for tf in LEVEL_ORDER:
        sub = ticker_df[ticker_df["timeframe"] == tf]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["datetime"], y=[LEVEL_LABEL[tf]] * len(sub),
            mode="markers",
            marker=dict(size=11, color=level_colors[tf],
                        line=dict(color="#0B0F14", width=1)),
            name=LEVEL_LABEL[tf],
            hovertemplate=f"{LEVEL_LABEL[tf]}<br>%{{x|%d %b %H:%M}}<extra></extra>",
        ))
    fig.update_layout(height=160, **PLOTLY_LAYOUT)
    fig.update_yaxes(categoryorder="array",
                     categoryarray=[LEVEL_LABEL[t] for t in reversed(LEVEL_ORDER)])
    return fig


# ─────────────────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────────────────
if not st.session_state.get("entered"):
    st.markdown(f"""
    <div class="land-wrap">
        <div class="land-eyebrow">{BRAND_TAG}</div>
        <h1 class="land-title">{BRAND_NAME}</h1>
        <p class="land-tagline">Institutional-Grade Signal Discovery</p>
        <p class="land-sub">
            A multi-level confluence engine that surfaces high-probability
            exhaustion patterns across four intraday analysis horizons.
        </p>
        <div class="land-stats">
            <div class="land-stat"><div class="num">04</div><div class="lbl">Levels</div></div>
            <div class="land-stat"><div class="num">05</div><div class="lbl">Boosters</div></div>
            <div class="land-stat"><div class="num">250+</div><div class="lbl">Instruments</div></div>
        </div>
        <div class="land-features">
            <div class="land-feature">
                <h4>Multi-Level Confluence</h4>
                <p>Independent detection across four horizons ensures only
                   durable signals reach the surface.</p>
            </div>
            <div class="land-feature">
                <h4>Quant Scoring</h4>
                <p>Every signal is graded 0–100 on quant, exhaustion depth,
                   and Level‑1 confirmation with multi-booster conviction.</p>
            </div>
            <div class="land-feature">
                <h4>Deep Analytics</h4>
                <p>Candlestick overlays, level alignment matrix, and
                   automated analysis for every qualified hit.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1, 1])
    with c:
        if st.button("ENTER PLATFORM", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────
live, status_label = market_status()
pill_cls = "status-live" if live else "status-closed"
dot_cls = "dot-live" if live else "dot-closed"
_rotating_quote = QUOTES[int(time.time() // 30) % len(QUOTES)]

st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">{BRAND_TAG}</div>
    <div class="hero-title">{BRAND_NAME}</div>
    <p class="hero-sub">Multi-level confluence engine · Four intraday analysis horizons</p>
    <div class="status-pill {pill_cls}">
        <span class="dot {dot_cls}"></span> {status_label}
    </div>
    <p class="hero-quote">“{_rotating_quote}”</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# CONTROL PANEL
# ─────────────────────────────────────────────────────────
st.markdown('<div class="control-card">', unsafe_allow_html=True)
st.markdown('<div class="control-title">Scan Configuration</div>', unsafe_allow_html=True)

rc1, rc2 = st.columns([2, 1])
with rc1:
    universe = st.radio(
        "Instrument Universe",
        ["Standard (~190)", "High Volatility (~60)", "Full (~250)"],
        index=2, horizontal=True,
    )
    if universe.startswith("Standard"):
        base = [t.replace(".NS", "") for t in STANDARD_SYMBOLS]
    elif universe.startswith("High"):
        base = [t.replace(".NS", "") for t in HIGH_VOL_SYMBOLS]
    else:
        base = ALL_SYMBOLS
with rc2:
    max_tickers = st.slider("Max Instruments", min_value=10, max_value=len(base),
                             value=len(base), step=10)
tickers = base[:max_tickers]

rc3, rc4 = st.columns([3, 2])
with rc3:
    st.markdown('<div class="section-label">Analysis Levels</div>', unsafe_allow_html=True)
    lvl_cols = st.columns(4)
    lvl_1 = lvl_cols[0].checkbox("Level 1", value=True)
    lvl_2 = lvl_cols[1].checkbox("Level 2", value=True)
    lvl_3 = lvl_cols[2].checkbox("Level 3", value=True)
    lvl_4 = lvl_cols[3].checkbox("Level 4", value=True)
    selected_tfs = [tf for tf, on in
                    [("15m", lvl_1), ("30m", lvl_2),
                     ("45m", lvl_3), ("60m", lvl_4)] if on]
with rc4:
    days_back = st.slider("Look-back Window (days)", 5, 30, 10, 1)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

rc5, rc6 = st.columns([1, 1])
with rc5:
    l1_threshold = st.slider("Level-1 Oversold Threshold (%)",
                              min_value=-5.0, max_value=-1.0,
                              value=-2.0, step=0.25,
                              help="Deviation % below 20-EMA required to qualify as L1 staging.")
with rc6:
    min_boosters = st.slider("Minimum Boosters Required",
                              min_value=2, max_value=6, value=3, step=1,
                              help="S=6, A=5, B=4, C=3. Higher = stricter.")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns([2, 1, 1, 1])
with b1:
    run_btn = st.button("RUN SCAN", use_container_width=True, type="primary")
with b2:
    refresh_btn = st.button("Refresh", use_container_width=True)
with b3:
    clear_btn = st.button("Clear", use_container_width=True)
with b4:
    if st.session_state.get("scan_out"):
        df_now = st.session_state.scan_out["results_df"]
        if not df_now.empty:
            st.download_button(
                "Export", data=to_csv_bytes(df_now),
                file_name=f"signals_{datetime.now():%Y%m%d_%H%M}.csv",
                mime="text/csv", use_container_width=True,
            )
st.markdown('</div>', unsafe_allow_html=True)

if clear_btn:
    st.session_state.scan_out = None
    st.rerun()
if refresh_btn:
    st.cache_data.clear()
    st.session_state.scan_out = None
    st.success("Cache cleared. Next scan will pull fresh data.")


# ─────────────────────────────────────────────────────────
# RUN SCAN
# ─────────────────────────────────────────────────────────
if "scan_out" not in st.session_state:
    st.session_state.scan_out = None

if run_btn:
    if not selected_tfs:
        st.error("Select at least one level.")
        st.stop()
    if not tickers:
        st.error("No instruments selected.")
        st.stop()
    fetch_slot = st.empty()
    fetch_slot.info(f"Fetching data for {len(tickers)} instruments…")
    batch_data, fetch_err = cached_batch(tuple(tickers))
    if fetch_err:
        fetch_slot.empty(); st.error(f"Fetch failed: {fetch_err}"); st.stop()
    if not batch_data:
        fetch_slot.empty(); st.error("No data returned. Try Refresh."); st.stop()
    fetch_slot.success(f"{len(batch_data)}/{len(tickers)} loaded. Processing…")
    progress = st.progress(0.0, text="Detecting signals…")
    status_slot = st.empty()

    def _prog(p):
        progress.progress(min(p, 1.0), text=f"Scanning… {int(p*100)}%")

    def _tick(name, n):
        if n > 0:
            status_slot.success(f"{name} — {n} qualified")
        else:
            status_slot.info(f"{name}")

    out = process_batch(batch_data, selected_tfs, days_back=days_back,
                        l1_threshold=l1_threshold, min_boosters=min_boosters,
                        progress_cb=_prog, ticker_cb=_tick)
    progress.empty(); status_slot.empty(); fetch_slot.empty()

    st.session_state.scan_out = out
    st.session_state.scan_meta = {
        "tickers_scanned": len(batch_data),
        "timeframes": selected_tfs,
        "days_back": days_back,
        "l1_threshold": l1_threshold,
        "min_boosters": min_boosters,
    }
    st.success(f"Scan complete — {len(out['results_df'])} signal(s) in {out['scan_time_s']}s.")


# ─────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────
out = st.session_state.scan_out
if out is None:
    st.info("Configure the scan above, then click RUN SCAN.")
    st.stop()

df = out["results_df"]
diag = out["diag"]
meta = st.session_state.get("scan_meta", {})
levels_str = " · ".join([LEVEL_LABEL[t] for t in meta.get("timeframes", [])])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Instruments Scanned", meta.get("tickers_scanned", 0))
k2.metric("Signals Detected", len(df),
          delta=f"{df['ticker'].nunique()} unique" if len(df) else "none")
k3.metric("Scan Duration", f"{out['scan_time_s']}s")
k4.metric("Active Levels", levels_str)

tab_sig, tab_chart, tab_perf, tab_diag, tab_err = st.tabs(
    ["SIGNALS", "CHART", "PERFORMANCE", "ANALYTICS", "NOTES"]
)


# ─── TAB 1: SIGNALS ─────────────────────────────────────
with tab_sig:
    if df.empty:
        st.info(f"No signals detected in the last {meta.get('days_back', 10)} days.")
    else:
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            tf_f = st.multiselect("Level",
                options=sorted(df["timeframe"].unique().tolist()),
                default=sorted(df["timeframe"].unique().tolist()),
                format_func=lambda x: LEVEL_LABEL.get(x, x))
        with f2:
            tier_f = st.multiselect("Tier",
                options=["S", "A", "B", "C"],
                default=["S", "A", "B", "C"])
        with f3:
            tk_f = st.multiselect("Instrument",
                sorted(df["ticker"].unique().tolist()),
                default=[], placeholder="All instruments")
        with f4:
            min_bias = st.slider("Max Bias Threshold",
                float(df["raw_di_diff"].min()), 0.0, 0.0)

        filt = df[df["timeframe"].isin(tf_f) & df["tier"].isin(tier_f)
                  & (df["raw_di_diff"] <= min_bias)]
        if tk_f:
            filt = filt[filt["ticker"].isin(tk_f)]
        filt = filt.sort_values(["conviction", "datetime"], ascending=[False, False])

        disp = filt.copy().reset_index(drop=True)
        disp.insert(0, "Rank", range(1, len(disp) + 1))
        disp["Timestamp"] = disp["datetime"].dt.strftime("%d %b %Y · %H:%M")
        disp["Instrument"] = disp["ticker"]
        disp["Level"] = disp["timeframe"].map(LEVEL_LABEL)
        disp["Last Price"] = disp["close"].round(2)
        disp["Deviation"] = disp["distance_pct"].round(2)
        disp["Bias"] = disp["raw_di_diff"].round(2)
        # ── FIX: alias lowercase source columns to display columns ──
        disp["Tier"] = disp["tier"].astype(str)
        disp["Conviction"] = disp["conviction"].astype(int)

        cols_show = ["Rank", "Timestamp", "Instrument", "Level", "Tier",
                     "Conviction", "Last Price", "Deviation", "Bias"]
        disp = disp[cols_show]

        def _style_row(row):
            tier = str(row["Tier"])
            color = TIER_COLORS.get(tier, "#9CA3AF")
            bg = {"S": "rgba(201,162,39,0.14)", "A": "rgba(34,197,94,0.10)",
                  "B": "rgba(0,209,178,0.08)"}.get(tier, "")
            styles = []
            for col in row.index:
                if col == "Tier":
                    styles.append(f'background-color:{bg};color:{color};font-weight:700')
                elif bg and tier in ["S", "A"]:
                    styles.append(f'background-color:{bg};color:#E5E7EB')
                else:
                    styles.append('')
            return styles

        styled = disp.style.apply(_style_row, axis=1)
        st.dataframe(
            styled, use_container_width=True, hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("#", width="small"),
                "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                "Instrument": st.column_config.TextColumn("Instrument", width="small"),
                "Level": st.column_config.TextColumn("Level", width="small"),
                "Tier": st.column_config.TextColumn("Tier", width="small"),
                "Conviction": st.column_config.NumberColumn("Conv", format="%d", width="small"),
                "Last Price": st.column_config.NumberColumn("Last", format="%.2f", width="small"),
                "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%", width="small"),
                "Bias": st.column_config.NumberColumn("Bias", format="%.2f", width="small"),
            },
        )
        st.caption("Sorted by Conviction (highest first). Tier colours: "
                   "S=gold · A=green · B=teal · C=grey.")


# ─── TAB 2: CHART ───────────────────────────────────────
with tab_chart:
    if df.empty:
        st.info("No signals available — run a scan with at least one qualified hit.")
    else:
        labels = df.apply(
            lambda r: f"[{r['tier']}] {r['ticker']} · {LEVEL_LABEL[r['timeframe']]} · "
                      f"{r['datetime']:%d %b %Y %H:%M}", axis=1).tolist()
        pick = st.selectbox("Select a signal", labels, key="chart_pick")
        idx = labels.index(pick)
        row = df.iloc[idx]

        data, ferr = cached_batch((row["ticker"],))
        if ferr or row["ticker"] not in data:
            st.error(f"Could not load data for {row['ticker']}. Try refreshing.")
        else:
            raw = data[row["ticker"]].copy()
            if not isinstance(raw.index, pd.DatetimeIndex):
                raw.index = pd.to_datetime(raw.index)
            if raw.index.tz is None:
                raw.index = raw.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
            else:
                raw.index = raw.index.tz_convert("Asia/Kolkata")
            rule = TIMEFRAME_MAP[row["timeframe"]]
            rs = raw.resample(rule, origin="start_day", offset="9h15min",
                              label="left", closed="left").agg({
                                  "open": "first", "high": "max", "low": "min",
                                  "close": "last", "volume": "sum"}).dropna()
            scanned = detect_signals(rs, meta.get("l1_threshold", -2.0))
            ctx = compute_signal_context(scanned, row)
            mtf = get_current_mtf_state(raw, meta.get("l1_threshold", -2.0))

            q1, q2, q3, q4, q5 = st.columns(5)
            q1.metric("Tier", row["tier"],
                      f"{int(row['booster_pts'])}/6 boosters")
            q2.metric("Conviction", f"{int(row['conviction'])}/100")
            q3.metric("Deviation", f"{ctx['dev']:.2f}%")
            q4.metric("Bias", f"{ctx['bias']:.2f}")
            q5.metric("Bars Since", ctx["bars_since"], f"{ctx['change_since']:+.2f}%")

            st.markdown("#### Confluence Boosters")
            bcols = st.columns(5)
            checks = [
                ("Multi-TF Agreement", f"{int(row['mtf_agree'])} TF",
                 int(row['mtf_agree']) >= 1,
                 f"{'✓' if row['mtf_agree']>=2 else ('~' if row['mtf_agree']==1 else '✗')}"),
                ("Volume Footprint", "Dry→Surge",
                 bool(row["vol_footprint"]),
                 "✓" if row["vol_footprint"] else "✗"),
                ("Candle Strength", f"{ctx['candle_pos']*100:.0f}%",
                 bool(row["candle_strong"]),
                 "✓" if row["candle_strong"] else "✗"),
                ("Momentum Decel", "Improving",
                 bool(row["mom_decel"]),
                 "✓" if row["mom_decel"] else "✗"),
                ("Near Support", f"{ctx['dist_to_low_atr']:.1f}×ATR",
                 bool(row["near_support"]),
                 "✓" if row["near_support"] else "✗"),
            ]
            for col, (name, val, ok, mark) in zip(bcols, checks):
                with col:
                    color = "#22C55E" if ok else "#EF4444"
                    st.markdown(
                        f"<div style='background:#121821;border:1px solid #1F2937;"
                        f"border-left:3px solid {color};border-radius:6px;"
                        f"padding:10px 12px;'>"
                        f"<div style='font-size:10px;color:#9CA3AF;letter-spacing:0.08em;"
                        f"text-transform:uppercase;font-weight:600;'>{name}</div>"
                        f"<div style='font-family:JetBrains Mono,monospace;color:{color};"
                        f"font-size:16px;font-weight:700;margin-top:4px;'>"
                        f"{mark} {val}</div></div>",
                        unsafe_allow_html=True)

            st.markdown("#### Price Action · Signal Overlay")
            fig = build_pro_chart(scanned, row, ctx,
                                   l1_threshold=meta.get("l1_threshold", -2.0),
                                   window_days=7)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": True, "displaylogo": False})
            else:
                st.warning("No price bars available around this signal.")

            st.markdown("#### Level Alignment Matrix")
            mtf_rows = []
            for tf_name in LEVEL_ORDER:
                state = mtf.get(tf_name)
                if state is None:
                    mtf_rows.append({"Level": LEVEL_LABEL[tf_name], "Status": "—",
                                     "Bias": "—", "Deviation": "—", "Quant Score": "—"})
                else:
                    mtf_rows.append({"Level": LEVEL_LABEL[tf_name],
                                     "Status": state["status"],
                                     "Bias": round(state["bias"], 2),
                                     "Deviation": round(state["dev"], 2),
                                     "Quant Score": round(state["vol_score"], 0)})
            mtf_df = pd.DataFrame(mtf_rows)

            def _style_status(val):
                v = str(val)
                if v == "Active":
                    return "background-color:rgba(34,197,94,0.12);color:#22C55E;font-weight:600;"
                if v == "Exhaustion":
                    return "background-color:rgba(245,158,11,0.12);color:#F59E0B;font-weight:600;"
                if v == "Bias Only":
                    return "background-color:rgba(0,209,178,0.10);color:#00D1B2;font-weight:600;"
                if v == "Quiet":
                    return "color:#9CA3AF;"
                return ""

            styled_mtf = mtf_df.style.map(_style_status, subset=["Status"])
            st.dataframe(
                styled_mtf, use_container_width=True, hide_index=True,
                column_config={
                    "Level": st.column_config.TextColumn("Level", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="medium"),
                    "Bias": st.column_config.NumberColumn("Bias", format="%.2f"),
                    "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%"),
                    "Quant Score": st.column_config.NumberColumn("Quant Score", format="%.0f"),
                },
            )

            ticker_hist = df[df["ticker"] == row["ticker"]].copy()
            if len(ticker_hist) >= 1:
                st.markdown("#### Signal History · This Instrument")
                timeline_fig = build_signal_timeline(ticker_hist)
                st.plotly_chart(timeline_fig, use_container_width=True,
                                config={"displayModeBar": False})

            st.markdown("#### Swing Context")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Recent High", f"{ctx['recent_high']:.2f}",
                      f"{ctx['dist_from_high']:.2f}%")
            s2.metric("Recent Low", f"{ctx['recent_low']:.2f}",
                      f"{ctx['dist_from_low']:+.2f}%")
            s3.metric("Bars Since Signal", ctx["bars_since"])
            s4.metric("Change Since", f"{ctx['change_since']:+.2f}%")

            related = df[df["ticker"] == row["ticker"]].copy()
            if len(related) > 1:
                related = related.drop(df.index[idx]) if idx in df.index else related
                if not related.empty:
                    st.markdown("#### Related Signals · Same Instrument")
                    rel = related.reset_index(drop=True)
                    rel.insert(0, "Rank", range(1, len(rel) + 1))
                    rel["Timestamp"] = rel["datetime"].dt.strftime("%d %b %Y · %H:%M")
                    rel["Level"] = rel["timeframe"].map(LEVEL_LABEL)
                    rel["Last Price"] = rel["close"].round(2)
                    rel["Deviation"] = rel["distance_pct"].round(2)
                    rel["Bias"] = rel["raw_di_diff"].round(2)
                    # ── FIX: alias lowercase tier → display column ──
                    rel["Tier"] = rel["tier"].astype(str)
                    st.dataframe(
                        rel[["Rank", "Timestamp", "Level", "Tier",
                             "Last Price", "Deviation", "Bias"]],
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Rank": st.column_config.NumberColumn("#", width="small"),
                            "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                            "Level": st.column_config.TextColumn("Level", width="small"),
                            "Tier": st.column_config.TextColumn("Tier", width="small"),
                            "Last Price": st.column_config.NumberColumn("Last", format="%.2f"),
                            "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%"),
                            "Bias": st.column_config.NumberColumn("Bias", format="%.2f"),
                        },
                    )


# ─── TAB 3: PERFORMANCE ────────────────────────────────
with tab_perf:
    st.markdown("### Win Rate by Tier")
    if df.empty:
        st.info("No signals to evaluate. Run a scan first.")
    else:
        closed = df[df["outcome_status"].isin(["Target Hit", "Stop Hit", "Open"])].copy()
        if closed.empty:
            st.info("Not enough completed outcomes yet. "
                    "Outcomes require 20 bars after signal.")
        else:
            def _hit(row):
                return 1 if row["outcome_status"] == "Target Hit" else (
                    1 if row["outcome_status"] == "Open" and (row["outcome_r"] or 0) > 0 else 0)

            closed["is_win"] = closed.apply(_hit, axis=1)

            p1, p2, p3, p4 = st.columns(4)
            total_closed = len(closed)
            overall_wr = closed["is_win"].mean() * 100 if total_closed else 0
            avg_r = closed["outcome_r"].dropna().mean() if total_closed else 0
            s_tier = closed[closed["tier"] == "S"]
            s_wr = s_tier["is_win"].mean() * 100 if len(s_tier) else 0
            p1.metric("Closed Signals", total_closed)
            p2.metric("Overall Win Rate", f"{overall_wr:.1f}%")
            p3.metric("Avg R", f"{avg_r:+.2f}" if not pd.isna(avg_r) else "—")
            p4.metric("S-Tier Win Rate", f"{s_wr:.1f}%")

            breakdown = []
            for tier in ["S", "A", "B", "C"]:
                sub = closed[closed["tier"] == tier]
                n = len(sub)
                wr = sub["is_win"].mean() * 100 if n else 0
                r_avg = sub["outcome_r"].dropna().mean() if n else 0
                breakdown.append({
                    "Tier": tier, "Count": n,
                    "Win Rate %": round(wr, 1),
                    "Avg R": round(r_avg, 2) if not pd.isna(r_avg) else 0.0,
                })
            br_df = pd.DataFrame(breakdown)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=br_df["Tier"], y=br_df["Win Rate %"],
                marker_color=[TIER_COLORS.get(t, "#9CA3AF") for t in br_df["Tier"]],
                text=[f"{v:.1f}%" for v in br_df["Win Rate %"]],
                textposition="outside",
                textfont=dict(family="JetBrains Mono, monospace", size=12),
            ))
            fig.update_layout(
                height=280, **PLOTLY_LAYOUT,
                yaxis=dict(range=[0, 100], gridcolor="#1F2937"),
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            st.dataframe(br_df, use_container_width=True, hide_index=True)
            st.caption(
                "Win = Target Hit (1R) or positive Open R. "
                "Stop Hit = −1R. Window = 20 bars post-signal."
            )


# ─── TAB 4: ANALYTICS ──────────────────────────────────
with tab_diag:
    st.markdown("### Detection Funnel")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Core Matches", diag["stage_core"])
    d2.metric("With L1 Staging", diag["stage_final"])
    d3.metric("Qualified (≥min boosters)",
              sum(diag["tier_counts"].values()))
    d4.metric("No Data", diag["empty_data"])

    st.markdown("### Tier Distribution")
    tc = diag["tier_counts"]
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("S-Tier", tc.get("S", 0))
    t2.metric("A-Tier", tc.get("A", 0))
    t3.metric("B-Tier", tc.get("B", 0))
    t4.metric("C-Tier", tc.get("C", 0))

    st.caption(
        f"Window cutoff: {out['cutoff']} · Duration: {out['scan_time_s']}s · "
        f"Instruments processed: {out.get('tickers_processed', 0)} · "
        f"L1 threshold: {meta.get('l1_threshold', -2.0):.2f}% · "
        f"Min boosters: {meta.get('min_boosters', 3)}"
    )


# ─── TAB 5: NOTES ──────────────────────────────────────
with tab_err:
    if not out["errors"]:
        st.success("No exceptions — all instruments processed cleanly.")
    else:
        st.warning(f"{len(out['errors'])} instrument(s) returned a processing note.")
        st.dataframe(pd.DataFrame(out["errors"], columns=["Instrument", "Note"]),
                     use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="fintrix-footer">
    <div class="brand">{BRAND_NAME}</div>
    <div class="tag">{BRAND_TAG}</div>
</div>
""", unsafe_allow_html=True)
