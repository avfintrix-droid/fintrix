import numpy as np
import pandas as pd
import yfinance as yf
import warnings
import time
import streamlit as st
from datetime import datetime, timedelta
import pytz

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Signal Detection Suite",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 0%, #0f1a2e 0%, #0a0e1a 40%, #060910 100%); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px; }

/* Landing */
.land-wrap { max-width: 900px; margin: 80px auto; text-align: center; }
.land-eyebrow { font-size: 0.72rem; letter-spacing: 0.28em; color: #00d4ff;
    font-weight: 700; text-transform: uppercase; margin-bottom: 16px; }
.land-title { font-size: 3.4rem; font-weight: 900;
    background: linear-gradient(90deg, #ffffff, #a8e6ff, #00d4ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 20px 0; letter-spacing: -0.035em; line-height: 1.05; }
.land-sub { color: #8892a6; font-size: 1.12rem; line-height: 1.75;
    margin-bottom: 6px; max-width: 640px; margin-left: auto; margin-right: auto; }
.land-stats { display: flex; gap: 20px; justify-content: center; margin: 48px 0; flex-wrap: wrap; }
.land-stat { background: linear-gradient(135deg, #131824, #182135);
    border: 1px solid #1e2a3f; border-radius: 14px; padding: 24px 36px; min-width: 160px;
    transition: border-color 0.2s ease, transform 0.2s ease; }
.land-stat:hover { border-color: rgba(0,212,255,0.4); transform: translateY(-2px); }
.land-stat .num { color: #00d4ff; font-size: 2rem; font-weight: 800;
    font-family: 'JetBrains Mono', monospace; }
.land-stat .lbl { color: #8892a6; font-size: 0.78rem; margin-top: 6px;
    letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }
.land-features { display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 16px; margin-top: 48px; text-align: left; }
.land-feature { background: rgba(19, 24, 36, 0.65); border: 1px solid #1e2a3f;
    border-radius: 14px; padding: 22px; }
.land-feature h4 { color: #e0e6ed; font-size: 0.94rem; margin: 0 0 8px 0;
    font-weight: 700; letter-spacing: -0.01em; }
.land-feature p { color: #6b7a90; font-size: 0.85rem; margin: 0; line-height: 1.6; }

/* Hero */
.hero-wrap { background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,230,118,0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.18); border-radius: 16px;
    padding: 26px 32px; margin-bottom: 20px;
    box-shadow: 0 8px 40px rgba(0, 212, 255, 0.06); }
.hero-eyebrow { font-size: 0.72rem; letter-spacing: 0.28em; color: #00d4ff;
    font-weight: 700; text-transform: uppercase; margin-bottom: 6px; }
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
.dot-live { background: #00e676; box-shadow: 0 0 8px #00e676;
    animation: pulse 1.8s infinite; }
.dot-closed { background: #ffab00; }
@keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.35 } }

/* Control panel */
.control-card { background: linear-gradient(135deg, #131824 0%, #182135 100%);
    border: 1px solid #1e2a3f; border-radius: 16px;
    padding: 26px 30px; margin-bottom: 20px;
    box-shadow: 0 6px 32px rgba(0,0,0,0.35); }
.control-title { color: #00d4ff; font-size: 0.76rem; letter-spacing: 0.18em;
    font-weight: 800; text-transform: uppercase; margin-bottom: 18px; }

/* Metrics */
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
h2, h3 { color: #e0e6ed !important; }
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
# CORE DETECTION ENGINE
# ─────────────────────────────────────────────────────────
def detect_signals(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(c).lower() for c in df.columns]
    results = df.copy()

    # Condition A — Exhaustion bottom with momentum reversal
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

    # Condition B — Directional bias threshold
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

    # Final confluence
    results["signal_final"] = (
        results["option_bottom_confirmed"] & (results["raw_di_diff"] < -10)
    )
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
# PROCESS BATCH
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
# LANDING SCREEN
# ─────────────────────────────────────────────────────────
if not st.session_state.get("entered"):
    st.markdown("""
    <div class="land-wrap">
        <div class="land-eyebrow">◈ SIGNAL INTELLIGENCE</div>
        <h1 class="land-title">Signal Detection Suite</h1>
        <p class="land-sub">
            A multi-timeframe confluence engine that identifies high-probability
            exhaustion patterns across intraday horizons — <b>15m</b>, <b>30m</b>,
            <b>45m</b> and <b>60m</b>.
        </p>
        <div class="land-stats">
            <div class="land-stat"><div class="num">4</div><div class="lbl">Timeframes</div></div>
            <div class="land-stat"><div class="num">2</div><div class="lbl">Stage Filters</div></div>
            <div class="land-stat"><div class="num">250+</div><div class="lbl">Instruments</div></div>
        </div>
        <div class="land-features">
            <div class="land-feature">
                <h4>Multi-timeframe Confluence</h4>
                <p>Independent detection across four intraday horizons ensures
                   only durable signals surface.</p>
            </div>
            <div class="land-feature">
                <h4>Two-Stage Filtering</h4>
                <p>Every candidate must pass an exhaustion gate and a bias
                   gate on the same bar to qualify.</p>
            </div>
            <div class="land-feature">
                <h4>On-Demand Scan</h4>
                <p>Nothing runs automatically. Configure your scope,
                   trigger a scan, review qualified hits.</p>
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
    <div class="hero-eyebrow">◈ SIGNAL INTELLIGENCE</div>
    <div class="hero-title">Signal Detection Suite</div>
    <p class="hero-sub">
        Multi-timeframe confluence · 15m / 30m / 45m / 60m
    </p>
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
        "Max Instruments",
        min_value=10, max_value=len(base),
        value=min(50, len(base)), step=10,
        help="Lower this for faster scans.",
    )
tickers = base[:max_tickers]

rc3, rc4 = st.columns([3, 2])
with rc3:
    st.markdown("**Timeframes**")
    tf_cols = st.columns(4)
    tf_15 = tf_cols[0].checkbox("15m", value=True)
    tf_30 = tf_cols[1].checkbox("30m", value=True)
    tf_45 = tf_cols[2].checkbox("45m", value=True)
    tf_60 = tf_cols[3].checkbox("60m", value=True)
    selected_tfs = [t for t, on in
                    [("15m", tf_15), ("30m", tf_30),
                     ("45m", tf_45), ("60m", tf_60)] if on]
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
        st.error("Select at least one timeframe.")
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

k1, k2, k3, k4 = st.columns(4)
k1.metric("Instruments Scanned", meta.get("tickers_scanned", out.get("tickers_processed", 0)))
k2.metric("Signals Detected", len(df),
          delta=f"{df['ticker'].nunique()} unique" if len(df) else "none")
k3.metric("Scan Duration", f"{out['scan_time_s']}s")
k4.metric("Active Timeframes", " · ".join(meta.get("timeframes", [])))

tab_sig, tab_chart, tab_diag, tab_err, tab_info = st.tabs(
    ["🎯 Signals", "📈 Chart", "📊 Analytics", "⚠ Notes", "ℹ Info"]
)

# ── Tab 1: Signals
with tab_sig:
    if df.empty:
        st.info(f"No signals detected in the last {meta.get('days_back', 10)} days.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            tf_f = st.multiselect("Timeframe",
                sorted(df["timeframe"].unique().tolist()),
                default=sorted(df["timeframe"].unique().tolist()))
        with f2:
            tk_f = st.multiselect("Instrument",
                sorted(df["ticker"].unique().tolist()),
                default=[], placeholder="All instruments")
        with f3:
            min_bias = st.slider("Max Bias threshold",
                float(df["raw_di_diff"].min()), 0.0,
                float(df["raw_di_diff"].min()))

        filt = df[df["timeframe"].isin(tf_f) & (df["raw_di_diff"] <= min_bias)]
        if tk_f:
            filt = filt[filt["ticker"].isin(tk_f)]
        filt = filt.sort_values(["datetime", "ticker"], ascending=[False, True])

        disp = filt.copy()
        disp["datetime"] = disp["datetime"].dt.strftime("%Y-%m-%d %H:%M")
        for c in ["close", "distance_pct", "raw_di_diff"]:
            disp[c] = disp[c].round(2)

        st.dataframe(disp, use_container_width=True, hide_index=True,
            column_config={
                "datetime": st.column_config.TextColumn("Timestamp", width="medium"),
                "ticker": st.column_config.TextColumn("Instrument", width="small"),
                "timeframe": st.column_config.TextColumn("TF", width="small"),
                "close": st.column_config.NumberColumn("Last", format="%.2f"),
                "distance_pct": st.column_config.NumberColumn("Dev %", format="%.2f%%"),
                "raw_di_diff": st.column_config.NumberColumn("Bias", format="%.2f"),
            })

# ── Tab 2: Chart
with tab_chart:
    if df.empty:
        st.info("No signals to chart.")
    else:
        labels = df.apply(lambda r: f"{r['ticker']} · {r['timeframe']} · "
                                     f"{r['datetime']:%d %b %H:%M}", axis=1).tolist()
        pick = st.selectbox("Select signal", labels)
        idx = labels.index(pick)
        row = df.iloc[idx]
        st.caption(f"**{row['ticker']}** · **{row['timeframe']}** · "
                   f"Last {row['close']:.2f} · Dev {row['distance_pct']:.2f}% · "
                   f"Bias {row['raw_di_diff']:.2f}")
        try:
            data, _ = cached_batch((row["ticker"],))
            if row["ticker"] in data:
                raw = data[row["ticker"]].copy()
                if not isinstance(raw.index, pd.DatetimeIndex):
                    raw.index = pd.to_datetime(raw.index)
                if raw.index.tz is None:
                    raw.index = raw.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
                else:
                    raw.index = raw.index.tz_convert("Asia/Kolkata")
                rs = raw.resample(TIMEFRAME_MAP[row["timeframe"]],
                    origin="start_day", offset="9h15min",
                    label="left", closed="left").agg({
                        "open":"first","high":"max","low":"min",
                        "close":"last","volume":"sum"}).dropna()
                win = rs.loc[(rs.index >= row["datetime"] - pd.Timedelta(days=5)) &
                             (rs.index <= row["datetime"] + pd.Timedelta(days=2))]
                if not win.empty:
                    st.line_chart(win["close"], height=360, use_container_width=True)
                else:
                    st.warning("No bars available around this signal.")
        except Exception as e:
            st.error(f"Chart unavailable: {e}")

# ── Tab 3: Analytics
with tab_diag:
    st.markdown("### Detection Funnel")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Stage 1 Match", diag["stage_a"])
    d2.metric("Stage 2 Match", diag["stage_b"])
    d3.metric("Qualified", diag["final"])
    d4.metric("No Data", diag["empty_data"])
    st.caption(
        f"Window cutoff: {out['cutoff']} · Duration: {out['scan_time_s']}s · "
        f"Instruments processed: {out.get('tickers_processed', 0)}"
    )

# ── Tab 4: Notes
with tab_err:
    if not out["errors"]:
        st.success("No exceptions — all instruments processed cleanly.")
    else:
        st.warning(f"{len(out['errors'])} instrument(s) returned a processing note.")
        st.dataframe(pd.DataFrame(out["errors"], columns=["Instrument", "Note"]),
                     use_container_width=True, hide_index=True)

# ── Tab 5: Info
with tab_info:
    st.markdown("""
### Signal Detection Suite

A **multi-timeframe confluence scanner** that surfaces high-probability
exhaustion patterns across intraday horizons.

#### Coverage
- **Timeframes:** 15m · 30m · 45m · 60m
- **Universe:** Standard · High Volatility · Full
- **Look-back:** Configurable 5–30 days

#### Method
Two independent stage filters must both trigger on the same bar before a
signal qualifies. This strict overlap reduces noise and improves signal
quality — fewer but higher-conviction candidates.

#### Output
- Qualified signal table with timestamp, last price, deviation, and bias
- Per-signal chart overlay
- Stage-by-stage detection funnel
- CSV export

---
*For informational purposes only. Not investment advice. Verify every
signal against your own risk framework before acting.*
    """)