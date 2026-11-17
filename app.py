"""
Oversold Core Scanner — 2-condition engine.
Pure Python. No Streamlit dependencies so it can be unit-tested
or run as a CLI with `python scanner.py`.
"""
import numpy as np
import pandas as pd
import yfinance as yf
import warnings
from datetime import datetime, timedelta
import pytz

warnings.filterwarnings("ignore")

# ==========================================
# WATCHLISTS
# ==========================================
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
    "WIPRO.NS", "YESBANK.NS", "ZEEL.NS", "ZOMATO.NS", "ZYDUSLIFE.NS",
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
    "COFORGE.NS", "EXIDEIND.NS", "FORTIS.NS", "GLENMARK.NS", "BIOCON.NS",
]

ALL_TICKERS = list(dict.fromkeys(
    [t.replace(".NS", "") for t in (NSE_FO_TICKERS + HIGH_BETA_TICKERS)]
))

TIMEFRAME_MAP = {
    "15m": "15min",
    "30m": "30min",
    "45m": "45min",
    "60m": "60min",
}


# ==========================================
# INDICATOR HELPERS (Pine-faithful)
# ==========================================
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


# ==========================================
# CORE SCANNER
# ==========================================
def scan_combined_oversold_stocks(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(c).lower() for c in df.columns]
    results = df.copy()

    # CONDITION 1: Option-strike bottom
    results["ema_value"] = ta_ema(results["close"], 20)
    results["distance_pct"] = ((results["close"] - results["ema_value"]) /
                               results["ema_value"]) * 100
    results["dist_stdev"] = ta_stdev_pop(results["distance_pct"], 100)
    results["exhaustion_band"] = -(results["dist_stdev"] * 2.5)

    results["vol_ma"] = ta_sma(results["volume"], 20)
    results["is_vol_surge"] = results["volume"] > (results["vol_ma"] * 2.0)

    dp = results["distance_pct"]
    results["is_turning_up"] = (dp > dp.shift(1)) & (dp.shift(1) < dp.shift(2))
    results["is_deep_exhaust"] = results["distance_pct"] <= results["exhaustion_band"]

    results["option_bottom_confirmed"] = (
        results["is_deep_exhaust"]
        & results["is_turning_up"]
        & results["is_vol_surge"]
    )

    # CONDITION 2: Raw DI difference < -10
    di_len = 100
    high, low, close = results["high"], results["low"], results["close"]

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    tr = pd.concat(
        [high - low,
         (high - close.shift(1)).abs(),
         (low - close.shift(1)).abs()],
        axis=1
    ).max(axis=1)

    tr_rma = ta_rma(tr, di_len)
    plus_dm_rma = ta_rma(pd.Series(plus_dm, index=results.index), di_len)
    minus_dm_rma = ta_rma(pd.Series(minus_dm, index=results.index), di_len)

    plus_di = np.where(tr_rma != 0, 100 * plus_dm_rma / tr_rma, 0.0)
    minus_di = np.where(tr_rma != 0, 100 * minus_dm_rma / tr_rma, 0.0)
    results["raw_di_diff"] = plus_di - minus_di

    # FINAL
    results["signal_final"] = (
        results["option_bottom_confirmed"] & (results["raw_di_diff"] < -10)
    )
    return results


# ==========================================
# DEFAULT DATA FETCHER
# ==========================================
def default_fetch(ticker: str, period: str, interval: str) -> pd.DataFrame:
    return yf.download(
        ticker + ".NS", period=period, interval=interval,
        progress=False, auto_adjust=True, threads=False,
    )


# ==========================================
# SCAN ORCHESTRATOR
# ==========================================
def run_scan(
    tickers,
    timeframes,
    days_back=10,
    data_fetcher=None,
    progress_cb=None,
    ticker_cb=None,
):
    """
    Returns dict:
      results_df  – all signals (DataFrame)
      diag        – aggregate diagnostic dict
      errors      – list of (ticker, msg)
      scan_time_s – wall-clock seconds
    """
    import time
    if data_fetcher is None:
        data_fetcher = default_fetch

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

    t0 = time.time()

    for i, ticker in enumerate(tickers, 1):
        try:
            raw = data_fetcher(ticker, "60d", "15m")
            if raw is None or raw.empty:
                diag_total["empty_data"] += 1
                if ticker_cb:
                    ticker_cb(ticker, 0)
                if progress_cb:
                    progress_cb(i / len(tickers))
                continue

            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            raw.columns = [str(c).lower() for c in raw.columns]

            if not isinstance(raw.index, pd.DatetimeIndex):
                raw.index = pd.to_datetime(raw.index)

            if raw.index.tz is None:
                raw.index = raw.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
            else:
                raw.index = raw.index.tz_convert("Asia/Kolkata")

            raw = raw[raw["volume"] > 0]
            if len(raw) < 100:
                if ticker_cb:
                    ticker_cb(ticker, 0)
                if progress_cb:
                    progress_cb(i / len(tickers))
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
                    cols_out = [
                        "datetime", "ticker", "timeframe", "close",
                        "distance_pct", "raw_di_diff",
                    ]
                    all_results.append(sigs[cols_out])
                    ticker_signals += len(sigs)

            if ticker_cb:
                ticker_cb(ticker, ticker_signals)

        except Exception as e:
            errors.append((ticker, str(e)))

        if progress_cb:
            progress_cb(i / len(tickers))

    elapsed = time.time() - t0

    if all_results:
        df = pd.concat(all_results, ignore_index=True)
        df = df[df["datetime"].dt.date >= cutoff]
    else:
        df = pd.DataFrame(
            columns=["datetime", "ticker", "timeframe", "close",
                     "distance_pct", "raw_di_diff"]
        )

    return {
        "results_df": df,
        "diag": diag_total,
        "errors": errors,
        "scan_time_s": round(elapsed, 1),
        "cutoff": cutoff,
    }


# ==========================================
# CLI MODE
# ==========================================
if __name__ == "__main__":
    out = run_scan(ALL_TICKERS, ["15m", "30m", "45m", "60m"], days_back=10)
    print("Diagnostics:", out["diag"])
    print(f"Signals: {len(out['results_df'])} in {out['scan_time_s']}s")
    if not out["results_df"].empty:
        print(out["results_df"].to_string(index=False))