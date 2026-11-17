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
    page_title="Oversold Core Scanner",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
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

.land-wrap { max-width: 860px; margin: 70px auto; text-align: center; }
.land-eyebrow { font-size: 0.72rem; letter-spacing: 0.25em; color: #00d4ff;
    font-weight: 700; text-transform: uppercase; margin-bottom: 14px; }
.land-title { font-size: 3.2rem; font-weight: 900;
    background: linear-gradient(90deg, #ffffff, #a8e6ff, #00d4ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 18px 0; letter-spacing: -0.03em; }
.land-sub { color: #8892a6; font-size: 1.1rem; line-height: 1.7; margin-bottom: 8px; }
.land-stats { display: flex; gap: 20px; justify-content: center; margin: 44px 0; flex-wrap: wrap; }
.land-stat { background: linear-gradient(135deg, #131824, #182135);
    border: 1px solid #1e2a3f; border-radius: 14px; padding: 22px 32px; min-width: 150px; }
.land-stat .num { color: #00d4ff; font-size: 1.9rem; font-weight: 800;
    font-family: 'JetBrains Mono', monospace; }
.land-stat .lbl { color: #8892a6; font-size: 0.82rem; margin-top: 4px;
    letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600; }
.land-features { display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 16px; margin-top: 40px; text-align: left; }
.land-feature { background: rgba(19, 24, 36, 0.6); border: 1px solid #1e2a3f;
    border-radius: 12px; padding: 20px; }
.land-feature h4 { color: #e0e6ed; font-size: 0.95rem; margin: 0 0 6px 0; }
.land-feature p { color: #6b7a90; font-size: 0.85rem; margin: 0; line-height: 1.5; }

.hero-wrap { background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,230,118,0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.18); border-radius: 16px;
    padding: 26px 32px; margin-bottom: 20px;
    box-shadow: 0 8px 40px rgba(0, 212, 255, 0.06); }
.hero-eyebrow { font-size: 0.72rem; letter-spacing: 0.25em; color: #00d4ff;
    font-weight: 700; text-transform: uppercase; margin-bottom: 6px; }
.hero-title { font-size: 2.1rem; font-weight: 800;
    background: linear-gradient(90deg, #ffffff 0%, #a8e6ff 60%, #00d4ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0; letter-spacing: -0.02em; }
.hero-sub { color: #6b7a90; font-size: 0.94rem; margin: 0; }
.status-pill { display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 14px; border-radius: 999px; font-size: 0.78rem;
    font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    margin-top: 14px; }
.status-live { background: rgba(0,230,118,0.12); color: #00e676;
    border: 1px solid rgba(0,230,118,0.35); }
.status-closed { background: rgba(255,171,0,0.10); color: #ffab00;
    border: 1px solid rgba(255,171,0,0.35); }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-live { background: #00e676; box-shadow: 0 0 8px #00e676;
    animation: pulse 1.8s infinite; }
.dot-closed { background: #ffab00; }
@keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.35 } }

.control-card { background: linear-gradient(135deg, #131824 0%, #182135 100%);
    border: 1px solid #1e2a3f; border-radius: 16px;
    padding: 24px 28px; margin-bottom: 20px;
    box-shadow: 0 6px 32px rgba(0,0,0,0.35); }
.control-title { color: #00d4ff; font-size: 0.78rem; letter-spacing: 0.15em;
    font-weight: 800; text-transform: uppercase; margin-bottom: 16px; }

[data-testid="stMetric"] { background: linear-gradient(135deg, #131824, #182135);
    border: 1px solid #1e2a3f; border-radius: 14px;
    padding: 18px 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.35); }
[data-testid="stMetricLabel"] { color: #6b7a90 !important; font-size: 0.75rem !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
    font-weight: 700 !important; }
[data-testid="stMetricValue"] { color: #e0e6ed !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important; font-size: 1.9rem !important; }

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #00d4ff 0%, #00a3cc 100%);
    color: #0a0e1a !important; border: none; font-weight: 800;
    letter-spacing: 0.08em; padding: 0.9rem 2rem; border-radius: 12px;
    font-size: 1rem; box-shadow: 0 6px 24px rgba(0, 212, 255, 0.35);
    transition: all 0.2s ease; text-transform: uppercase; }
.stButton > button[kind="primary"]:hover { transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.55); }

.stDownloadButton > button {
    background: linear-gradient(90deg, #00e676 0%, #00b862 100%);
    color: #0a0e1a !important; font-weight: 700;
    border-radius: 10px; border: none; padding: 0.6rem 1.4rem; }

[data-testid="stSidebar"] { background: linear-gradient(180deg, #0c1220 0%, #080c15 100%);
    border-right: 1px solid #1a2130; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #00d4ff !important; letter-spacing: 0.05em;
    font-size: 0.82rem !important; text-transform: uppercase;
    font-weight: 800; margin-top: 1rem; }

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
# WATCHLISTS
# ─────────────────────────────────────────────────────────
NSE_FO_TICKERS = [
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

HIGH_BETA_TICKERS = [
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

ALL_TICKERS = list(dict.fromkeys(
    [t.replace(".NS", "") for t in (NSE_FO_TICKERS + HIGH_BETA_TICKERS)]
))

TIMEFRAME_MAP = {"5m": "5min", "10m": "10min", "15m": "15min"}


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
# CORE SCANNER
# ─────────────────────────────────────────────────────────
def scan_combined_oversold_stocks(df):
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
# BATCH FETCH  ✅ FIXED: lowercase columns at extraction
# ─────────────────────────────────────────────────────────
def batch_fetch(tickers, period="15d", interval="5m"):
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
        return {}, "yfinance returned empty data (rate-limit or network)"

    out = {}
    if isinstance(raw.columns, pd.MultiIndex):
        available = raw.columns.get_level_values(0).unique()
        for sym in symbols:
            if sym not in available:
                continue
            df = raw[sym].dropna(how="all")
            if df.empty:
                continue
            df.columns = [str(c).lower() for c in df.columns]   # ✅ FIX
            out[sym.replace(".NS", "")] = df
    else:
        if len(symbols) == 1 and not raw.dropna(how="all").empty:
            df = raw.dropna(how="all")
            df.columns = [str(c).lower() for c in df.columns]   # ✅ FIX
            out[symbols[0].replace(".NS", "")] = df

    return out, None


# ─────────────────────────────────────────────────────────
# PROCESS BATCH  ✅ FIXED: defensive lowercase + volume guard
# ─────────────────────────────────────────────────────────
def process_batch(batch_data, timeframes, days_back=10,
                  progress_cb=None, ticker_cb=None):
    t0 = time.time()
    tf_map = [(tf, TIMEFRAME_MAP[tf]) for tf in timeframes if tf in TIMEFRAME_MAP]

    all_results = []
    errors = []
    diag_total = {"empty_data": 0, "option_bottom": 0, "di_negative": 0, "final": 0}

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

            # ✅ FIX: normalize columns before volume filter
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            raw.columns = [str(c).lower() for c in raw.columns]

            # ✅ FIX: guard against missing volume column
            if "volume" not in raw.columns:
                errors.append((ticker, "no 'volume' column in data"))
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

                scanned = scan_combined_oversold_stocks(resampled)

                diag_total["option_bottom"] += int(scanned["option_bottom_confirmed"].sum())
                diag_total["di_negative"] += int((scanned["raw_di_diff"] < -10).sum())
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
        return False, f"Weekend · {now:%a %d %b %Y}"
    in_session = (
        (now.hour > 9 or (now.hour == 9 and now.minute >= 15))
        and (now.hour < 15 or (now.hour == 15 and now.minute <= 30))
    )
    if in_session:
        return True, f"Market Open · {now:%H:%M IST}"
    return False, f"Market Closed · {now:%a %d %b, %H:%M IST}"

def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")

@st.cache_data(ttl=600, show_spinner=False)
def cached_batch(tickers_tuple):
    return batch_fetch(list(tickers_tuple), period="15d", interval="5m")


# ─────────────────────────────────────────────────────────
# LANDING SCREEN
# ─────────────────────────────────────────────────────────
if not st.session_state.get("entered"):
    st.markdown("""
    <div class="land-wrap">
        <div class="land-eyebrow">◈ QUANT SCANNER · NSE INDIA</div>
        <h1 class="land-title">Oversold Core Scanner</h1>
        <p class="land-sub">
            Two-condition confluence engine that detects high-conviction
            exhaustion signals across <b>5m</b>, <b>10m</b> and <b>15m</b>.
        </p>
        <div class="land-stats">
            <div class="land-stat"><div class="num">2</div><div class="lbl">Core Conditions</div></div>
            <div class="land-stat"><div class="num">3</div><div class="lbl">Timeframes</div></div>
            <div class="land-stat"><div class="num">250+</div><div class="lbl">NSE Equities</div></div>
        </div>
        <div class="land-features">
            <div class="land-feature">
                <h4>🎯 Option-Strike Bottom</h4>
                <p>Close ≤ −2.5σ below EMA-20 · DI up-turn · Vol &gt; 2× MA-20</p>
            </div>
            <div class="land-feature">
                <h4>⚡ Bearish DI Dominance</h4>
                <p>+DI − −DI &lt; −10 on a 100-bar RMA</p>
            </div>
            <div class="land-feature">
                <h4>🎛 Manual Control</h4>
                <p>Nothing runs automatically. Configure, press RUN SCAN.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1, 1, 1])
    with c:
        if st.button("▶  Enter Dashboard", use_container_width=True, type="primary"):
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
    <div class="hero-eyebrow">◈ QUANT SCANNER · NSE INDIA</div>
    <div class="hero-title">Oversold Core Signal Detection</div>
    <p class="hero-sub">
        Two-condition confluence · <b>Option-Strike Bottom</b> + <b>DI &lt; −10</b>
        &nbsp;·&nbsp; 5m / 10m / 15m timeframes
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
st.markdown('<div class="control-title">⚙ SCAN CONTROL PANEL</div>', unsafe_allow_html=True)

rc1, rc2 = st.columns([2, 1])
with rc1:
    universe = st.radio(
        "Universe",
        ["NSE F&O (~190)", "High Beta (~60)", "Combined (~250)"],
        index=2, horizontal=True,
    )
    if universe.startswith("NSE"):
        base = [t.replace(".NS", "") for t in NSE_FO_TICKERS]
    elif universe.startswith("High"):
        base = [t.replace(".NS", "") for t in HIGH_BETA_TICKERS]
    else:
        base = ALL_TICKERS
with rc2:
    max_tickers = st.slider(
        "Max tickers", min_value=10, max_value=len(base),
        value=min(50, len(base)), step=10,
    )
tickers = base[:max_tickers]

rc3, rc4 = st.columns([2, 1])
with rc3:
    st.markdown("**Timeframes**")
    tf_cols = st.columns(3)
    tf_5  = tf_cols[0].checkbox("5m",  value=True)
    tf_10 = tf_cols[1].checkbox("10m", value=True)
    tf_15 = tf_cols[2].checkbox("15m", value=True)
    selected_tfs = [t for t, on in
                    [("5m", tf_5), ("10m", tf_10), ("15m", tf_15)] if on]
with rc4:
    days_back = st.slider("Look-back (days)", 3, 15, 10, 1)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns([2, 1, 1, 1])
with b1:
    run_btn = st.button("▶  RUN SCAN", use_container_width=True, type="primary")
with b2:
    refresh_btn = st.button("🔄  Refresh Data", use_container_width=True)
with b3:
    clear_btn = st.button("🗑  Clear Results", use_container_width=True)
with b4:
    if st.session_state.get("scan_out"):
        df_now = st.session_state.scan_out["results_df"]
        if not df_now.empty:
            st.download_button(
                "⬇  CSV", data=to_csv_bytes(df_now),
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
    st.success("Cache cleared. Next scan will fetch fresh data.")


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
        st.error("No tickers selected.")
        st.stop()

    fetch_slot = st.empty()
    fetch_slot.info(f"📡 Fetching {len(tickers)} tickers from Yahoo Finance…")
    batch_data, fetch_err = cached_batch(tuple(tickers))

    if fetch_err:
        fetch_slot.empty()
        st.error(f"Fetch failed: {fetch_err}")
        st.stop()
    if not batch_data:
        fetch_slot.empty()
        st.error("No data returned. Try **Refresh Data** and scan again.")
        st.stop()

    fetch_slot.success(f"✅  Fetched {len(batch_data)}/{len(tickers)} tickers. Processing…")

    progress = st.progress(0.0, text="Processing indicators…")
    status = st.empty()

    def _prog(p):
        progress.progress(min(p, 1.0), text=f"Scanning… {int(p*100)}%")

    def _tick(name, n):
        if n > 0:
            status.success(f"🎯  **{name}** — {n} signal(s)")
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
        f"across {len(batch_data)} tickers in {out['scan_time_s']}s."
    )


# ─────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────
out = st.session_state.scan_out

if out is None:
    st.info("👈  Configure the scan above, then click **▶ RUN SCAN**. Results will appear here.")
    st.stop()

df   = out["results_df"]
diag = out["diag"]
meta = st.session_state.get("scan_meta", {})

k1, k2, k3, k4 = st.columns(4)
k1.metric("Tickers Scanned", meta.get("tickers_scanned", out.get("tickers_processed", 0)))
k2.metric("Final Signals", len(df),
          delta=f"{df['ticker'].nunique()} unique" if len(df) else "none")
k3.metric("Scan Time", f"{out['scan_time_s']}s")
k4.metric("Timeframes", " · ".join(meta.get("timeframes", [])))

tab_sig, tab_chart, tab_diag, tab_err, tab_about = st.tabs(
    ["🎯 Signals", "📈 Chart", "🔬 Diagnostics", "⚠ Errors", "ℹ About"]
)

with tab_sig:
    if df.empty:
        st.info(f"No signals found in the last {meta.get('days_back', 10)} days.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            tf_f = st.multiselect("Timeframe",
                sorted(df["timeframe"].unique().tolist()),
                default=sorted(df["timeframe"].unique().tolist()))
        with f2:
            tk_f = st.multiselect("Ticker",
                sorted(df["ticker"].unique().tolist()),
                default=[], placeholder="All tickers")
        with f3:
            min_di = st.slider("Max DI diff",
                float(df["raw_di_diff"].min()), 0.0,
                float(df["raw_di_diff"].min()))

        filt = df[df["timeframe"].isin(tf_f) & (df["raw_di_diff"] <= min_di)]
        if tk_f:
            filt = filt[filt["ticker"].isin(tk_f)]
        filt = filt.sort_values(["datetime", "ticker"], ascending=[False, True])

        disp = filt.copy()
        disp["datetime"] = disp["datetime"].dt.strftime("%Y-%m-%d %H:%M")
        for c in ["close", "distance_pct", "raw_di_diff"]:
            disp[c] = disp[c].round(2)

        st.dataframe(disp, use_container_width=True, hide_index=True,
            column_config={
                "datetime": st.column_config.TextColumn("Time (IST)", width="medium"),
                "ticker": st.column_config.TextColumn("Ticker", width="small"),
                "timeframe": st.column_config.TextColumn("TF", width="small"),
                "close": st.column_config.NumberColumn("Close", format="₹%.2f"),
                "distance_pct": st.column_config.NumberColumn("% EMA", format="%.2f%%"),
                "raw_di_diff": st.column_config.NumberColumn("DI Diff", format="%.2f"),
            })

with tab_chart:
    if df.empty:
        st.info("No signals to chart.")
    else:
        labels = df.apply(lambda r: f"{r['ticker']} · {r['timeframe']} · "
                                     f"{r['datetime']:%d %b %H:%M}", axis=1).tolist()
        pick = st.selectbox("Pick a signal", labels)
        idx = labels.index(pick)
        row = df.iloc[idx]
        st.caption(f"**{row['ticker']}** · **{row['timeframe']}** · "
                   f"₹{row['close']:.2f} · %EMA {row['distance_pct']:.2f}% · "
                   f"DI diff {row['raw_di_diff']:.2f}")
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
                win = rs.loc[(rs.index >= row["datetime"] - pd.Timedelta(days=3)) &
                             (rs.index <= row["datetime"] + pd.Timedelta(days=1))]
                if not win.empty:
                    st.line_chart(win["close"], height=340, use_container_width=True)
                else:
                    st.warning("No bars around this signal.")
        except Exception as e:
            st.error(f"Chart error: {e}")

with tab_diag:
    st.markdown("### Stage Diagnostics · bar-events across all tickers")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Option-Bottom", diag["option_bottom"])
    d2.metric("DI < −10",     diag["di_negative"])
    d3.metric("Final",        diag["final"])
    d4.metric("Empty Data",   diag["empty_data"])
    st.caption(f"Cutoff: {out['cutoff']} · Duration: {out['scan_time_s']}s")

with tab_err:
    if not out["errors"]:
        st.success("No errors — all tickers processed cleanly.")
    else:
        st.warning(f"{len(out['errors'])} ticker(s) failed.")
        st.dataframe(pd.DataFrame(out["errors"], columns=["Ticker", "Error"]),
                     use_container_width=True, hide_index=True)

with tab_about:
    st.markdown("""
### ◈ Oversold Core Scanner

**Two conditions, both required on the same bar:**

**Condition 1 — Option-Strike Bottom**
- Close ≤ −2.5σ below 20-EMA exhaustion band
- Distance-% turned up (bottoming)
- Volume ≥ 2× its 20-bar moving average

**Condition 2 — Bearish DI Dominance**
- `+DI − −DI < −10` on a 100-bar RMA

**Timeframes:** 5m · 10m · 15m (resampled from 5m bars, live candle dropped).

**Data:** Yahoo Finance, 15-day lookback of 5-minute bars. Batch-fetched in one call, cached 10 min.

*Educational use only. Not investment advice.*
    """)