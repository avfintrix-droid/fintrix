# ============================================================
# FINTRIX ANALYTICS · Signal Intelligence + Small-Cap Coiled Screener
# Two independent modules · Shared dark institutional UI
# ============================================================
import numpy as np
import pandas as pd
import yfinance as yf
import warnings
import time
import io
import logging
import contextlib
import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")
for _n in ('yfinance', 'urllib3', 'peewee', 'requests'):
    logging.getLogger(_n).setLevel(logging.CRITICAL)
    logging.getLogger(_n).propagate = False

# ─────────────────────────────────────────────────────────
# PLOTLY TEMPLATE (inlined — no external file)
# ─────────────────────────────────────────────────────────
PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "#0B0F14",
    "font": {"family": "Inter, -apple-system, sans-serif",
             "color": "#E5E7EB", "size": 11},
    "xaxis": {"gridcolor": "#1F2937", "gridwidth": 0.5, "linecolor": "#1F2937",
              "zeroline": False,
              "tickfont": {"family": "JetBrains Mono, monospace",
                           "color": "#9CA3AF", "size": 10},
              "showspikes": False},
    "yaxis": {"gridcolor": "#1F2937", "gridwidth": 0.5, "linecolor": "#1F2937",
              "zeroline": False,
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
    "showlegend": False, "hovermode": "x unified", "dragmode": "pan",
}

CANDLE_UP = "#22C55E"
CANDLE_DOWN = "#EF4444"
EMA_PRIMARY = "#00D1B2"
EMA_SECONDARY = "#C9A227"
SIGNAL_MARKER = "#C9A227"

BRAND_NAME = "FINTRIX ANALYTICS"
BRAND_TAG = "INSTITUTIONAL SIGNAL INTELLIGENCE"

LEVEL_LABEL = {"15m": "Level 1", "30m": "Level 2", "45m": "Level 3", "60m": "Level 4"}
LEVEL_ORDER = ["15m", "30m", "45m", "60m"]

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fintrix Analytics · Signal Intelligence",
    page_icon="◆", layout="wide", initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
# INSTITUTIONAL CSS (unchanged from FINTRIX)
# ─────────────────────────────────────────────────────────
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
.land-feature h4{color:var(--text-primary);font-size:0.88rem;margin:0 0 8px 0;font-weight:600;}
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
[data-testid="stMetricLabel"]{color:var(--text-muted)!important;font-size:10px!important;
    letter-spacing:0.08em!important;text-transform:uppercase!important;font-weight:600!important;}
[data-testid="stMetricValue"]{color:var(--text-primary)!important;
    font-family:'JetBrains Mono',monospace!important;font-weight:600!important;
    font-size:1.6rem!important;}
[data-testid="stMetricDelta"]{font-family:'JetBrains Mono',monospace!important;
    font-size:11px!important;font-weight:500!important;}
.stButton>button{border-radius:6px;font-weight:600;font-size:12px;
    letter-spacing:0.06em;text-transform:uppercase;padding:0.65rem 1.2rem;
    transition:all 150ms ease;border:1px solid var(--border);
    background:transparent;color:var(--text-primary)!important;}
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
.stSelectbox label,.stMultiSelect label,.stSlider label,.stRadio label,.stTextInput label,
.stNumberInput label,.stFileUploader label,.stCheckbox label{
    color:var(--text-muted)!important;font-weight:500!important;
    font-size:11px!important;letter-spacing:0.06em!important;text-transform:uppercase!important;}
[data-baseweb="select"]>div{background:var(--bg-elevated)!important;
    border:1px solid var(--border)!important;border-radius:6px!important;
    color:var(--text-primary)!important;}
[data-baseweb="select"]>div:focus-within{border-color:var(--accent-teal)!important;
    box-shadow:0 0 0 2px rgba(0,209,178,0.15)!important;}
[data-baseweb="tag"]{background:rgba(0,209,178,0.15)!important;
    color:var(--accent-teal)!important;border:1px solid rgba(0,209,178,0.3)!important;}
[data-baseweb="tag"] span{color:var(--accent-teal)!important;}
.stSlider [data-baseweb="slider"] [role="slider"]{background:var(--accent-teal)!important;
    border:2px solid var(--bg-panel)!important;
    box-shadow:0 0 0 1px var(--accent-teal)!important;}
.stRadio [role="radiogroup"] label{text-transform:none!important;letter-spacing:0!important;
    font-size:13px!important;color:var(--text-primary)!important;}
.stRadio [role="radiogroup"] label[data-checked="true"]{color:var(--accent-teal)!important;}
.stCheckbox label{color:var(--text-primary)!important;font-size:13px!important;
    text-transform:none!important;letter-spacing:0!important;}
.stTabs [data-baseweb="tab-list"]{gap:0;border-bottom:1px solid var(--border);padding-bottom:0;}
.stTabs [data-baseweb="tab"]{color:var(--text-muted);font-weight:600;font-size:11px;
    letter-spacing:0.08em;text-transform:uppercase;padding:12px 20px;
    border-bottom:2px solid transparent;
    transition:color 150ms ease,border-color 150ms ease;}
.stTabs [data-baseweb="tab"]:hover{color:var(--text-primary);}
.stTabs [aria-selected="true"]{color:var(--accent-teal)!important;
    border-bottom:2px solid var(--accent-teal)!important;background:transparent!important;}
h2,h3,h4{color:var(--text-primary)!important;letter-spacing:-0.01em;font-weight:600!important;}
h2{font-size:16px!important;margin-top:1.4rem!important;padding-bottom:10px;
    border-bottom:1px solid var(--border);}
h3{font-size:14px!important;}
h4{font-size:13px!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;
    border-radius:8px!important;overflow:hidden!important;
    background:var(--bg-panel)!important;}
[data-testid="stDataFrame"] [role="columnheader"]{background:var(--bg-elevated)!important;
    color:var(--text-muted)!important;font-size:10px!important;font-weight:600!important;
    letter-spacing:0.08em!important;text-transform:uppercase!important;
    border-bottom:1px solid var(--border)!important;padding:10px 12px!important;}
