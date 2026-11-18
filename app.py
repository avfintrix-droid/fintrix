import numpy as np
import pandas as pd
import yfinance as yf
import warnings
import time
import streamlit as st
from datetime import datetime, timedelta
import pytz

import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# BRANDING + LEVEL MAPPING
# ─────────────────────────────────────────────────────────
BRAND_NAME = "Fintrix Analytics"

# Internal timeframe keys → client-facing level labels
LEVEL_LABEL = {
    "15m": "Level 1",
    "30m": "Level 2",
    "45m": "Level 3",
    "60m": "Level 4",
}
LEVEL_ORDER = ["15m", "30m", "45m", "60m"]

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{BRAND_NAME} · Signal Detection Suite",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
# GLOBAL CSS  (desktop + mobile media queries)
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 0%, #0f1a2e 0%, #0a0e1a 40%, #060910 100%); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px; }

.land-wrap { max-width: 900px; margin: 80px auto; text-align: center; }
.land-eyebrow { font-size: 0.72rem; letter-spacing: 0.32em; color: #00d4ff;
    font-weight: 800; text-transform: uppercase; margin-bottom: 16px; }
.land-title { font-size: 3.4rem; font-weight: 900;
    background: linear-gradient(90deg, #ffffff, #a8e6ff, #00d4ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 20px 0; letter-spacing: -0.035em; line-height: 1.05; }
.land-sub { color: #8892a6; font-size: 1.12rem; line-height: 1.75;
    margin-bottom: 6px; max-width: 640px; margin-left: auto; margin-right: auto; }
.land-stats { display: flex; gap: 20px; justify-content: center; margin: 48px 0; flex-wrap: wrap; }
.land-stat { background: linear-gradient(135deg, #131824, #182135);
    border: 1px solid #1e2a3f; border-radius: 14px; padding: 24px 36px; min-width: 160px; }
.land-stat .num { color: #00d4ff; font-size: 2rem; font-weight: 800;
    font-family: 'JetBrains Mono', monospace; }
.land-stat .lbl { color: #8892a6; font-size: 0.78rem; margin-top: 6px;
    letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }
.land-features { display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 16px; margin-top: 48px; text-align: left; }
.land-feature { background: rgba(19, 24, 36, 0.65); border: 1px solid #1e2a3f;
    border-radius: 14px; padding: 22px; }
.land-feature h4 { color: #e0e6ed; font-size: 0.94rem; margin: 0 0 8px 0; font-weight: 700; }
.land-feature p { color: #6b7a90; font-size: 0.85rem; margin: 0; line-height: 1.6; }

.hero-wrap { background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,230,118,0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.18); border-radius: 16px;
    padding: 26px 32px; margin-bottom: 20px;
    box-shadow: 0 8px 40px rgba(0, 212, 255, 0.06); }
.hero-eyebrow { font-size: 0.72rem; letter-spacing: 0.32em; color: #00d4ff;
    font-weight: 800; text-transform: uppercase; margin-bottom: 6px; }
.hero-title { font-size: 2.1rem; font-weight: 800;
    background: linear-gradient(90deg, #ffffff 0%, #a8e6ff 60%, #00d4ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0; letter-spacing: -0.02em; }
.hero-sub { color: #6b7a90; font-size: 0.94rem; margin: 0; }
.status-pill { display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 14px; border-radius: 999px; font-size: 0.74rem;
    font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    margin-top: 16px; }
.status-live { background: rgba(0,230,118,0.12); color: #00e676;
    border: 1px solid rgba(0,230,118,0.35); }
.status-closed { background: rgba(255,171,0,0.10); color: #ffab00;
    border: 1px solid rgba(255,171,0,0.35); }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-live { background: #00e676; box-shadow: 0 0 8px #00e676; animation: pulse 1.8s infinite; }
.dot-closed { background: #ffab00; }
@keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.35 } }

.control-card { background: linear-gradient(135deg, #131824 0%, #182135 100%);
    border: 1px solid #1e2a3f; border-radius: 16px;
    padding: 26px 30px; margin-bottom: 20px;
    box-shadow: 0 6px 32px rgba(0,0,0,0.35); }
.control-title { color: #00d4ff; font-size: 0.76rem; letter-spacing: 0.18em;
    font-weight: 800; text-transform: uppercase; margin-bottom: 18px; }

[data-testid="stMetric"] { background: linear-gradient(135deg, #131824, #182135);
    border: 1px solid #1e2a3f; border-radius: 14px;
    padding: 18px 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.35); }
[data-testid="stMetricLabel"] { color: #6b7a90 !important; font-size: 0.74rem !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    font-weight: 700 !important; }
[data-testid="stMetricValue"] { color: #e0e6ed !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important; font-size: 1.9rem !important; }

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #00d4ff 0%, #00a3cc 100%);
    color: #0a0e1a !important; border: none; font-weight: 800;
    letter-spacing: 0.1em; padding: 0.9rem 2rem; border-radius: 12px;
    font-size: 0.98rem; box-shadow: 0 6px 24px rgba(0, 212, 255, 0.35);
    transition: all 0.2s ease; text-transform: uppercase; }
.stButton > button[kind="primary"]:hover { transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.55); }

.stDownloadButton > button {
    background: linear-gradient(90deg, #00e676 0%, #00b862 100%);
    color: #0a0e1a !important; font-weight: 700;
    border-radius: 10px; border: none; padding: 0.6rem 1.4rem; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #1e2a3f; }
.stTabs [data-baseweb="tab"] { color: #6b7a90; font-weight: 600;
    font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;
    padding: 10px 20px; }
.stTabs [aria-selected="true"] { color: #00d4ff !important;
    border-bottom-color: #00d4ff !important; }
h2, h3, h4 { color: #e0e6ed !important; }

.fintrix-footer { text-align:center; margin-top:48px; padding-top:24px;
    border-top:1px solid #1e2a3f; }
.fintrix-footer .brand { color:#3a4355; font-size:0.68rem; letter-spacing:0.24em;
    font-weight:800; text-transform:uppercase; }
.fintrix-footer .tag { color:#2a3244; font-size:0.6rem; letter-spacing:0.12em;
    margin-top:6px; }

/* ─── MOBILE ─── */
@media (max-width: 768px) {
    .block-container { padding-left: 0.75rem; padding-right: 0.75rem; padding-top: 1rem; }
    .hero-wrap { padding: 18px 20px !important; border-radius: 12px !important; }
    .hero-title { font-size: 1.4rem !important; }
    .hero-eyebrow { font-size: 0.6rem !important; letter-spacing: 0.24em !important; }
    .hero-sub { font-size: 0.82rem !important; }
    .control-card { padding: 16px 18px !important; border-radius: 12px !important; }
    .control-title { font-size: 0.68rem !important; letter-spacing: 0.14em !important;
        margin-bottom: 12px !important; }
    [data-testid="stMetricValue"] { font-size: 1.35rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.6rem !important; letter-spacing: 0.05em !important; }
    [data-testid="stMetric"] { padding: 14px 16px !important; border-radius: 10px !important; }
    .stButton > button { padding: 0.75rem 1rem !important; font-size: 0.85rem !important;
        min-height: 44px !important; }
    .stButton > button[kind="primary"] { padding: 0.9rem 1.2rem !important;
        font-size: 0.88rem !important; letter-spacing: 0.06em !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.7rem !important;
        padding: 8px 10px !important; letter-spacing: 0.03em !important; }
    .land-wrap { margin: 40px auto; padding: 0 16px; }
    .land-title { font-size: 2rem !important; }
    .land-sub { font-size: 0.95rem !important; line-height: 1.6 !important; }
    .land-stats { gap: 10px; margin: 30px 0; }
    .land-stat { padding: 16px 22px; min-width: 105px; flex: 1; }
    .land-stat .num { font-size: 1.5rem; }
    .land-stat .lbl { font-size: 0.62rem; }
    .land-features { grid-template-columns: 1fr; margin-top: 30px; }
    .land-feature { padding: 16px; }
    .land-feature h4 { font-size: 0.88rem; }
    .land-feature p { font-size: 0.78rem; }
    .status-pill { font-size: 0.65rem; padding: 5px 11px; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1rem !important; }
    h4 { font-size: 0.9rem !important; }
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
# INDICATOR HELPERS  (UNCHANGED)
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
# CORE DETECTION ENGINE  (UNCHANGED)
# ─────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────
# BATCH FETCH  (UNCHANGED)
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
# PROCESS BATCH  (UNCHANGED)
# ─────────────────────────────────────────────────────────
def process_batch(batch_data, timeframes, days_back=10,
                  progress_cb=None, ticker_cb=None):
    t0 = time.time()
    tf_map = [(tf, TIMEFRAME_MAP[tf]) for tf in timeframes if tf in TIMEFRAME_MAP]

    all_results = []
    errors = []
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
                ).agg({
                    "open": "first", "high": "max",
                    "low": "min", "close": "last", "volume": "sum",
                }).dropna()

                if len(resampled) < 100:
                    continue

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
        return False, "Session Closed"
    in_session = (
        (now.hour > 9 or (now.hour == 9 and now.minute >= 15))
        and (now.hour < 15 or (now.hour == 15 and now.minute <= 30))
    )
    return (True, "Session Live") if in_session else (False, "Session Closed")

def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")

@st.cache_data(ttl=600, show_spinner=False)
def cached_batch(tickers_tuple):
    return batch_fetch(list(tickers_tuple), period="60d", interval="15m")


# ─────────────────────────────────────────────────────────
# ADVANCED ANALYTICS  (vol_score added to outputs)
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
    recent_low  = float(lookback["low"].min())
    dist_from_high = (float(bar["close"]) - recent_high) / recent_high * 100
    dist_from_low  = (float(bar["close"]) - recent_low) / recent_low * 100

    bars_since = len(scanned) - 1 - sig_pos
    if sig_pos < len(scanned) - 1:
        current_close = float(scanned.iloc[-1]["close"])
        change_since = (current_close - float(bar["close"])) / float(bar["close"]) * 100
    else:
        change_since = 0.0

    return {
        "vol_ratio": vol_ratio,
        "vol_score": vol_score,
        "dev": dev, "bias": bias,
        "quality": quality, "quality_label": label,
        "dist_from_high": dist_from_high,
        "dist_from_low": dist_from_low,
        "bars_since": int(bars_since),
        "change_since": float(change_since),
        "sig_pos": int(sig_pos),
        "bar": bar,
        "recent_high": recent_high,
        "recent_low": recent_low,
    }


def get_current_mtf_state(raw):
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
            scanned = detect_signals(rs)
            last = scanned.iloc[-1]
            vma = last.get("vol_ma", np.nan)
            vol_ratio = float(last["volume"] / vma) if (vma and vma > 0) else 0.0
            vol_score = min(100.0, max(0.0, (vol_ratio - 2.0) / 4.0 * 100))

            if bool(last["signal_final"]):
                status, icon = "Active", "🟢"
            elif bool(last["option_bottom_confirmed"]):
                status, icon = "Exhaustion", "🟡"
            elif float(last["raw_di_diff"]) < -10:
                status, icon = "Bias Only", "🔵"
            else:
                status, icon = "Quiet", "⚪"

            result[tf_name] = {
                "status": status, "icon": icon,
                "signal": bool(last["signal_final"]),
                "bias": float(last["raw_di_diff"]),
                "dev": float(last["distance_pct"]),
                "vol_ratio": vol_ratio,
                "vol_score": vol_score,
            }
        except Exception:
            result[tf_name] = None
    return result


def build_pro_chart(scanned, row, ctx, window_days=7):
    sig_dt = row["datetime"]
    start = sig_dt - pd.Timedelta(days=window_days)
    end   = sig_dt + pd.Timedelta(days=2)
    win = scanned.loc[(scanned.index >= start) & (scanned.index <= end)].copy()

    if win.empty:
        return None

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, row_heights=[0.74, 0.26])

    fig.add_trace(go.Candlestick(
        x=win.index, open=win["open"], high=win["high"],
        low=win["low"], close=win["close"], name="Price",
        increasing_line_color="#00e676", decreasing_line_color="#ff3d5a",
        increasing_fillcolor="rgba(0,230,118,0.25)",
        decreasing_fillcolor="rgba(255,61,90,0.25)",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=win.index, y=win["ema_value"], name="Baseline",
        line=dict(color="#00d4ff", width=1.6), opacity=0.85,
        hovertemplate="Baseline: %{y:.2f}<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[sig_dt], y=[float(ctx["bar"]["close"])],
        mode="markers+text",
        marker=dict(symbol="star", size=22, color="#ffcc00",
                    line=dict(color="#ffffff", width=2)),
        text=["SIGNAL"], textposition="top center",
        textfont=dict(color="#ffcc00", size=11, family="Inter"),
        name="Signal", hoverinfo="skip", showlegend=False,
    ), row=1, col=1)

    colors = ["#00e676" if c >= o else "#ff3d5a"
              for o, c in zip(win["open"], win["close"])]
    fig.add_trace(go.Bar(
        x=win.index, y=win["volume"], name="Volume",
        marker_color=colors, marker_line_width=0, opacity=0.7,
    ), row=2, col=1)

    fig.update_layout(
        height=560, template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(19, 24, 36, 0.55)",
        font=dict(family="Inter", color="#e0e6ed", size=11),
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False, hovermode="x unified", dragmode="pan",
    )
    fig.update_xaxes(rangeslider_visible=False, gridcolor="#1a2130")
    fig.update_yaxes(gridcolor="#1a2130", title_text="Price", row=1, col=1)
    fig.update_yaxes(gridcolor="#1a2130", title_text="Volume", row=2, col=1)
    return fig


def build_signal_timeline(ticker_df):
    """Timeline with Level labels instead of timeframes."""
    fig = go.Figure()
    level_colors = {
        "15m": "#00d4ff", "30m": "#00e676",
        "45m": "#ffcc00", "60m": "#ff7ab3",
    }
    for tf in LEVEL_ORDER:
        sub = ticker_df[ticker_df["timeframe"] == tf]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["datetime"], y=[LEVEL_LABEL[tf]] * len(sub),
            mode="markers",
            marker=dict(size=14, color=level_colors[tf],
                        line=dict(color="#ffffff", width=1)),
            name=LEVEL_LABEL[tf],
            hovertemplate=f"{LEVEL_LABEL[tf]}<br>%{{x|%d %b %H:%M}}<extra></extra>",
        ))
    fig.update_layout(
        height=170, template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(19, 24, 36, 0.55)",
        margin=dict(l=80, r=10, t=10, b=10),
        showlegend=False, font=dict(family="Inter", color="#e0e6ed", size=11),
    )
    fig.update_xaxes(gridcolor="#1a2130")
    fig.update_yaxes(gridcolor="#1a2130",
                     categoryorder="array",
                     categoryarray=[LEVEL_LABEL[t] for t in reversed(LEVEL_ORDER)])
    return fig


def generate_narrative(row, ctx, mtf):
    ticker = row["ticker"]
    level = LEVEL_LABEL[row["timeframe"]]
    sig_time = row["datetime"]

    aligned = [k for k, v in mtf.items() if v and v["signal"]]
    n_aligned = len(aligned)

    if n_aligned >= 3:
        conviction = "**high conviction** — broad multi-level alignment"
    elif n_aligned == 2:
        conviction = "**moderate conviction** — partial level agreement"
    elif n_aligned == 1:
        conviction = "**single-level signal** — confirmation pending"
    else:
        conviction = "**historical signal** — current state has cooled"

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
        parts.append(
            f"Price has moved **{ctx['change_since']:+.2f}%** since the signal "
            f"({ctx['bars_since']} bars ago)."
        )

    return " ".join(parts)


# ─────────────────────────────────────────────────────────
# LANDING SCREEN
# ─────────────────────────────────────────────────────────
if not st.session_state.get("entered"):
    st.markdown(f"""
    <div class="land-wrap">
        <div class="land-eyebrow">◈ {BRAND_NAME.upper()}</div>
        <h1 class="land-title">Signal Detection Suite</h1>
        <p class="land-sub">
            A multi-level confluence engine that identifies high-probability
            exhaustion patterns across four intraday analysis horizons.
        </p>
        <div class="land-stats">
            <div class="land-stat"><div class="num">4</div><div class="lbl">Levels</div></div>
            <div class="land-stat"><div class="num">2</div><div class="lbl">Stage Filters</div></div>
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
                <p>Every signal is graded 0–100 on volume, exhaustion depth,
                   and directional bias strength.</p>
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
        if st.button("▶  Enter Suite", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────
live, status_label = market_status()
pill_cls = "status-live" if live else "status-closed"
dot_cls  = "dot-live" if live else "dot-closed"

st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">◈ {BRAND_NAME.upper()}</div>
    <div class="hero-title">Signal Detection Suite</div>
    <p class="hero-sub">Multi-level confluence engine · 4 analysis horizons</p>
    <div class="status-pill {pill_cls}">
        <span class="dot {dot_cls}"></span> {status_label}
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# CONTROL PANEL
# ─────────────────────────────────────────────────────────
st.markdown('<div class="control-card">', unsafe_allow_html=True)
st.markdown('<div class="control-title">⚙ SCAN CONFIGURATION</div>', unsafe_allow_html=True)

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
    max_tickers = st.slider(
        "Max Instruments", min_value=10, max_value=len(base),
        value=len(base), step=10,
    )
tickers = base[:max_tickers]

rc3, rc4 = st.columns([3, 2])
with rc3:
    st.markdown("**Analysis Levels**")
    lvl_cols = st.columns(4)
    lvl_1 = lvl_cols[0].checkbox("Level 1", value=True, help="Shortest horizon")
    lvl_2 = lvl_cols[1].checkbox("Level 2", value=True, help="Short horizon")
    lvl_3 = lvl_cols[2].checkbox("Level 3", value=True, help="Medium horizon")
    lvl_4 = lvl_cols[3].checkbox("Level 4", value=True, help="Long horizon")
    selected_tfs = [tf for tf, on in
                    [("15m", lvl_1), ("30m", lvl_2),
                     ("45m", lvl_3), ("60m", lvl_4)] if on]
with rc4:
    days_back = st.slider("Look-back Window (days)", 5, 30, 10, 1)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns([2, 1, 1, 1])
with b1:
    run_btn = st.button("▶  RUN SCAN", use_container_width=True, type="primary")
with b2:
    refresh_btn = st.button("🔄  Refresh", use_container_width=True)
with b3:
    clear_btn = st.button("🗑  Clear", use_container_width=True)
with b4:
    if st.session_state.get("scan_out"):
        df_now = st.session_state.scan_out["results_df"]
        if not df_now.empty:
            st.download_button(
                "⬇  Export", data=to_csv_bytes(df_now),
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
    fetch_slot.info(f"📡 Fetching data for {len(tickers)} instruments…")
    batch_data, fetch_err = cached_batch(tuple(tickers))

    if fetch_err:
        fetch_slot.empty()
        st.error(f"Fetch failed: {fetch_err}")
        st.stop()
    if not batch_data:
        fetch_slot.empty()
        st.error("No data returned. Try **Refresh** and scan again.")
        st.stop()

    fetch_slot.success(f"✅  {len(batch_data)}/{len(tickers)} instruments loaded. Processing…")

    progress = st.progress(0.0, text="Detecting signals…")
    status = st.empty()

    def _prog(p):
        progress.progress(min(p, 1.0), text=f"Scanning… {int(p*100)}%")

    def _tick(name, n):
        if n > 0:
            status.success(f"🎯  **{name}** — {n} qualified")
        else:
            status.info(f"🔍  {name}")

    out = process_batch(batch_data, selected_tfs, days_back=days_back,
                        progress_cb=_prog, ticker_cb=_tick)
    progress.empty()
    status.empty()
    fetch_slot.empty()

    st.session_state.scan_out = out
    st.session_state.scan_meta = {
        "tickers_scanned": len(batch_data),
        "timeframes": selected_tfs,
        "days_back": days_back,
    }
    st.success(
        f"✅  Scan complete — **{len(out['results_df'])} signal(s)** "
        f"across {len(batch_data)} instruments in {out['scan_time_s']}s."
    )


# ─────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────
out = st.session_state.scan_out

if out is None:
    st.info("👆  Configure the scan above, then click **▶ RUN SCAN**.")
    st.stop()

df   = out["results_df"]
diag = out["diag"]
meta = st.session_state.get("scan_meta", {})

levels_str = " · ".join([LEVEL_LABEL[t] for t in meta.get("timeframes", [])])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Instruments Scanned", meta.get("tickers_scanned", out.get("tickers_processed", 0)))
k2.metric("Signals Detected", len(df),
          delta=f"{df['ticker'].nunique()} unique" if len(df) else "none")
k3.metric("Scan Duration", f"{out['scan_time_s']}s")
k4.metric("Active Levels", levels_str)

tab_sig, tab_chart, tab_diag, tab_err = st.tabs(
    ["🎯 Signals", "📈 Chart", "📊 Analytics", "⚠ Notes"]
)


# ═════════════════════════════════════════════════════════
# TAB 1 — SIGNALS (presentable + top 3 green)
# ═════════════════════════════════════════════════════════
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
            )
        with f2:
            tk_f = st.multiselect(
                "Instrument",
                sorted(df["ticker"].unique().tolist()),
                default=[], placeholder="All instruments",
            )
        with f3:
            min_bias = st.slider(
                "Max Bias threshold",
                float(df["raw_di_diff"].min()), 0.0, 0.0,
            )

        filt = df[df["timeframe"].isin(tf_f) & (df["raw_di_diff"] <= min_bias)]
        if tk_f:
            filt = filt[filt["ticker"].isin(tk_f)]
        filt = filt.sort_values(["datetime", "ticker"], ascending=[False, True])

        # ── Build clean display table ──────────────────
        disp = filt.copy().reset_index(drop=True)
        disp.insert(0, "Rank", range(1, len(disp) + 1))
        disp["Timestamp"] = disp["datetime"].dt.strftime("%d %b %Y · %H:%M")
        disp["Instrument"] = disp["ticker"]
        disp["Level"] = disp["timeframe"].map(LEVEL_LABEL)
        disp["Last Price"] = disp["close"].round(2)
        disp["Deviation"] = disp["distance_pct"].round(2)
        disp["Bias"] = disp["raw_di_diff"].round(2)

        cols_show = ["Rank", "Timestamp", "Instrument", "Level",
                     "Last Price", "Deviation", "Bias"]
        disp = disp[cols_show]

        # ── Highlight top 3 most recent rows green ─────
        top3_set = set(range(min(3, len(disp))))

        def _style_row(row):
            if row.name in top3_set:
                return (['background-color: rgba(0, 230, 118, 0.12); '
                         'color: #00e676; font-weight: 600'] * len(row))
            return [''] * len(row)

        styled = disp.style.apply(_style_row, axis=1)

        st.dataframe(
            styled,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("#", width="small"),
                "Timestamp": st.column_config.TextColumn("🕐 Timestamp", width="medium"),
                "Instrument": st.column_config.TextColumn("📊 Instrument", width="small"),
                "Level": st.column_config.TextColumn("◈ Level", width="small"),
                "Last Price": st.column_config.NumberColumn("Last", format="%.2f", width="small"),
                "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%", width="small"),
                "Bias": st.column_config.NumberColumn("Bias", format="%.2f", width="small"),
            },
        )

        st.caption("🟢 Green rows mark the 3 most recent signals.")


# ═════════════════════════════════════════════════════════
# TAB 2 — CHART (Level labels + Quant Score)
# ═════════════════════════════════════════════════════════
with tab_chart:
    if df.empty:
        st.info("No signals available — run a scan with at least one qualified hit.")
    else:
        labels = df.apply(
            lambda r: f"{r['ticker']} · {LEVEL_LABEL[r['timeframe']]} · "
                      f"{r['datetime']:%d %b %Y %H:%M}",
            axis=1,
        ).tolist()
        pick = st.selectbox("Select a signal to analyse", labels, key="chart_pick")
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
            rs = raw.resample(
                rule, origin="start_day", offset="9h15min",
                label="left", closed="left",
            ).agg({
                "open": "first", "high": "max", "low": "min",
                "close": "last", "volume": "sum",
            }).dropna()

            scanned = detect_signals(rs)
            ctx = compute_signal_context(scanned, row)
            mtf = get_current_mtf_state(raw)

            # ─── Quant Scorecard ──────────────────────────
            q1, q2, q3, q4, q5 = st.columns(5)
            q1.metric("Signal Quality", f"{ctx['quality']}/100", ctx["quality_label"])
            q2.metric("Quant Score", f"{ctx['vol_score']:.0f}/100",
                      "high" if ctx['vol_score'] >= 50 else "moderate")
            q3.metric("Deviation", f"{ctx['dev']:.2f}%")
            q4.metric("Bias", f"{ctx['bias']:.2f}")
            q5.metric("Bars Since", ctx["bars_since"], f"{ctx['change_since']:+.2f}%")

            # ─── Main Chart ────────────────────────────────
            st.markdown("#### Price Action · Signal Overlay")
            fig = build_pro_chart(scanned, row, ctx, window_days=7)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": True, "displaylogo": False})
            else:
                st.warning("No price bars available around this signal.")

            # ─── Level Alignment Matrix ────────────────────
            st.markdown("#### Level Alignment Matrix")
            mtf_rows = []
            for tf_name in LEVEL_ORDER:
                state = mtf.get(tf_name)
                if state is None:
                    mtf_rows.append({
                        "Level": LEVEL_LABEL[tf_name], "Status": "—",
                        "Bias": "—", "Deviation": "—", "Quant Score": "—",
                    })
                else:
                    mtf_rows.append({
                        "Level": LEVEL_LABEL[tf_name],
                        "Status": f"{state['icon']}  {state['status']}",
                        "Bias": round(state["bias"], 2),
                        "Deviation": round(state["dev"], 2),
                        "Quant Score": round(state["vol_score"], 0),
                    })
            st.dataframe(
                pd.DataFrame(mtf_rows),
                use_container_width=True, hide_index=True,
                column_config={
                    "Level": st.column_config.TextColumn("◈ Level", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="medium"),
                    "Bias": st.column_config.NumberColumn("Bias", format="%.2f"),
                    "Deviation": st.column_config.NumberColumn("Dev %", format="%.2f%%"),
                    "Quant Score": st.column_config.NumberColumn("Quant Score", format="%.0f"),
                },
            )

            # ─── Automated Analysis ────────────────────────
            st.markdown("#### Automated Analysis")
            st.info(generate_narrative(row, ctx, mtf))

            # ─── Signal History timeline ───────────────────
            ticker_hist = df[df["ticker"] == row["ticker"]].copy()
            if len(ticker_hist) >= 1:
                st.markdown("#### Signal History · This Instrument")
                timeline_fig = build_signal_timeline(ticker_hist)
                st.plotly_chart(timeline_fig, use_container_width=True,
                                config={"displayModeBar": False})

            # ─── Swing Context ─────────────────────────────
            st.markdown("#### Swing Context")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Recent High", f"{ctx['recent_high']:.2f}",
                      f"{ctx['dist_from_high']:.2f}%")
            s2.metric("Recent Low", f"{ctx['recent_low']:.2f}",
                      f"{ctx['dist_from_low']:+.2f}%")
            s3.metric("Bars Since Signal", ctx["bars_since"])
            s4.metric("Change Since", f"{ctx['change_since']:+.2f}%")

            # ─── Related signals ───────────────────────────
            related = df[(df["ticker"] == row["ticker"])].copy()
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
                        },
                    )


# ═════════════════════════════════════════════════════════
# TAB 3 — ANALYTICS
# ═════════════════════════════════════════════════════════
with tab_diag:
    st.markdown("### Detection Funnel")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Filter 1 Match", diag["stage_a"])
    d2.metric("Filter 2 Match", diag["stage_b"])
    d3.metric("Qualified", diag["final"])
    d4.metric("No Data", diag["empty_data"])
    st.caption(
        f"Window cutoff: {out['cutoff']} · Duration: {out['scan_time_s']}s · "
        f"Instruments processed: {out.get('tickers_processed', 0)}"
    )


# ═════════════════════════════════════════════════════════
# TAB 4 — NOTES
# ═════════════════════════════════════════════════════════
with tab_err:
    if not out["errors"]:
        st.success("No exceptions — all instruments processed cleanly.")
    else:
        st.warning(f"{len(out['errors'])} instrument(s) returned a processing note.")
        st.dataframe(pd.DataFrame(out["errors"], columns=["Instrument", "Note"]),
                     use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────
# FOOTER — Fintrix Branding
# ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="fintrix-footer">
    <div class="brand">Powered by {BRAND_NAME}</div>
    <div class="tag">SIGNAL INTELLIGENCE PLATFORM</div>
</div>
""", unsafe_allow_html=True)
