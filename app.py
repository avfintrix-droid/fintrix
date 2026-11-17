import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import scanner

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
# GLOBAL CSS — professional dark trading theme
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 0%, #0f1a2e 0%, #0a0e1a 40%, #060910 100%); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px; }

/* Landing */
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

/* Main hero */
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

/* Control panel card */
.control-card { background: linear-gradient(135deg, #131824 0%, #182135 100%);
    border: 1px solid #1e2a3f; border-radius: 16px;
    padding: 24px 28px; margin-bottom: 20px;
    box-shadow: 0 6px 32px rgba(0,0,0,0.35); }
.control-title { color: #00d4ff; font-size: 0.78rem; letter-spacing: 0.15em;
    font-weight: 800; text-transform: uppercase; margin-bottom: 16px; }

/* Metrics */
[data-testid="stMetric"] { background: linear-gradient(135deg, #131824, #182135);
    border: 1px solid #1e2a3f; border-radius: 14px;
    padding: 18px 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.35); }
[data-testid="stMetricLabel"] { color: #6b7a90 !important; font-size: 0.75rem !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
    font-weight: 700 !important; }
[data-testid="stMetricValue"] { color: #e0e6ed !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important; font-size: 1.9rem !important; }

/* Primary button (RUN SCAN) */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #00d4ff 0%, #00a3cc 100%);
    color: #0a0e1a !important; border: none; font-weight: 800;
    letter-spacing: 0.08em; padding: 0.9rem 2rem; border-radius: 12px;
    font-size: 1rem; box-shadow: 0 6px 24px rgba(0, 212, 255, 0.35);
    transition: all 0.2s ease; text-transform: uppercase; }
.stButton > button[kind="primary"]:hover { transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.55); }

/* Secondary buttons */
.stButton > button { border-radius: 10px; font-weight: 600; }

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(90deg, #00e676 0%, #00b862 100%);
    color: #0a0e1a !important; font-weight: 700;
    border-radius: 10px; border: none; padding: 0.6rem 1.4rem; }

/* Sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0c1220 0%, #080c15 100%);
    border-right: 1px solid #1a2130; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #00d4ff !important; letter-spacing: 0.05em;
    font-size: 0.82rem !important; text-transform: uppercase;
    font-weight: 800; margin-top: 1rem; }

/* Tabs */
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


# ─────────────────────────────────────────────────────────
# LANDING SCREEN (first visit)
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
# CONTROL PANEL — prominent scan button on dashboard
# ─────────────────────────────────────────────────────────
st.markdown('<div class="control-card">', unsafe_allow_html=True)
st.markdown('<div class="control-title">⚙ SCAN CONTROL PANEL</div>', unsafe_allow_html=True)

# Row 1: Universe + Max tickers
rc1, rc2 = st.columns([2, 1])
with rc1:
    universe = st.radio(
        "Universe",
        ["NSE F&O (~190)", "High Beta (~60)", "Combined (~250)"],
        index=2, horizontal=True,
        help="Which watchlist to scan.",
    )
    if universe.startswith("NSE"):
        base = [t.replace(".NS", "") for t in scanner.NSE_FO_TICKERS]
    elif universe.startswith("High"):
        base = [t.replace(".NS", "") for t in scanner.HIGH_BETA_TICKERS]
    else:
        base = scanner.ALL_TICKERS
with rc2:
    max_tickers = st.slider(
        "Max tickers",
        min_value=10, max_value=len(base),
        value=min(50, len(base)), step=10,
        help="Streamlit Cloud times out at 5 min. 50 is safe with batch fetch.",
    )
tickers = base[:max_tickers]

# Row 2: Timeframes + Lookback
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

# Row 3: THE SCAN BUTTONS
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
                "⬇  CSV",
                data=to_csv_bytes(df_now),
                file_name=f"signals_{datetime.now():%Y%m%d_%H%M}.csv",
                mime="text/csv",
                use_container_width=True,
            )

st.markdown('</div>', unsafe_allow_html=True)