[data-testid="stDataFrame"] [role="gridcell"]{font-family:'JetBrains Mono',monospace!important;
    font-size:12px!important;color:var(--text-primary)!important;
    padding:8px 12px!important;border-bottom:1px solid rgba(31,41,55,0.5)!important;}
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
    .land-tagline{font-size:0.9rem!important;margin:20px 0 10px 0;}
    .land-sub{font-size:0.85rem!important;line-height:1.6!important;}
    .land-stats{margin-top:32px;max-width:100%;}
    .land-stat{padding:16px 20px;min-width:100px;}
    .land-stat .num{font-size:1.4rem;}
    .land-features{grid-template-columns:1fr;margin-top:32px;}
    .hero-wrap{padding:18px 20px!important;}
    .hero-title{font-size:18px!important;}
    .control-card{padding:16px 18px!important;}
    [data-testid="stMetric"]{padding:12px 14px!important;}
    [data-testid="stMetricValue"]{font-size:1.3rem!important;}
    .stButton>button{padding:0.7rem 1rem!important;font-size:11px!important;
        min-height:42px!important;}
    .stTabs [data-baseweb="tab"]{font-size:10px!important;padding:9px 10px!important;}
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# FINTRIX MODULE — universes
# ============================================================
STANDARD_SYMBOLS = [
    "AARTIIND.NS","ABB.NS","ABBOTINDIA.NS","ABCAPITAL.NS","ABFRL.NS",
    "ACC.NS","ADANIENT.NS","ADANIGREEN.NS","ADANIPORTS.NS","ADANIENSOL.NS",
    "ADANIPOWER.NS","ALKEM.NS","AMBUJACEM.NS","APOLLOHOSP.NS","APOLLOTYRE.NS",
    "ASHOKLEY.NS","ASIANPAINT.NS","ASTRAL.NS","ATUL.NS","AUBANK.NS",
    "AUROPHARMA.NS","AXISBANK.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS",
    "BALKRISIND.NS","BALRAMCHIN.NS","BANDHANBNK.NS","BANKBARODA.NS","BATAINDIA.NS",
    "BEL.NS","BERGEPAINT.NS","BHARATFORG.NS","BHARTIARTL.NS","BHEL.NS",
    "BIOCON.NS","BOSCHLTD.NS","BPCL.NS","BRITANNIA.NS","BSOFT.NS",
    "CANBK.NS","CANFINHOME.NS","CHAMBLFERT.NS","CHOLAFIN.NS","CIPLA.NS",
    "COALINDIA.NS","COFORGE.NS","COLPAL.NS","CONCOR.NS","COROMANDEL.NS",
    "CROMPTON.NS","CUMMINSIND.NS","CYIENT.NS","DABUR.NS","DALBHARAT.NS",
    "DEEPAKNTR.NS","DELHIVERY.NS","DIVISLAB.NS","DLF.NS","DRREDDY.NS",
    "EICHERMOT.NS","ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","FORTIS.NS",
    "GAIL.NS","GLENMARK.NS","GMRINFRA.NS","GODREJCP.NS","GODREJPROP.NS",
    "GRANULES.NS","GRASIM.NS","GUJGASLTD.NS","HAL.NS","HAVELLS.NS",
    "HCLTECH.NS","HDFCBANK.NS","HDFCLIFE.NS","HEROMOTOCO.NS","HINDALCO.NS",
    "HINDCOPPER.NS","HINDPETRO.NS","HINDUNILVR.NS","ICICIBANK.NS","ICICIGI.NS",
    "ICICIPRULI.NS","IDEA.NS","IDFCFIRSTB.NS","IEX.NS","IGL.NS",
    "INDHOTEL.NS","INDIACEM.NS","INDIAMART.NS","INDIGO.NS","INDUSINDBK.NS",
    "INDUSTOWER.NS","INFY.NS","IOC.NS","IPCALAB.NS","IRCTC.NS",
    "IRFC.NS","ITC.NS","JINDALSTEL.NS","JIOFIN.NS","JKCEMENT.NS",
    "JSWENERGY.NS","JSWSTEEL.NS","JUBLFOOD.NS","KALYANKJIL.NS","KEI.NS",
    "KFINTECH.NS","KOTAKBANK.NS","KPITTECH.NS","LALPATHLAB.NS","LICHSGFIN.NS",
    "LICI.NS","LTIM.NS","LT.NS","LTTS.NS","LUPIN.NS",
    "M&M.NS","M&MFIN.NS","MANAPPURAM.NS","MARICO.NS","MARUTI.NS",
    "MAXHEALTH.NS","METROBRAND.NS","MCX.NS","MOTHERSON.NS","MPHASIS.NS",
    "MRF.NS","MUTHOOTFIN.NS","NATIONALUM.NS","NAUKRI.NS","NAVINFLUOR.NS",
    "NESTLEIND.NS","NHPC.NS","NMDC.NS","NTPC.NS","OBEROIRLTY.NS",
    "OFSS.NS","OIL.NS","ONGC.NS","PAGEIND.NS","PAYTM.NS",
    "PEL.NS","PERSISTENT.NS","PETRONET.NS","PFC.NS","PHOENIXLTD.NS",
    "PIDILITIND.NS","PIIND.NS","PNB.NS","POLYCAB.NS","POWERGRID.NS",
    "PRESTIGE.NS","PVRINOX.NS","RAMCOCEM.NS","RBLBANK.NS","RECLTD.NS",
    "RELIANCE.NS","RVNL.NS","SAIL.NS","SBICARD.NS","SBILIFE.NS",
    "SBIN.NS","SHREECEM.NS","SHRIRAMFIN.NS","SIEMENS.NS","SOLARINDS.NS",
    "SONACOMS.NS","SRF.NS","SUNPHARMA.NS","SUNTV.NS","SUPREMEIND.NS",
    "SUZLON.NS","SYNGENE.NS","TATACOMM.NS","TATACONSUM.NS","TATAELXSI.NS",
    "TATAMOTORS.NS","TATAPOWER.NS","TATASTEEL.NS","TCS.NS","TECHM.NS",
    "TIINDIA.NS","TITAN.NS","TORNTPHARM.NS","TORNTPOWER.NS","TRENT.NS",
    "TRIDENT.NS","TVSMOTOR.NS","UBL.NS","ULTRACEMCO.NS","UNIONBANK.NS",
    "UNOMINDA.NS","UPL.NS","VBL.NS","VEDL.NS","VOLTAS.NS",
    "WIPRO.NS","YESBANK.NS","ZEEL.NS","ZOMATO.NS","ZYDUSLIFE.NS"
]
HIGH_VOL_SYMBOLS = [
    "BSE.NS","MCX.NS","RVNL.NS","MAZDOCK.NS","BHEL.NS",
    "GODREJPROP.NS","PRESTIGE.NS","DLF.NS","PFC.NS","RECLTD.NS",
    "SUZLON.NS","IDEA.NS","ZOMATO.NS","PAYTM.NS","IRFC.NS",
    "GMRINFRA.NS","SAIL.NS","TATACOMM.NS","MOTHERSON.NS","ADANIENT.NS",
    "ADANIPOWER.NS","ADANIGREEN.NS","ADANIENSOL.NS","NATIONALUM.NS","HINDCOPPER.NS",
    "IRB.NS","INDUSTOWER.NS","BANDHANBNK.NS","PNB.NS","BANKBARODA.NS",
    "CANBK.NS","IDFCFIRSTB.NS","RBLBANK.NS","UNIONBANK.NS","ABCAPITAL.NS",
    "JIOFIN.NS","GVT&D.NS","INOXWIND.NS","VOLTAS.NS","CHOLAFIN.NS",
    "SHRIRAMFIN.NS","TRENT.NS","HAL.NS","BEL.NS","COCHINSHIP.NS",
    "TATAMOTORS.NS","TVSMOTOR.NS","ASHOKLEY.NS","BHARATFORG.NS","HINDALCO.NS",
    "JINDALSTEL.NS","JSWENERGY.NS","POLYCAB.NS","KEI.NS","KPITTECH.NS",
    "COFORGE.NS","EXIDEIND.NS","FORTIS.NS","GLENMARK.NS","BIOCON.NS"
]
ALL_SYMBOLS = list(dict.fromkeys(
    [t.replace(".NS", "") for t in (STANDARD_SYMBOLS + HIGH_VOL_SYMBOLS)]
))
TIMEFRAME_MAP = {"15m": "15min", "30m": "30min", "45m": "45min", "60m": "60min"}


# ============================================================
# FINTRIX helpers (unchanged)
# ============================================================
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

def detect_signals(df):
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

    results["signal_final"] = (
        results["option_bottom_confirmed"] & (results["raw_di_diff"] < -10)
    )
    return results

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
            if sym not in available: continue
            df = raw[sym].dropna(how="all")
            if df.empty: continue
            df.columns = [str(c).lower() for c in df.columns]
            out[sym.replace(".NS", "")] = df
    else:
        if len(symbols) == 1 and not raw.dropna(how="all").empty:
            df = raw.dropna(how="all")
            df.columns = [str(c).lower() for c in df.columns]
            out[symbols[0].replace(".NS", "")] = df
    return out, None

def process_batch(batch_data, timeframes, days_back=10,
                  progress_cb=None, ticker_cb=None):
    t0 = time.time()
    tf_map = [(tf, TIMEFRAME_MAP[tf]) for tf in timeframes if tf in TIMEFRAME_MAP]
    all_results, errors = [], []
    diag_total = {"empty_data": 0, "stage_a": 0, "stage_b": 0, "final": 0}

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
            ticker_signals = 0
            for tf_name, resample_rule in tf_map:
                resampled = raw.resample(
                    resample_rule, origin="start_day", offset="9h15min",
                    label="left", closed="left",
                ).agg({"open": "first", "high": "max",
                       "low": "min", "close": "last", "volume": "sum"}).dropna()
                if len(resampled) < 100: continue
                if is_live_market and len(resampled) > 1:
                    resampled = resampled.iloc[:-1]
                scanned = detect_signals(resampled)
                diag_total["stage_a"] += int(scanned["option_bottom_confirmed"].sum())
                diag_total["stage_b"] += int((scanned["raw_di_diff"] < -10).sum())
                diag_total["final"] += int(scanned["signal_final"].sum())
                sigs = scanned[scanned["signal_final"]].copy()
                if not sigs.empty:
                    idx_name = sigs.index.name or "datetime"
                    sigs = sigs.reset_index().rename(columns={idx_name: "datetime"})
                    sigs["ticker"] = ticker
                    sigs["timeframe"] = tf_name
                    cols_out = ["datetime", "ticker", "timeframe", "close",
                                "distance_pct", "raw_di_diff"]
                    all_results.append(sigs[cols_out])
                    ticker_signals += len(sigs)
            if ticker_cb: ticker_cb(ticker, ticker_signals)
        except Exception as e:
            errors.append((ticker, str(e)))
        if progress_cb: progress_cb(i / total)

    elapsed = round(time.time() - t0, 1)
    if all_results:
        df = pd.concat(all_results, ignore_index=True)
        df = df[df["datetime"].dt.date >= cutoff]
    else:
        df = pd.DataFrame(columns=["datetime", "ticker", "timeframe",
                                   "close", "distance_pct", "raw_di_diff"])
    return {"results_df": df, "diag": diag_total, "errors": errors,
            "scan_time_s": elapsed, "cutoff": cutoff,
            "tickers_processed": len(items)}

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
    return df.to_csv(index=False).encode("utf-8")

@st.cache_data(ttl=600, show_spinner=False)
def cached_batch(tickers_tuple):
    return batch_fetch(list(tickers_tuple), period="60d", interval="15m")

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
    return {"vol_ratio": vol_ratio, "vol_score": vol_score,
            "dev": dev, "bias": bias,
            "quality": quality, "quality_label": label,
            "dist_from_high": dist_from_high, "dist_from_low": dist_from_low,
            "bars_since": int(bars_since), "change_since": float(change_since),
            "sig_pos": int(sig_pos), "bar": bar,
            "recent_high": recent_high, "recent_low": recent_low}

def get_current_mtf_state(raw):
    result = {}
    for tf_name, rule in TIMEFRAME_MAP.items():
        try:
            rs = raw.resample(rule, origin="start_day", offset="9h15min",
                              label="left", closed="left").agg({
                                  "open": "first", "high": "max", "low": "min",
                                  "close": "last", "volume": "sum"}).dropna()
            if len(rs) < 100:
                result[tf_name] = None; continue
            scanned = detect_signals(rs)
            last = scanned.iloc[-1]
            vma = last.get("vol_ma", np.nan)
            vol_ratio = float(last["volume"] / vma) if (vma and vma > 0) else 0.0
            vol_score = min(100.0, max(0.0, (vol_ratio - 2.0) / 4.0 * 100))
            if bool(last["signal_final"]):        status = "Active"
            elif bool(last["option_bottom_confirmed"]): status = "Exhaustion"
            elif float(last["raw_di_diff"]) < -10: status = "Bias Only"
            else:                                 status = "Quiet"
            result[tf_name] = {"status": status,
                               "signal": bool(last["signal_final"]),
                               "bias": float(last["raw_di_diff"]),
                               "dev": float(last["distance_pct"]),
                               "vol_ratio": vol_ratio, "vol_score": vol_score}
        except Exception:
            result[tf_name] = None
    return result

def build_pro_chart(scanned, row, ctx, window_days=7):
    sig_dt = row["datetime"]
    start = sig_dt - pd.Timedelta(days=window_days)
    end   = sig_dt + pd.Timedelta(days=2)
    win = scanned.loc[(scanned.index >= start) & (scanned.index <= end)].copy()
    if win.empty: return None
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, row_heights=[0.74, 0.26])
    fig.add_trace(go.Candlestick(
        x=win.index, open=win["open"], high=win["high"],
        low=win["low"], close=win["close"], name="Price",
        increasing_line_color=CANDLE_UP, decreasing_line_color=CANDLE_DOWN,
        increasing_fillcolor="rgba(34,197,94,0.35)",
        decreasing_fillcolor="rgba(239,68,68,0.35)"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=win.index, y=win["ema_value"], name="Baseline",
        line=dict(color=EMA_PRIMARY, width=1.5), opacity=0.9,
        hovertemplate="Baseline: %{y:.2f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[sig_dt], y=[float(ctx["bar"]["close"])], mode="markers",
        marker=dict(symbol="diamond", size=14, color=SIGNAL_MARKER,
                    line=dict(color="#E5E7EB", width=1.5)),
        name="Signal", hoverinfo="skip", showlegend=False), row=1, col=1)
    colors = [CANDLE_UP if c >= o else CANDLE_DOWN
              for o, c in zip(win["open"], win["close"])]
    fig.add_trace(go.Bar(x=win.index, y=win["volume"], name="Volume",
                         marker_color=colors, marker_line_width=0,
                         opacity=0.65), row=2, col=1)
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
        if sub.empty: continue
        fig.add_trace(go.Scatter(
            x=sub["datetime"], y=[LEVEL_LABEL[tf]] * len(sub),
            mode="markers",
            marker=dict(size=11, color=level_colors[tf],
                        line=dict(color="#0B0F14", width=1)),
            name=LEVEL_LABEL[tf],
            hovertemplate=f"{LEVEL_LABEL[tf]}<br>%{{x|%d %b %H:%M}}<extra></extra>"))
    fig.update_layout(height=160, **PLOTLY_LAYOUT)
    fig.update_yaxes(categoryorder="array",
                     categoryarray=[LEVEL_LABEL[t] for t in reversed(LEVEL_ORDER)])
    return fig

def generate_narrative(row, ctx, mtf):
    ticker = row["ticker"]; level = LEVEL_LABEL[row["timeframe"]]
    sig_time = row["datetime"]
    aligned = [k for k, v in mtf.items() if v and v["signal"]]
    n_aligned = len(aligned)
    if n_aligned >= 3: conviction = "high conviction — broad multi-level alignment"
    elif n_aligned == 2: conviction = "moderate conviction — partial level agreement"
    elif n_aligned == 1: conviction = "single-level signal — confirmation pending"
    else: conviction = "historical signal — current state has cooled"
    aligned_labels = [LEVEL_LABEL[k] for k in aligned]
    parts = [
        f"**{ticker}** triggered on **{level}** at **{sig_time:%d %b %Y, %H:%M}** "
        f"with a signal quality score of **{ctx['quality']}/100** ({ctx['quality_label']}).",
        f"Price closed at **{float(ctx['bar']['close']):.2f}**, "
        f"**{abs(ctx['dev']):.2f}%** below its 20-bar baseline, "
        f"with a quant score of **{ctx['vol_score']:.0f}/100**. "
        f"Directional bias printed at **{ctx['bias']:.1f}**, confirming sustained selling pressure.",
        f"Level alignment: **{n_aligned} of 4** "
        f"({', '.join(aligned_labels) if aligned_labels else 'none currently active'}) — {conviction}.",
    ]
    if ctx["bars_since"] > 0:
        parts.append(f"Price has moved **{ctx['change_since']:+.2f}%** since the signal "
                     f"({ctx['bars_since']} bars ago).")
    return " ".join(parts)


# ============================================================
# SMALL-CAP MODULE — universe & config
# ============================================================
SC_TELEGRAM_BOT_TOKEN = '7064609087:AAEdusnfAy9-ZECdePF933EkUfNM-LBSjsQ'
SC_TELEGRAM_CHAT_ID   = '5762493363'
SC_EXCEL_FILE = 'list small.xlsx'
SC_SHEET_NAME = 'list small'