# Handle buttons
if clear_btn:
    st.session_state.scan_out = None
    st.rerun()

if refresh_btn:
    st.cache_data.clear()
    st.session_state.scan_out = None
    st.success("Cache cleared. Next scan will fetch fresh data.")

if not selected_tfs and run_btn:
    st.error("Select at least one timeframe.")
    st.stop()


# ─────────────────────────────────────────────────────────
# CACHED FETCH
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def cached_batch(tickers_tuple):
    return scanner.batch_fetch(list(tickers_tuple), period="15d", interval="5m")


# ─────────────────────────────────────────────────────────
# RUN SCAN
# ─────────────────────────────────────────────────────────
if "scan_out" not in st.session_state:
    st.session_state.scan_out = None

if run_btn:
    if not tickers:
        st.error("No tickers selected.")
        st.stop()

    # Stage 1: fetch
    fetch_slot = st.empty()
    fetch_slot.info(f"📡 Fetching {len(tickers)} tickers from Yahoo Finance…")
    batch_data, fetch_err = cached_batch(tuple(tickers))

    if fetch_err:
        fetch_slot.empty()
        st.error(f"Fetch failed: {fetch_err}")
        st.stop()

    if not batch_data:
        fetch_slot.empty()
        st.error("No data returned. Try clicking **Refresh Data** and scanning again.")
        st.stop()

    fetch_slot.success(f"✅  Fetched {len(batch_data)}/{len(tickers)} tickers. Processing…")

    # Stage 2: process
    progress = st.progress(0.0, text="Processing indicators…")
    status = st.empty()

    def _prog(p):
        progress.progress(min(p, 1.0), text=f"Scanning… {int(p*100)}%")

    def _tick(name, n):
        if n > 0:
            status.success(f"🎯  **{name}** — {n} signal(s)")
        else:
            status.info(f"🔍  {name}")

    out = scanner.process_batch(
        batch_data, selected_tfs,
        days_back=days_back,
        progress_cb=_prog, ticker_cb=_tick,
    )
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
    st.info(
        "👈  Configure the scan above, then click **▶ RUN SCAN**. "
        "Results will appear here."
    )
    st.stop()

df   = out["results_df"]
diag = out["diag"]
meta = st.session_state.get("scan_meta", {})

# KPI strip
k1, k2, k3, k4 = st.columns(4)
k1.metric("Tickers Scanned", meta.get("tickers_scanned", out.get("tickers_processed", 0)))
k2.metric("Final Signals", len(df),
          delta=f"{df['ticker'].nunique()} unique" if len(df) else "none")
k3.metric("Scan Time", f"{out['scan_time_s']}s")
k4.metric("Timeframes", " · ".join(meta.get("timeframes", [])))

# Tabs
tab_sig, tab_chart, tab_diag, tab_err, tab_about = st.tabs(
    ["🎯 Signals", "📈 Chart", "🔬 Diagnostics", "⚠ Errors", "ℹ About"]
)

# ── Tab 1: Signals
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

# ── Tab 2: Chart
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
                rs = raw.resample(scanner.TIMEFRAME_MAP[row["timeframe"]],
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

# ── Tab 3: Diagnostics
with tab_diag:
    st.markdown("### Stage Diagnostics · bar-events across all tickers")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Option-Bottom", diag["option_bottom"])
    d2.metric("DI < −10",     diag["di_negative"])
    d3.metric("Final",        diag["final"])
    d4.metric("Empty Data",   diag["empty_data"])
    st.caption(f"Cutoff: {out['cutoff']} · Duration: {out['scan_time_s']}s")

# ── Tab 4: Errors
with tab_err:
    if not out["errors"]:
        st.success("No errors — all tickers processed cleanly.")
    else:
        st.warning(f"{len(out['errors'])} ticker(s) failed.")
        st.dataframe(pd.DataFrame(out["errors"], columns=["Ticker", "Error"]),
                     use_container_width=True, hide_index=True)

# ── Tab 5: About
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