SYMBOLS_RAW_SC = (
    "KRSNAA.NS, MSPL.NS, BAJEL.NS, SHK.NS, CAPACITE.NS, PFS.NS, JAICORPLTD.NS, "
    "SPICELOUNG.NS, NILKAMAL.NS, MOLDTKPAC.NS, EIHAHOTELS.NS, SATIN.NS, KPGEL.NS, "
    "INDOCO.NS, GSPCROP.NS, KOTIC.NS, SPANDANA.NS, SAKSOFT.NS, STUDDS.NS, HATHWAY.NS, "
    "INSECTICID.NS, VIKRAN.NS, SOLARA.NS, GEOJITFSL.NS, SPAL.NS, GHVINFRA.NS, "
    "MUKANDLTD.NS, TASTYBITE.NS, ELPROINTL.NS, MOBAVENUE.NS, YATRA.NS, MTNL.NS, "
    "HINDWAREAP.NS, HGS.NS, VERANDA.NS, EMSLIMITED.NS, SILVERTUC.NS, PANAMAPET.NS, "
    "ORIENTHOT.NS, RANEHOLDIN.NS, STOVEKRAFT.NS, ADOR.NS, TCC.NS, INDNIPPON.NS, IPL.NS, "
    "COSMOFIRST.NS, TALBROAUTO.NS, NDRAUTO.NS, INDIANHUME.NS, GOODYEAR.NS, GOCOLORS.NS, "
    "MBEL.NS, SOMANYCERA.NS, ACCELYA.NS, SUMMITSEC.NS, CEINSYS.NS, APOLLOPIPE.NS, "
    "SOLARWORLD.NS, SHALBY.NS, RAMCOSYS.NS, DELTACORP.NS, DISAQ.NS, SIMPLEXINF.NS, "
    "SANSTAR.NS, INFOBEAN.NS, RISHABH.NS, FRONTSP.NS, HITECH.NS, STALLION.NS, "
    "WAAREEINDO.NS, KHAZANCHI.NS, JNKINDIA.NS, VINDHYATEL.NS, KPL.NS, GNA.NS, "
    "WINDLAS.NS, NIBE.NS, SPORTKING.NS, LANDMARK.NS, KALAMANDIR.NS, AAYUSHBULL.NS, "
    "ARMANFIN.NS, GRANDOAK.NS, AMRUTANJAN.NS, CITURGIA.NS, DOLPHIN.NS, BLSE.NS, "
    "RICOAUTO.NS, SDBL.NS, INDOKEM.NS, ASHIKA.NS, ALGOQUANT.NS, UGROCAP.NS, RAJESH.NS, "
    "ASIANTILES.NS, DOLLAR.NS, SHUKRAPHAR.NS, GARUDA.NS, YASHHV.NS, BLIL.NS, "
    "ASALCBR.NS, CONFIPET.NS, EXICOM.NS, WEL.NS, MOBIKWIK.NS, SBC.NS, GTLINFRA.NS, "
    "SESHAPAPER.NS, JINDRILL.NS, AMIC.NS, SURYODAY.NS, DLINKINDIA.NS, NELCO.NS, "
    "ALLTIME.NS, SUMEETINDS.NS, DYCL.NS, BFINVEST.NS, VIDHIING.NS, GOCLCORP.NS, "
    "GODAVARIB.NS, SMCGLOBAL.NS, ASTEC.NS, KMCSHIL.NS, SHANTIGOLD.NS, TITANBIO.NS, "
    "RMDRIP.NS, RACLGEAR.NS, MCLOUD.NS, JGCHEM.NS, VIDYAWIRES.NS, TIL.NS, ONEPOINT.NS, "
    "NAVKARCORP.NS, GANDHAR.NS, GYFTR.NS, DIGITIDE.NS, SULA.NS, JAGRAN.NS, MODINSU.NS, "
    "GPTINFRA.NS, SURAKSHA.NS, PASHUPATI.NS, MRUTR.NS, SPMLINFRA.NS, SANGHIIND.NS, "
    "DSSL.NS, SPIC.NS, META.NS, OMAXE.NS, ARFIN.NS, MAHASTEEL.NS, PNBGILTS.NS, "
    "FINOPB.NS, DCW.NS, WENDT.NS, NGLFINE.NS, MIIL.NS, ESAFSFB.NS, HESTERBIO.NS, "
    "RIR.NS, PRECAM.NS, BLUECLOUDS.NS, AIRLTD.NS, SHRIRAMPPS.NS, AWHCL.NS, AURUM.NS, "
    "DOLATALGO.NS, JYOTISTRUC.NS, WALCHANNAG.NS, CFF.NS, ASIANENE.NS, AMIRCHAND.NS, "
    "HARAFIN.NS, VENUSREM.NS, PARACABLES.NS, ORIENTTECH.NS, HUHTAMAKI.NS, DEN.NS, "
    "IVALUE.NS, MOTISONS.NS, CLSEL.NS, SEPC.NS, TINNARUBR.NS, MOL.NS, BHARATWIRE.NS, "
    "SIGNPOST.NS, SALASAR.NS, 5PAISA.NS, PUNJABCHEM.NS, EXPLEOSOL.NS, IMPAL.NS, "
    "ALLCARGO.NS, TTKHLTCARE.NS, ANDHRAPAP.NS, JAGSNPHARM.NS, UFBL.NS, BENARAS.NS, "
    "EKC.NS, UNITECH.NS, IFGLEXPOR.NS, ATULAUTO.NS, GNRL.NS, QUADFUTURE.NS, SYNCOMF.NS, "
    "HMAAGRO.NS, ALLDIGI.NS, KROSS.NS, MMWL.NS, TEXINFRA.NS, GREENPOWER.NS, PLATIND.NS, "
    "JINDALPHOT.NS, APEX.NS, GENESYS.NS, PNGSREVA.NS, IGPL.NS, MANAKCOAT.NS, "
    "CAPITALSFB.NS, ULTRAMAR.NS, RAJRILTD.NS, LINCOLN.NS, IGARASHI.NS, HITECHGEAR.NS, "
    "PAUSHAKLTD.NS, STEELXIND.NS, EXCELINDUS.NS, RGL.NS, BLKASHYAP.NS, RUPA.NS, "
    "VALIANT.NS, 3BBLACKBIO.NS, MONTECARLO.NS, AYMSYNTEX.NS, IKIO.NS, ZSARACOM.NS, "
    "INDSWFTLAB.NS, ONIDA.NS, HIMATSEIDE.NS, ALICON.NS, FAZE3Q.NS, CENTRUM.NS, "
    "STLNETWORK.NS, BALAJITELE.NS, JPOLYINVST.NS, IZMO.NS, LAXMIDENTL.NS, ARIHANTSUP.NS, "
    "VOEPL.NS, RIIL.NS, JAYBARMARU.NS, SHREEPUSHK.NS, BUTTERFLY.NS, HARIOMPIPE.NS, "
    "DAMCAPITAL.NS, ROTO.NS, ACGL.NS, BIRLANU.NS, MADRASFERT.NS, TARSONS.NS, DIFFNKG.NS, "
    "JYOTIRES.NS, CIFL.NS, PANORAMA.NS, SALZERELEC.NS, GPTHEALTH.NS, ANDREWYU.NS, "
    "BGDL.NS, BHARATSE.NS, RRPDEFENSE.NS, UNIECOM.NS, UDS.NS, RAJOOENG.NS, DHANBANK.NS, "
    "KALIND.NS, BOROSCI.NS, ANDHRSUGAR.NS, SHREDIGCEM.NS, NELCAST.NS, VHL.NS, SRM.NS, "
    "RSL.NS, BAJAJHCARE.NS, WCIL.NS, RATNAVEER.NS, TGVSL.NS, JARO.NS, MASTERTR.NS, "
    "GULPOLY.NS, SURAJEST.NS, GALAPREC.NS, AKCAPIT.NS, SYSTMTXC.NS, IRMENERGY.NS, "
    "NIITLTD.NS, INDORAMA.NS, TBZ.NS, SAPL.NS, RAMASTEEL.NS, ELECTHERM.NS, AFSL.NS, "
    "CREST.NS, CONTROLPR.NS, ABINFRA.NS, FINKURVE.NS, HARDWYN.NS, FREDUN.NS, MWL.NS, "
    "AEROENTER.NS, BIL.NS, AXISOL.NS, AVTNPL.NS, GANDHITUBE.NS, ASTAR.NS, BLUSPRING.NS, "
    "JAYTEX.NS, ORICONENT.NS, ZUARI.NS, YUKEN.NS, SKMEGGPROD.NS, BSHSL.NS, QUICKHEAL.NS, "
    "CNL.NS, ARIHANT.NS, CENTENKA.NS, TNPL.NS, INDPRUD.NS, BMW.NS, MAMATA.NS, OAL.NS, "
    "WEALTH.NS, MICEL.NS, MANALIPETC.NS, GRPLTD.NS, MAFATIND.NS, SEKURITIND.NS, "
    "FERMENTA.NS, MATRIMONY.NS, EXCELSOFT.NS, AMNPLST.NS, PRIMESECU.NS, ROHLTD.NS, "
    "NITTAGELA.NS, ASIANHOTNR.NS, ARIS.NS, VHLTD.NS, LOTUSCHO.NS, ROBU.NS, IFBAGRO.NS, "
    "TAALTECH.NS, BCLIND.NS, ORIRAIL.NS, EIMCOELECO.NS, GARGI.NS, HEALTHX.NS, "
    "ADVENTHTL.NS, APIS.NS, ESTER.NS, BORANA.NS, GKSL.NS, NDTV.NS, STANLEY.NS, "
    "DECCANCE.NS, A1L.NS, HEXATRADEX.NS, SICALLOG.NS, ECOSMOBLTY.NS, SWELECTES.NS, "
    "INDOBORAX.NS, GEMAROMA.NS, STEL.NS, COSMICCRF.NS, BAJAJINDEF.NS, RDBIPL.NS, "
    "UTTAMSUGAR.NS, BAJAJST.NS, KRISHIVAL.NS, PROSTARM.NS, NINSYS.NS, YSL.NS, "
    "WANBURY.NS, PERVASIVE.NS, BRIGHT.NS, ONEGLOBAL.NS, KELLTONTEC.NS, VASCONEQ.NS, "
    "BRRL.NS, KOKUYOCMLN.NS, DHARMAJ.NS, VADILENT.NS, MCCHRLS-B.NS, DVL.NS, "
    "DHAMPURSUG.NS, THEMISMED.NS, INDOAMIN.NS, SUNRAKSHAK.NS, SIGACHI.NS, ZELIO.NS, "
    "AVADHSUGAR.NS, OMINFRAL.NS, STERTOOLS.NS, GICHSGFIN.NS, ELDEHSG.NS, MAXIND.NS, "
    "SUDARCOLOR.NS, SCODATUBES.NS, NCLIND.NS, SRHHYPOLTD.NS, GCSL.NS, SGIL.NS, "
    "MUNJALAU.NS, KRYSTAL.NS, FEDDERSHOL.NS, TNPETRO.NS, AMBIKCO.NS, RNBDENIMS.NS, "
    "CROPSTER.NS, HERANBA.NS, KABRAEXTRU.NS, BPLPHARMA.NS, ISTLTD.NS, NWIL.NS, "
    "SUYOG.NS, MAANALU.NS, NAHARSPING.NS, MEIL.NS"
)
SC_SYMBOLS = list(dict.fromkeys(
    [s.strip() for s in SYMBOLS_RAW_SC.split(',') if s.strip()]))

# ============================================================
# SMALL-CAP helpers (unchanged)
# ============================================================
def sc_send_telegram(msg, quiet=True):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{SC_TELEGRAM_BOT_TOKEN}/sendMessage",
            data={'chat_id': SC_TELEGRAM_CHAT_ID, 'text': msg,
                  'parse_mode': 'HTML'}, timeout=10)
        if r.status_code != 200 and not quiet:
            st.warning(f"Telegram failed: {r.status_code}")
    except Exception:
        if not quiet:
            st.warning("Telegram request error")

def sc_load_mcap_excel(filelike):
    try:
        try:
            df = pd.read_excel(filelike, sheet_name=SC_SHEET_NAME)
        except Exception:
            df = pd.read_excel(filelike)
        df = df.rename(columns={df.columns[0]: 'stock name',
                                df.columns[1]: 'market cap'})
        df['stock name'] = df['stock name'].astype(str).str.strip().str.upper()
        df['market cap'] = pd.to_numeric(df['market cap'], errors='coerce')
        df = df.dropna(subset=['market cap'])
        df = df[~df['stock name'].isin(['-', 'NAN', 'NONE', ''])]
        df = df.drop_duplicates('stock name')
        return dict(zip(df['stock name'], df['market cap']))
    except Exception:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def sc_get_mcap_yf(symbol):
    try:
        t = yf.Ticker(symbol)
        try:
            fi = t.fast_info
            mc = fi.get('market_cap') if hasattr(fi, 'get') else getattr(fi, 'market_cap', None)
            if mc and mc > 0:
                return float(mc) / 1e7
        except Exception:
            pass
        try:
            info = t.info
            mc = info.get('marketCap') if info else None
            if mc and mc > 0:
                return float(mc) / 1e7
        except Exception:
            pass
    except Exception:
        pass
    return None

@st.cache_data(ttl=1800, show_spinner=False)
def sc_get_price_data(symbol):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            df = yf.download(symbol, period='1y', interval='1d',
                             auto_adjust=True, progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[['High', 'Low', 'Close', 'Volume']].dropna()
        return df if len(df) >= 100 else None
    except Exception:
        return None

def sc_get_vah(df, va_pct, bins=100):
    price = (df['High'] + df['Low']) / 2.0
    vol   = df['Volume']
    mask  = price.notna() & vol.notna() & (vol > 0)
    price, vol = price[mask], vol[mask]
    if price.empty:
        return None
    hist, edges = np.histogram(price, bins=bins, weights=vol)
    if hist.sum() <= 0:
        return None
    levels = (edges[:-1] + edges[1:]) / 2.0
    vdf = pd.DataFrame({'Price': levels, 'Volume': hist}) \
             .sort_values('Volume', ascending=False)
    vdf['Cum'] = vdf['Volume'].cumsum()
    total = vdf['Volume'].sum()
    va = vdf[vdf['Cum'] <= total * va_pct]
    return None if va.empty else float(va['Price'].max())

def sc_compute_signal(df, symbol, mcap, cfg):
    if df is None or len(df) < 100:
        return None
    vah = sc_get_vah(df, cfg['va_pct'])
    if vah is None or not np.isfinite(vah):
        return None
    prev_close = float(df['Close'].iloc[-2])
    close      = float(df['Close'].iloc[-1])
    if cfg['require_fresh']:
        if not (prev_close <= vah < close):
            return None
    else:
        if not (close > vah):
            return None
    try:
        atr_series = ta.volatility.AverageTrueRange(
            high=df['High'], low=df['Low'], close=df['Close'],
            window=cfg['atr_window']).average_true_range()
        atr = float(atr_series.iloc[-1])
    except Exception:
        return None
    if not np.isfinite(atr) or close <= 0:
        return None
    atr_pct = atr / close * 100.0
    if atr_pct <= cfg['min_atr_pct']:
        return None
    hv_current = hv_cutoff = None
    hv_calm = False
    try:
        log_ret = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        if len(log_ret) >= cfg['hv_window'] + 20:
            hv_series = (log_ret.rolling(cfg['hv_window']).std()
                         * np.sqrt(252) * 100).dropna()
            if len(hv_series) >= 100:
                hv_current = float(hv_series.iloc[-1])
                recent = hv_series.iloc[-min(cfg['hv_lookback'], len(hv_series)):]
                hv_cutoff = float(np.percentile(recent, cfg['hv_pct']))
                hv_calm = hv_current <= hv_cutoff
    except Exception:
        pass
    return {
        'Stock'            : symbol.replace('.NS', ''),
        'Market Cap (Cr)'  : round(mcap, 1),
        'CMP'              : round(close, 2),
        f'VAH({int(cfg["va_pct"]*100)}%)': round(vah, 2),
        f'ATR({cfg["atr_window"]})': round(atr, 2),
        'ATR %'            : round(atr_pct, 2),
        f'HV({cfg["hv_window"]}) %': round(hv_current, 1) if hv_current is not None else None,
        'HV Calm Cutoff %' : round(hv_cutoff, 1) if hv_cutoff is not None else None,
        'HV Calm'          : '✅' if hv_calm else '❌',
        '_hv_calm'         : hv_calm,
    }


# ============================================================
# LANDING PAGE
# ============================================================
if not st.session_state.get("entered"):
    st.markdown(f"""
    <div class="land-wrap">
        <div class="land-eyebrow">{BRAND_TAG}</div>
        <h1 class="land-title">{BRAND_NAME}</h1>
        <p class="land-tagline">Institutional-Grade Signal Discovery</p>
        <p class="land-sub">
            A multi-level confluence engine combined with a coiled-spring
            small-cap screener — two independent discovery systems in one
            institutional workspace.
        </p>
        <div class="land-stats">
            <div class="land-stat"><div class="num">04</div><div class="lbl">Levels</div></div>
            <div class="land-stat"><div class="num">02</div><div class="lbl">Modules</div></div>
            <div class="land-stat"><div class="num">680+</div><div class="lbl">Instruments</div></div>
        </div>
        <div class="land-features">
            <div class="land-feature">
                <h4>Multi-Level Confluence</h4>
                <p>Independent detection across four intraday horizons ensures
                   only durable signals reach the surface.</p>
            </div>
            <div class="land-feature">
                <h4>Coiled-Spring Screener</h4>
                <p>VAH-70% breakout + ATR% + calm-volatility filter surfaces
                   micro-caps quietly preparing to move.</p>
            </div>
            <div class="land-feature">
                <h4>Deep Analytics</h4>
                <p>Candlestick overlays, quality scoring, level alignment
                   matrix, and market-cap context per qualified hit.</p>
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


# ============================================================
# HERO
# ============================================================
live, status_label = market_status()
pill_cls = "status-live" if live else "status-closed"
dot_cls  = "dot-live" if live else "dot-closed"

st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">{BRAND_TAG}</div>
    <div class="hero-title">{BRAND_NAME}</div>
    <p class="hero-sub">Two independent discovery modules · Shared institutional workspace</p>
    <div class="status-pill {pill_cls}">
        <span class="dot {dot_cls}"></span> {status_label}
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# MODULE 1 — FINTRIX SIGNAL ENGINE (unchanged logic)
# ============================================================
def render_signal_engine():
    st.markdown('<div class="control-card">', unsafe_allow_html=True)
    st.markdown('<div class="control-title">Scan Configuration</div>',
                unsafe_allow_html=True)

    rc1, rc2 = st.columns([2, 1])
    with rc1:
        universe = st.radio(
            "Instrument Universe",
            ["Standard (~190)", "High Volatility (~60)", "Full (~250)"],
            index=2, horizontal=True, key="fx_universe_radio")
        if universe.startswith("Standard"):
            base = [t.replace(".NS", "") for t in STANDARD_SYMBOLS]
        elif universe.startswith("High"):
            base = [t.replace(".NS", "") for t in HIGH_VOL_SYMBOLS]
        else:
            base = ALL_SYMBOLS
    with rc2:
        max_tickers = st.slider(
            "Max Instruments", min_value=10, max_value=len(base),
            value=len(base), step=10, key="fx_max_tickers")

    tickers = base[:max_tickers]

    rc3, rc4 = st.columns([3, 2])
    with rc3:
        st.markdown('<div class="section-label">Analysis Levels</div>',
                    unsafe_allow_html=True)
        lvl_cols = st.columns(4)
        lvl_1 = lvl_cols[0].checkbox("Level 1", value=True, key="fx_lvl1")
        lvl_2 = lvl_cols[1].checkbox("Level 2", value=True, key="fx_lvl2")
        lvl_3 = lvl_cols[2].checkbox("Level 3", value=True, key="fx_lvl3")
        lvl_4 = lvl_cols[3].checkbox("Level 4", value=True, key="fx_lvl4")
        selected_tfs = [tf for tf, on in
                        [("15m", lvl_1), ("30m", lvl_2),
                         ("45m", lvl_3), ("60m", lvl_4)] if on]
    with rc4:
        days_back = st.slider("Look-back Window (days)", 5, 30, 10, 1,
                              key="fx_days_back")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns([2, 1, 1, 1])
    with b1:
        run_btn = st.button("RUN SCAN", use_container_width=True, type="primary",
                            key="fx_run_btn")
    with b2:
        refresh_btn = st.button("Refresh", use_container_width=True,
                                key="fx_refresh_btn")
    with b3:
        clear_btn = st.button("Clear", use_container_width=True,
                              key="fx_clear_btn")
    with b4:
        if st.session_state.get("scan_out"):
            df_now = st.session_state.scan_out["results_df"]
            if not df_now.empty:
                st.download_button(
                    "Export", data=to_csv_bytes(df_now),
                    file_name=f"signals_{datetime.now():%Y%m%d_%H%M}.csv",
                    mime="text/csv", use_container_width=True,
                    key="fx_export_btn")

    st.markdown('</div>', unsafe_allow_html=True)

    if clear_btn:
        st.session_state.scan_out = None
        st.rerun()

    if refresh_btn:
        st.cache_data.clear()
        st.session_state.scan_out = None
        st.success("Cache cleared. Next scan will pull fresh data.")

    if "scan_out" not in st.session_state:
        st.session_state.scan_out = None

    if run_btn:
        if not selected_tfs:
            st.error("Select at least one level.")
            return
        if not tickers:
            st.error("No instruments selected.")
            return

        fetch_slot = st.empty()
        fetch_slot.info(f"Fetching data for {len(tickers)} instruments…")
        batch_data, fetch_err = cached_batch(tuple(tickers))
        if fetch_err:
            fetch_slot.empty(); st.error(f"Fetch failed: {fetch_err}"); return
        if not batch_data:
            fetch_slot.empty(); st.error("No data returned. Try Refresh and scan again."); return

        fetch_slot.success(f"{len(batch_data)}/{len(tickers)} instruments loaded. Processing…")
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
                            progress_cb=_prog, ticker_cb=_tick)
        progress.empty(); status_slot.empty(); fetch_slot.empty()

        st.session_state.scan_out = out
        st.session_state.scan_meta = {
            "tickers_scanned": len(batch_data),
            "timeframes": selected_tfs,
            "days_back": days_back,
        }
        st.success(f"Scan complete — {len(out['results_df'])} signal(s) "
                   f"across {len(batch_data)} instruments in {out['scan_time_s']}s.")

    out = st.session_state.scan_out
    if out is None:
        st.info("Configure the scan above, then click RUN SCAN.")
        return

    df   = out["results_df"]
    diag = out["diag"]
    meta = st.session_state.get("scan_meta", {})
    levels_str = " · ".join([LEVEL_LABEL[t] for t in meta.get("timeframes", [])])

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Instruments Scanned",
              meta.get("tickers_scanned", out.get("tickers_processed", 0)))
    k2.metric("Signals Detected", len(df),
              delta=f"{df['ticker'].nunique()} unique" if len(df) else "none")
    k3.metric("Scan Duration", f"{out['scan_time_s']}s")
    k4.metric("Active Levels", levels_str)

    tab_sig, tab_chart, tab_diag, tab_err = st.tabs(
        ["SIGNALS", "CHART", "ANALYTICS", "NOTES"])

    with tab_sig:
        if df.empty:
            st.info(f"No signals detected in the last {meta.get('days_back', 10)} days.")
        else:
            f1, f2, f3 = st.columns(3)
            with f1:
                tf_f = st.multiselect(
                    "Level",
                    options=sorted(df["timeframe"].unique().tolist()),
                    default=sorted(df["timeframe"].unique().tolist()),
                    format_func=lambda x: LEVEL_LABEL.get(x, x),
                    key="fx_tf_filter")
            with f2:
                tk_f = st.multiselect(
                    "Instrument",
                    sorted(df["ticker"].unique().tolist()),
                    default=[], placeholder="All instruments",
                    key="fx_tk_filter")
            with f3:
                min_bias = st.slider(
                    "Max Bias Threshold",
                    float(df["raw_di_diff"].min()), 0.0, 0.0,
                    key="fx_bias_filter")

            filt = df[df["timeframe"].isin(tf_f) & (df["raw_di_diff"] <= min_bias)]
            if tk_f:
                filt = filt[filt["ticker"].isin(tk_f)]
            filt = filt.sort_values(["datetime", "ticker"], ascending=[False, True])

            disp = filt.copy().reset_index(drop=True)
            disp.insert(0, "Rank", range(1, len(disp) + 1))
            disp["Timestamp"] = disp["datetime"].dt.strftime("%d %b %Y · %H:%M")
            disp["Instrument"] = disp["ticker"]
            disp["Level"] = disp["timeframe"].map(LEVEL_LABEL)
            disp["Last Price"] = disp["close"].round(2)
            disp["Deviation"] = disp["distance_pct"].round(2)
            disp["Bias"] = disp["raw_di_diff"].round(2)
            disp = disp[["Rank", "Timestamp", "Instrument", "Level",
                         "Last Price", "Deviation", "Bias"]]
            top3 = set(range(min(3, len(disp))))

            def _style_row(row):
                if row.name in top3:
                    return ['background-color: rgba(34,197,94,0.10); '
                            'color: #22C55E; font-weight: 600'] * len(row)
                return [''] * len(row)

            st.dataframe(
                disp.style.apply(_style_row, axis=1),
                use_container_width=True, hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("#", width="small"),
                    "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                    "Instrument": st.column_config.TextColumn("Instrument", width="small"),
                    "Level": st.column_config.TextColumn("Level", width="small"),
                    "Last Price": st.column_config.NumberColumn("Last", format="%.2f", width="small"),
                    "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%", width="small"),
                    "Bias": st.column_config.NumberColumn("Bias", format="%.2f", width="small"),
                })
            st.caption("Highlighted rows mark the three most recent signals.")

    with tab_chart:
        if df.empty:
            st.info("No signals available — run a scan with at least one qualified hit.")
        else:
            labels = df.apply(
                lambda r: f"{r['ticker']} · {LEVEL_LABEL[r['timeframe']]} · "
                          f"{r['datetime']:%d %b %Y %H:%M}", axis=1).tolist()
            pick = st.selectbox("Select a signal", labels, key="fx_chart_pick")
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

                scanned = detect_signals(rs)
                ctx = compute_signal_context(scanned, row)
                mtf = get_current_mtf_state(raw)

                q1, q2, q3, q4, q5 = st.columns(5)
                q1.metric("Signal Quality", f"{ctx['quality']}/100", ctx["quality_label"])
                q2.metric("Quant Score", f"{ctx['vol_score']:.0f}/100",
                          "high" if ctx['vol_score'] >= 50 else "moderate")
                q3.metric("Deviation", f"{ctx['dev']:.2f}%")
                q4.metric("Bias", f"{ctx['bias']:.2f}")
                q5.metric("Bars Since", ctx["bars_since"], f"{ctx['change_since']:+.2f}%")

                st.markdown("#### Price Action · Signal Overlay")
                fig = build_pro_chart(scanned, row, ctx, window_days=7)
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
                        mtf_rows.append({
                            "Level": LEVEL_LABEL[tf_name], "Status": state["status"],
                            "Bias": round(state["bias"], 2),
                            "Deviation": round(state["dev"], 2),
                            "Quant Score": round(state["vol_score"], 0)})
                mtf_df = pd.DataFrame(mtf_rows)

                def _style_status(val):
                    v = str(val)
                    if v == "Active":
                        return "background-color: rgba(34,197,94,0.12); color: #22C55E; font-weight: 600;"
                    if v == "Exhaustion":
                        return "background-color: rgba(245,158,11,0.12); color: #F59E0B; font-weight: 600;"
                    if v == "Bias Only":
                        return "background-color: rgba(0,209,178,0.10); color: #00D1B2; font-weight: 600;"
                    if v == "Quiet":
                        return "color: #9CA3AF;"
                    return ""

                st.dataframe(
                    mtf_df.style.map(_style_status, subset=["Status"]),
                    use_container_width=True, hide_index=True,
                    column_config={
                        "Level": st.column_config.TextColumn("Level", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="medium"),
                        "Bias": st.column_config.NumberColumn("Bias", format="%.2f"),
                        "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%"),
                        "Quant Score": st.column_config.NumberColumn("Quant Score", format="%.0f"),
                    })

                st.markdown("#### Automated Analysis")
                st.info(generate_narrative(row, ctx, mtf))

                ticker_hist = df[df["ticker"] == row["ticker"]].copy()
                if len(ticker_hist) >= 1:
                    st.markdown("#### Signal History · This Instrument")
                    st.plotly_chart(build_signal_timeline(ticker_hist),
                                    use_container_width=True,
                                    config={"displayModeBar": False})

                st.markdown("#### Swing Context")
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Recent High", f"{ctx['recent_high']:.2f}",
                          f"{ctx['dist_from_high']:.2f}%")
                s2.metric("Recent Low", f"{ctx['recent_low']:.2f}",
                          f"{ctx['dist_from_low']:+.2f}%")
                s3.metric("Bars Since Signal", ctx["bars_since"])
                s4.metric("Change Since", f"{ctx['change_since']:+.2f}%")

                related = df[(df["ticker"] == row["ticker"])].copy()
                if len(related) > 1:
                    if idx in df.index:
                        related = related.drop(idx)
                    if not related.empty:
                        st.markdown("#### Related Signals · Same Instrument")
                        rel = related.reset_index(drop=True)
                        rel.insert(0, "Rank", range(1, len(rel) + 1))
                        rel["Timestamp"] = rel["datetime"].dt.strftime("%d %b %Y · %H:%M")
                        rel["Level"] = rel["timeframe"].map(LEVEL_LABEL)
                        rel["Last Price"] = rel["close"].round(2)
                        rel["Deviation"] = rel["distance_pct"].round(2)
                        rel["Bias"] = rel["raw_di_diff"].round(2)
                        st.dataframe(
                            rel[["Rank", "Timestamp", "Level", "Last Price",
                                 "Deviation", "Bias"]],
                            use_container_width=True, hide_index=True,
                            column_config={
                                "Rank": st.column_config.NumberColumn("#", width="small"),
                                "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                                "Level": st.column_config.TextColumn("Level", width="small"),
                                "Last Price": st.column_config.NumberColumn("Last", format="%.2f"),
                                "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%"),
                                "Bias": st.column_config.NumberColumn("Bias", format="%.2f"),
                            })

    with tab_diag:
        st.markdown("### Detection Funnel")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Filter 1 Match", diag["stage_a"])
        d2.metric("Filter 2 Match", diag["stage_b"])
        d3.metric("Qualified", diag["final"])
        d4.metric("No Data", diag["empty_data"])
        st.caption(
            f"Window cutoff: {out['cutoff']} · Duration: {out['scan_time_s']}s · "
            f"Instruments processed: {out.get('tickers_processed', 0)}")

    with tab_err:
        if not out["errors"]:
            st.success("No exceptions — all instruments processed cleanly.")
        else:
            st.warning(f"{len(out['errors'])} instrument(s) returned a processing note.")
            st.dataframe(pd.DataFrame(out["errors"], columns=["Instrument", "Note"]),
                         use_container_width=True, hide_index=True)


# ============================================================
# MODULE 2 — SMALL-CAP COILED SPRING SCREENER
# ============================================================
def render_smallcap_screener():
    st.markdown('<div class="control-card">', unsafe_allow_html=True)
    st.markdown('<div class="control-title">Screener Configuration</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        min_mcap = st.number_input("Min Market Cap (₹ Cr)", 100, 10000, 900, 100,
                                   key="sc_min_mcap")
        max_mcap = st.number_input("Max Market Cap (₹ Cr)", 100, 50000, 2500, 100,
                                   key="sc_max_mcap")
    with c2:
        va_pct = st.slider("Value Area %", 50, 90, 70, key="sc_va_pct") / 100.0
        atr_window = st.number_input("ATR Window", 5, 50, 14, key="sc_atr_window")
    with c3:
        min_atr_pct = st.number_input("Min ATR % (ATR/CMP × 100)", 0.0, 20.0,
                                      4.0, 0.5, key="sc_min_atr_pct")
        require_fresh = st.checkbox("Require fresh VAH cross", True,
                                    key="sc_require_fresh")

    st.markdown('<div class="section-label">HV (Calm) Filter</div>',
                unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    with h1:
        hv_window = st.number_input("HV Window (days)", 5, 60, 20,
                                    key="sc_hv_window")
    with h2:
        hv_lookback = st.number_input("HV Lookback (days)", 60, 500, 252,
                                      key="sc_hv_lookback")
    with h3:
        hv_pct = st.slider("HV Calm Percentile", 10, 90, 60,
                           help="HV must be below this percentile of its own history",
                           key="sc_hv_pct")

    st.markdown('<div class="section-label">Market Cap Source</div>',
                unsafe_allow_html=True)
    src1, src2 = st.columns(2)
    with src1:
        uploaded = st.file_uploader(f"Upload {SC_EXCEL_FILE}", type=['xlsx'],
                                    key="sc_excel_upload")
    with src2:
        use_yf_mcap = st.checkbox("Fallback to yfinance market cap (slow)", value=False,
                                  key="sc_yf_mcap")
        send_tg = st.checkbox("Send Telegram alerts", value=False,
                              key="sc_send_tg")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    sb1, sb2, sb3, sb4 = st.columns([2, 1, 1, 1])
    with sb1:
        sc_run_all = st.button("RUN BOTH SCANS", use_container_width=True,
                               type="primary", key="sc_run_all_btn")
    with sb2:
        sc_run_no_hv = st.button("Run Without HV", use_container_width=True,
                                 key="sc_run_no_hv_btn")
    with sb3:
        sc_clear = st.button("Clear", use_container_width=True,
                             key="sc_clear_btn")
    with sb4:
        if st.session_state.get("sc_last_run"):
            st.caption(f"Last run: {st.session_state['sc_last_run']}")

    st.markdown('</div>', unsafe_allow_html=True)

    if sc_clear:
        for k in ('sc_results_with_hv', 'sc_results_without_hv',
                  'sc_last_cfg', 'sc_last_run'):
            st.session_state.pop(k, None)
        st.rerun()

    mcap_map = {}
    if uploaded:
        mcap_map = sc_load_mcap_excel(uploaded)
        if mcap_map:
            st.success(f"✅ Loaded {len(mcap_map)} market caps from {uploaded.name}")
        else:
            st.warning("⚠ Could not parse uploaded Excel.")
    else:
        st.info(f"Upload {SC_EXCEL_FILE} for fast market-cap lookup "
                f"(otherwise enable yfinance fallback).")

    cfg = {
        'va_pct': va_pct, 'atr_window': atr_window,
        'min_atr_pct': min_atr_pct, 'require_fresh': require_fresh,
        'hv_window': hv_window, 'hv_lookback': hv_lookback, 'hv_pct': hv_pct,
    }

    # Build scan list
    scan_list = []
    with st.spinner("Building scan list …"):
        for sym in SC_SYMBOLS:
            name = sym.replace('.NS', '').upper()
            mcap = mcap_map.get(name)
            if mcap is None and use_yf_mcap:
                mcap = sc_get_mcap_yf(sym)
            if mcap is not None and min_mcap <= mcap <= max_mcap:
                scan_list.append((sym, mcap))

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Universe", len(SC_SYMBOLS))
    col_b.metric("In MCap range", len(scan_list))
    col_c.metric("MCap range", f"₹{min_mcap:,}–₹{max_mcap:,} Cr")

    if (sc_run_all or sc_run_no_hv):
        if not scan_list:
            st.error("No stocks in the market-cap range. Upload Excel or enable yfinance fallback.")
            return

        results_with_hv, results_without_hv = [], []
        progress = st.progress(0.0, text="Scanning …")
        status   = st.empty()
        t0 = time.time()

        for i, (sym, mcap) in enumerate(scan_list, 1):
            status.markdown(f"🔎 **{sym}** · {i}/{len(scan_list)}")
            df = sc_get_price_data(sym)
            r = sc_compute_signal(df, sym, mcap, cfg) if df is not None else None
            if r is not None:
                results_without_hv.append(r)
                if r['_hv_calm']:
                    results_with_hv.append(r)
            progress.progress(i / len(scan_list),
                              text=f"Scanned {i}/{len(scan_list)}")

        elapsed = time.time() - t0
        progress.empty(); status.empty()

        st.session_state['sc_results_with_hv']    = results_with_hv
        st.session_state['sc_results_without_hv'] = results_without_hv
        st.session_state['sc_last_cfg']           = cfg.copy()
        st.session_state['sc_last_run']           = datetime.now().strftime("%H:%M:%S")

        st.success(f"✅ Scanned {len(scan_list)} stocks in {elapsed:.0f}s — "
                   f"{len(results_with_hv)} coiled / {len(results_without_hv)} base")

        if send_tg and results_with_hv:
            for r in results_with_hv:
                msg = (
                    f"🚨 <b>{r['Stock']}</b> — Coiled VAH Breakout\n"
                    f"🏦 Market Cap: ₹{r['Market Cap (Cr)']:.1f} Cr\n"
                    f"💰 CMP: ₹{r['CMP']:.2f}\n"
                    f"📈 VAH: ₹{r[f'VAH({int(va_pct*100)}%)']:.2f}\n"
                    f"📊 ATR%: {r['ATR %']:.2f}%  |  HV: {r[f'HV({hv_window}) %']}%"
                )
                sc_send_telegram(msg, quiet=True)
            st.toast(f"📨 Sent {len(results_with_hv)} Telegram alerts", icon="📨")

    # Render stored results
    if 'sc_results_with_hv' not in st.session_state:
        st.info("Configure the settings above, then click RUN BOTH SCANS.")
        return

    hv     = st.session_state['sc_results_with_hv']
    no_hv  = st.session_state['sc_results_without_hv']
    cfg_s  = st.session_state.get('sc_last_cfg', cfg)

    if cfg != cfg_s:
        st.warning("⚠️ Settings changed since last scan — re-run to apply.")

    def render_table(rows, key, show_hv_col):
        if not rows:
            st.info("No matches for this scan.")
            return
        df_show = pd.DataFrame(rows)
        df_show = df_show.drop(columns=['_hv_calm'], errors='ignore')
        df_show = df_show.sort_values('Market Cap (Cr)',
                                      ascending=False).reset_index(drop=True)
        cols = list(df_show.columns)
        if not show_hv_col and 'HV Calm' in cols:
            cols.remove('HV Calm')
            df_show = df_show[cols]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        csv = df_show.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download CSV", data=csv,
            file_name=f"screener_{key}.csv", mime="text/csv",
            key=f"sc_dl_{key}")

    sub_with_hv, sub_without_hv = st.tabs([
        f"🔬 WITH HV · Coiled — {len(hv)}",
        f"📊 WITHOUT HV · Base — {len(no_hv)}",
    ])

    with sub_with_hv:
        st.caption(
            f"VAH({int(cfg_s['va_pct']*100)}%) breakout · "
            f"ATR% > {cfg_s['min_atr_pct']} · "
            f"HV({cfg_s['hv_window']}) ≤ {cfg_s['hv_pct']}th percentile (calm)")
        render_table(hv, "with_hv", show_hv_col=False)

    with sub_without_hv:
        st.caption(
            f"VAH({int(cfg_s['va_pct']*100)}%) breakout · "
            f"ATR% > {cfg_s['min_atr_pct']} · (no HV filter)")
        render_table(no_hv, "without_hv", show_hv_col=True)


# ============================================================
# TOP-LEVEL TABS
# ============================================================
main_tab1, main_tab2 = st.tabs([
    "◆ SIGNAL ENGINE",
    "◆ SMALL-CAP COILED SCREENER",
])

with main_tab1:
    render_signal_engine()

with main_tab2:
    render_smallcap_screener()


# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div class="fintrix-footer">
    <div class="brand">{BRAND_NAME}</div>
    <div class="tag">{BRAND_TAG}</div>
</div>
""", unsafe_allow_html=True)
