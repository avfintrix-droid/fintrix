# ================================
# DEX, VANNA & CHARM ANALYZER (NUBRA) — FINTRIX TERMINAL v3
# ================================
import sys
import dbm.dumb
if 'dbm.gnu' not in sys.modules:
    sys.modules['dbm.gnu'] = dbm.dumb

import streamlit as st
import pandas as pd
import numpy as np
from nubra_python_sdk.marketdata.market_data import MarketData
from nubra_python_sdk.start_sdk import InitNubraSdk, NubraEnv
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import math
import scipy.stats as stats
import plotly.graph_objects as go
import pyotp
import builtins
import getpass
import os

# ──────────────────────────────────────────
# NUBRA AUTHENTICATION (automated TOTP)
# ──────────────────────────────────────────
if 'nubra_client' not in st.session_state or st.session_state.nubra_client is None:
    with st.spinner("Authenticating with Nubra..."):
        # IMPORTANT: Replace with your actual TOTP secret (from nubra.totp_generate_secret())
        TOTP_SECRET = os.environ.get("NUBRA_TOTP_SECRET", "YOUR_TOTP_SECRET_HERE")
        totp = pyotp.TOTP(TOTP_SECRET)
        
        # Patch input() and getpass() to return the current TOTP when Nubra asks
        orig_input = builtins.input
        orig_getpass = getpass.getpass
        
        def auto_totp_input(prompt=""):
            return totp.now()
        
        def auto_totp_getpass(prompt=""):
            return totp.now()
        
        builtins.input = auto_totp_input
        getpass.getpass = auto_totp_getpass
        
        try:
            nubra_client = InitNubraSdk(
                env=NubraEnv.PROD,
                totp_login=True,   # enables TOTP flow
                env_creds=True      # reads PHONE_NO and MPIN from .env
            )
            st.session_state.nubra_client = nubra_client
            st.success("✅ Nubra Authentication Successful!")
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            st.stop()
        finally:
            # Restore original functions
            builtins.input = orig_input
            getpass.getpass = orig_getpass

# ──────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────
st.set_page_config(
    page_title="Fintrix | DEX · VANNA · CHARM",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────
# GLOBAL CSS (modified: PE now green)
# ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: #0a0c0f !important;
    color: #c9d1d9 !important;
}
.stApp { background: #0a0c0f !important; }

section[data-testid="stSidebar"] {
    background: #0f1117 !important;
    border-right: 1px solid #21262d !important;
}
section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextInput > div > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 4px !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #21262d !important;
    color: #f0a500 !important;
    border: 1px solid #f0a500 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    border-radius: 3px !important;
    width: 100% !important;
    margin-top: 6px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #f0a500 !important;
    color: #0a0c0f !important;
}

.fintrix-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    padding: 18px 0 8px 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 18px;
}
.fintrix-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: #f0a500;
    letter-spacing: 0.12em;
}
.fintrix-sub {
    font-size: 0.75rem;
    color: #484f58;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.06em;
}
.pulse {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 6px;
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

.cards-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}
.card {
    background: #0f1117;
    border: 1px solid #21262d;
    border-radius: 5px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.card.bear::before { background: #ef4444; }
.card.bull::before { background: #22c55e; }
.card-label {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #484f58;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 6px;
}
.card-val {
    font-size: 1.45rem;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.1;
}
.card-val.red { color: #ef4444; }
.card-val.green { color: #22c55e; }
.card-sub { font-size: 0.65rem; color: #484f58; font-family: 'IBM Plex Mono', monospace; margin-top: 4px; }
.card-badge {
    display: inline-block;
    font-size: 0.6rem;
    letter-spacing: 0.06em;
    padding: 2px 7px;
    border-radius: 2px;
    margin-top: 6px;
    font-family: 'IBM Plex Mono', monospace;
}
.badge-red { background: rgba(239,68,68,0.12); color: #f87171; }
.badge-green { background: rgba(34,197,94,0.12); color: #4ade80; }

.section-head {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #484f58;
    padding: 10px 0 6px 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 14px;
}

.decay-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0 10px 0;
    border-bottom: 2px solid #22c55e;
    margin-bottom: 16px;
}
.decay-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: #22c55e;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.decay-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 14px;
    background: #0f1117;
    border: 1px solid #21262d;
    border-radius: 5px;
    margin-bottom: 8px;
}
.decay-rank {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    color: #f0a500;
    background: #21262d;
    border-radius: 12px;
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.decay-strike {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #e6edf3;
    min-width: 110px;
    line-height: 1;
}
.decay-type-ce {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    padding: 3px 10px;
    border-radius: 3px;
    background: rgba(249,115,22,0.15);
    color: #f97316;
    border: 1px solid rgba(249,115,22,0.3);
    min-width: 40px;
    text-align: center;
}
.decay-type-pe {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    padding: 3px 10px;
    border-radius: 3px;
    background: rgba(34,197,94,0.15);
    color: #22c55e;
    border: 1px solid rgba(34,197,94,0.3);
    min-width: 40px;
    text-align: center;
}
.decay-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    color: #22c55e;
    min-width: 90px;
}
.decay-bar-wrap {
    flex: 1;
    height: 8px;
    background: #21262d;
    border-radius: 3px;
    overflow: hidden;
}
.decay-bar-ce {
    height: 100%;
    background: #f97316;
    border-radius: 3px;
}
.decay-bar-pe {
    height: 100%;
    background: #22c55e;
    border-radius: 3px;
}
.decay-charm-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #484f58;
    text-align: right;
    min-width: 60px;
}

.chart-label-row {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 4px;
}
.legend-dot {
    width: 10px; height: 10px;
    border-radius: 2px;
    display: inline-block;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #21262d !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #484f58 !important;
    background: transparent !important;
    border: none !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #f0a500 !important;
    border-bottom: 2px solid #f0a500 !important;
}

.stDataFrame { border: 1px solid #21262d !important; border-radius: 4px !important; }

[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.15rem !important;
    color: #e6edf3 !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.6rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #484f58 !important;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.extreme-card {
    background: #0f1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.extreme-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: #8b949e;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.extreme-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #e6edf3;
    line-height: 1.2;
}
.extreme-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #484f58;
    margin-top: 6px;
}
.extreme-badge {
    display: inline-block;
    background: #21262d;
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 0.65rem;
    font-family: 'IBM Plex Mono', monospace;
    color: #f0a500;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 1. INITIALIZE NUBRA (use authenticated client)
# ──────────────────────────────────────────
md = MarketData(st.session_state.nubra_client)

# ──────────────────────────────────────────
# 2. BLACK-SCHOLES HELPERS
# ──────────────────────────────────────────
def bs_d1_d2(S, K, T, r, sigma, q=0.0):
    if T <= 0: return 0.0, 0.0
    ss = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / ss
    return d1, d1 - ss

def compute_vanna(S, K, T, r, sigma, vega):
    if sigma <= 0 or T <= 0: return 0.0
    _, d2 = bs_d1_d2(S, K, T, r, sigma)
    return -vega * d2 / sigma

def compute_charm(S, K, T, r, sigma, q=0.0, option_type='call'):
    if T <= 1e-6 or sigma <= 0: return 0.0
    d1, d2 = bs_d1_d2(S, K, T, r, sigma, q)
    phi = stats.norm.pdf(d1)
    term = (r - q) / (sigma * math.sqrt(T)) - d2 / (2.0 * T)
    eq = math.exp(-q * T)
    base = -eq * phi * term
    return base - q * eq * stats.norm.cdf(d1) if option_type == 'call' else base + q * eq * stats.norm.cdf(-d1)

# ──────────────────────────────────────────
# 3. FETCH CHAIN
# ──────────────────────────────────────────
def fetch_chain(underlying, expiry_str):
    exchange = "BSE" if underlying == "SENSEX" else "NSE"
    try:
        result = md.option_chain(underlying, expiry_str, exchange)
        chain = result.chain
        spot = chain.current_price / 100 if chain.current_price else None
        strikes = sorted(set(
            [o.strike_price / 100 for o in chain.ce] +
            [o.strike_price / 100 for o in chain.pe]
        ))
        data = []
        for s in strikes:
            ce = next((o for o in chain.ce if o.strike_price / 100 == s), None)
            pe = next((o for o in chain.pe if o.strike_price / 100 == s), None)

            def get_price(opt):
                if opt is None:
                    return np.nan
                for attr in ['ltp', 'last_price', 'last_traded_price', 'close']:
                    if hasattr(opt, attr):
                        val = getattr(opt, attr)
                        if val is not None and not np.isnan(val):
                            return val
                return np.nan

            data.append({
                'strike': s,
                'call_gamma': ce.gamma if ce else np.nan,
                'call_oi': ce.open_interest if ce else 0,
                'call_vega': ce.vega if ce else np.nan,
                'call_iv': ce.iv if ce else np.nan,
                'put_gamma': pe.gamma if pe else np.nan,
                'put_oi': pe.open_interest if pe else 0,
                'put_vega': pe.vega if pe else np.nan,
                'put_iv': pe.iv if pe else np.nan,
            })
        return pd.DataFrame(data).set_index('strike'), spot
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return None, None

# ──────────────────────────────────────────
# 4. CALCULATE GREEKS
# ──────────────────────────────────────────
def calculate_greeks(df, spot, T_years, r=0.05):
    if df.empty or spot is None: return pd.DataFrame()
    res = df.copy()
    cv, pv, cc, pc = [], [], [], []
    for K, row in df.iterrows():
        try:
            ic, vc = float(row['call_iv']), float(row['call_vega'])
            if ic > 0 and vc == vc:
                cv.append(compute_vanna(spot, K, T_years, r, ic, vc))
                cc.append(compute_charm(spot, K, T_years, r, ic, option_type='call'))
            else:
                cv.append(0.0); cc.append(0.0)
        except (TypeError, ValueError):
            cv.append(0.0); cc.append(0.0)
        try:
            ip, vp = float(row['put_iv']), float(row['put_vega'])
            if ip > 0 and vp == vp:
                pv.append(compute_vanna(spot, K, T_years, r, ip, vp))
                pc.append(compute_charm(spot, K, T_years, r, ip, option_type='put'))
            else:
                pv.append(0.0); pc.append(0.0)
        except (TypeError, ValueError):
            pv.append(0.0); pc.append(0.0)

    res['call_vanna'] = cv; res['put_vanna'] = pv
    res['call_charm'] = cc; res['put_charm'] = pc

    res['dex']   = (res['call_gamma'] * res['call_oi'] - res['put_gamma'] * res['put_oi']) * spot / 1_000_000
    res['vanna'] = (res['call_vanna'] * res['call_oi'] - res['put_vanna'] * res['put_oi']) * spot / 1_000_000
    res['charm'] = (res['call_charm'] * res['call_oi'] - res['put_charm'] * res['put_oi']) * spot / 1_000_000

    res['charm_ce'] = res['call_charm'] * res['call_oi'] * spot / 1_000_000
    res['charm_pe'] = res['put_charm']  * res['put_oi']  * spot / 1_000_000
    return res

def find_dex_cross(df):
    vals, strikes = df['dex'].values, df.index.values
    for i in range(1, len(vals)):
        if vals[i-1] < 0 and vals[i] > 0:
            return strikes[i-1] + (0 - vals[i-1]) / (vals[i] - vals[i-1]) * (strikes[i] - strikes[i-1])
    return None

def find_vanna_clusters(df):
    strikes, vanna = df.index.values, df['vanna'].values
    clusters_pos, clusters_neg, cur_p, cur_n = [], [], [], []
    for i, s in enumerate(strikes):
        v = vanna[i]
        if v > 0:
            if cur_n: clusters_neg.append(cur_n); cur_n = []
            cur_p.append((s, v))
        elif v < 0:
            if cur_p: clusters_pos.append(cur_p); cur_p = []
            cur_n.append((s, v))
        else:
            if cur_p: clusters_pos.append(cur_p); cur_p = []
            if cur_n: clusters_neg.append(cur_n); cur_n = []
    if cur_p: clusters_pos.append(cur_p)
    if cur_n: clusters_neg.append(cur_n)
    clusters_pos = [c for c in clusters_pos if len(c) >= 2]
    clusters_neg = [c for c in clusters_neg if len(c) >= 2]
    best_p = max(clusters_pos, key=lambda c: sum(abs(v) for _, v in c)) if clusters_pos else None
    best_n = max(clusters_neg, key=lambda c: sum(abs(v) for _, v in c)) if clusters_neg else None
    ceil  = (min(s for s,_ in best_p), max(s for s,_ in best_p)) if best_p else None
    floor = (min(s for s,_ in best_n), max(s for s,_ in best_n)) if best_n else None
    return ceil, floor

def get_dex_extremes(df):
    valid = df[(df['call_oi'] > 0) | (df['put_oi'] > 0)].copy()
    if valid.empty:
        return None, None, None, None
    if not valid['dex'].isna().all():
        pos_row = valid.loc[valid['dex'].idxmax()]
        pos_strike = pos_row.name if pos_row['dex'] > 0 else None
        pos_dex = pos_row['dex'] if pos_row['dex'] > 0 else None
    else:
        pos_strike = pos_dex = None
    if not valid['dex'].isna().all():
        neg_row = valid.loc[valid['dex'].idxmin()]
        neg_strike = neg_row.name if neg_row['dex'] < 0 else None
        neg_dex = neg_row['dex'] if neg_row['dex'] < 0 else None
    else:
        neg_strike = neg_dex = None
    return pos_strike, pos_dex, neg_strike, neg_dex

def get_charm_extremes(df, spot):
    below_pe = [(strike, row['charm_pe']) for strike, row in df.iterrows()
                if strike < spot and row['put_oi'] > 0 and row['charm_pe'] < 0]
    above_ce = [(strike, row['charm_ce']) for strike, row in df.iterrows()
                if strike > spot and row['call_oi'] > 0 and row['charm_ce'] < 0]
    best_below = min(below_pe, key=lambda x: x[1]) if below_pe else None
    best_above = min(above_ce, key=lambda x: x[1]) if above_ce else None
    b_strike, b_charm = best_below if best_below else (None, None)
    a_strike, a_charm = best_above if best_above else (None, None)
    return b_strike, b_charm, a_strike, a_charm

# ──────────────────────────────────────────
# 5. CHART FUNCTIONS
# ──────────────────────────────────────────
CHART_BG   = "#0a0c0f"
PAPER_BG   = "#0a0c0f"
GRID_COLOR = "#1c2128"
TEXT_COLOR = "#8b949e"
AMBER      = "#f0a500"
RED        = "#ef4444"
GREEN      = "#22c55e"
BLUE       = "#3b82f6"
ORANGE     = "#f97316"

def base_layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(family="IBM Plex Mono", size=10, color="#484f58"), x=0.01, y=0.99),
        plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG, height=height,
        margin=dict(l=54, r=14, t=28, b=72),
        font=dict(family="IBM Plex Mono", size=9, color=TEXT_COLOR),
        xaxis=dict(
            showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
            tickfont=dict(size=8, color=TEXT_COLOR), tickangle=-55,
        ),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=True,
                   zerolinecolor="#30363d", zerolinewidth=1,
                   tickfont=dict(size=8, color=TEXT_COLOR)),
        legend=dict(font=dict(size=8, color=TEXT_COLOR), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )

def make_dex_chart(df, spot, zero_cross, height=380, x_range=None):
    if x_range is not None and len(x_range) == 2:
        min_s, max_s = x_range
        df = df[(df.index >= min_s) & (df.index <= max_s)]
    if df.empty:
        return go.Figure()
    strikes  = df.index.tolist()
    dex_vals = df['dex'].tolist()
    colors   = [RED if v < 0 else GREEN for v in dex_vals]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=strikes, y=dex_vals, name="DEX",
        marker_color=colors, marker_line_width=0, opacity=0.85,
        hovertemplate="<b>%{x}</b>  DEX: %{y:.3f}<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color="#30363d", width=1))
    if spot and (x_range is None or (x_range[0] <= spot <= x_range[1])):
        fig.add_vline(x=spot, line=dict(color=AMBER, width=1.5, dash="dot"),
                      annotation_text=f"SPOT {spot:.0f}",
                      annotation_font=dict(color=AMBER, size=8))
    if zero_cross and (x_range is None or (x_range[0] <= zero_cross <= x_range[1])):
        fig.add_vline(x=zero_cross, line=dict(color=BLUE, width=1.5, dash="dash"),
                      annotation_text=f"Δ0 {zero_cross:.0f}",
                      annotation_font=dict(color=BLUE, size=8),
                      annotation_position="top right")
    layout = base_layout("DEX BY STRIKE", height=height)
    layout['xaxis']['tickmode']  = 'array'
    layout['xaxis']['tickvals']  = strikes
    layout['xaxis']['ticktext']  = [str(int(s)) for s in strikes]
    layout['bargap'] = 0.15
    fig.update_layout(**layout)
    return fig

def make_charm_chart(df, spot, height=380, x_range=None):
    if x_range is not None and len(x_range) == 2:
        min_s, max_s = x_range
        df = df[(df.index >= min_s) & (df.index <= max_s)]
    if df.empty:
        return go.Figure()
    strikes    = df.index.tolist()
    charm_vals = df['charm'].tolist()
    colors     = [RED if v < 0 else GREEN for v in charm_vals]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=strikes, y=charm_vals, name="Charm",
        marker_color=colors, marker_line_width=0, opacity=0.85,
        hovertemplate="<b>%{x}</b>  Charm: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color="#30363d", width=1))
    if spot and (x_range is None or (x_range[0] <= spot <= x_range[1])):
        fig.add_vline(x=spot, line=dict(color=AMBER, width=1.5, dash="dot"),
                      annotation_text=f"SPOT {spot:.0f}",
                      annotation_font=dict(color=AMBER, size=8))
    layout = base_layout("CHARM BY STRIKE", height=height)
    layout['xaxis']['tickmode']  = 'array'
    layout['xaxis']['tickvals']  = strikes
    layout['xaxis']['ticktext']  = [str(int(s)) for s in strikes]
    layout['bargap'] = 0.15
    fig.update_layout(**layout)
    return fig

def make_vanna_chart(df, spot, ceil, floor, height=360):
    strikes    = df.index.tolist()
    vanna_vals = df['vanna'].tolist()
    colors     = [BLUE if v >= 0 else "#a855f7" for v in vanna_vals]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=strikes, y=vanna_vals, name="Vanna",
        marker_color=colors, marker_line_width=0, opacity=0.85,
        hovertemplate="<b>%{x}</b>  Vanna: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color="#30363d", width=1))
    if spot:
        fig.add_vline(x=spot, line=dict(color=AMBER, width=1.5, dash="dot"),
                      annotation_text=f"SPOT {spot:.0f}",
                      annotation_font=dict(color=AMBER, size=8))
    if ceil:
        fig.add_vrect(x0=ceil[0], x1=ceil[1], fillcolor="rgba(59,130,246,0.07)",
                      line=dict(color=BLUE, width=1, dash="dot"),
                      annotation_text="Ceiling", annotation_font=dict(color=BLUE, size=8))
    if floor:
        fig.add_vrect(x0=floor[0], x1=floor[1], fillcolor="rgba(239,68,68,0.07)",
                      line=dict(color=RED, width=1, dash="dot"),
                      annotation_text="Floor", annotation_font=dict(color=RED, size=8))
    layout = base_layout("VANNA BY STRIKE", height=height)
    layout['xaxis']['tickmode']  = 'array'
    layout['xaxis']['tickvals']  = strikes
    layout['xaxis']['ticktext']  = [str(int(s)) for s in strikes]
    layout['bargap'] = 0.15
    fig.update_layout(**layout)
    return fig

def make_decay_bar_chart(decay_df, height=320):
    labels = [f"{int(r['strike'])}  {'CE' if r['type']=='CE' else 'PE'}" for _, r in decay_df.iterrows()]
    values = decay_df['charm_val'].tolist()
    colors = [ORANGE if r['type'] == 'CE' else GREEN for _, r in decay_df.iterrows()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        marker_line_width=0,
        opacity=0.9,
        text=[f"{v:.4f}" for v in values],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=9, color=TEXT_COLOR),
        hovertemplate="<b>%{x}</b><br>Charm: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color="#30363d", width=1))

    layout = dict(
        plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG, height=height,
        margin=dict(l=54, r=14, t=28, b=60),
        font=dict(family="IBM Plex Mono", size=9, color=TEXT_COLOR),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=9, color="#c9d1d9"), tickangle=0),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=True,
                   zerolinecolor="#30363d", zerolinewidth=1,
                   tickfont=dict(size=8, color=TEXT_COLOR)),
        bargap=0.25,
        showlegend=False,
        annotations=[
            dict(
                x=0.5, y=1.04, xref="paper", yref="paper",
                text="HIGHEST DECAY PRESSURE  ·  CE = orange  ·  PE = green",
                showarrow=False,
                font=dict(family="IBM Plex Mono", size=9, color="#484f58"),
                xanchor="center",
            )
        ]
    )
    fig.update_layout(**layout)
    return fig

def build_decay_table(gk_df, top_n=8):
    rows = []
    for strike, row in gk_df.iterrows():
        if row['call_oi'] > 0:
            rows.append({'strike': strike, 'type': 'CE', 'charm_val': row['charm_ce'], 'oi': row['call_oi']})
        if row['put_oi'] > 0:
            rows.append({'strike': strike, 'type': 'PE', 'charm_val': row['charm_pe'], 'oi': row['put_oi']})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df[df['charm_val'] < 0].sort_values('charm_val').head(top_n).reset_index(drop=True)
    return df

# ──────────────────────────────────────────
# 6. SIDEBAR AND SESSION STATE
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:IBM Plex Mono;font-size:0.8rem;color:#f0a500;letter-spacing:0.1em;
    padding-bottom:12px;border-bottom:1px solid #21262d;margin-bottom:14px;'>
    ⬡ FINTRIX TERMINAL
    </div>""", unsafe_allow_html=True)

    st.session_state.underlying = st.selectbox(
        "UNDERLYING", ["NIFTY", "SENSEX"],
        index=0 if st.session_state.get("underlying", "NIFTY") == "NIFTY" else 1,
        key="sidebar_underlying"
    )
    st.session_state.expiry_input = st.text_input(
        "EXPIRY (YYYYMMDD)",
        value=st.session_state.get("expiry_input", "20260609"),
        key="sidebar_expiry"
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    interval_map   = {"30 sec": 30, "1 min": 60, "2 min": 120, "3 min": 180, "5 min": 300}
    selected_label = st.selectbox("AUTO-REFRESH", list(interval_map.keys()), index=1)
    refresh_seconds = interval_map[selected_label]
    auto_refresh   = st.checkbox("ENABLE AUTO-REFRESH", value=True)
    manual_refresh = st.button("⟳  REFRESH NOW")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:IBM Plex Mono;font-size:0.6rem;color:#30363d;line-height:1.8;'>
    RISK-FREE RATE · 5%<br>SOURCE · NUBRA PROD<br>GREEKS · BLACK-SCHOLES
    </div>""", unsafe_allow_html=True)

if auto_refresh:
    st_autorefresh(interval=refresh_seconds * 1000, key="fintrix_refresh")

if "underlying" not in st.session_state:
    st.session_state.underlying = "NIFTY"
if "expiry_input" not in st.session_state:
    st.session_state.expiry_input = "20260609"

_SS_DEFAULTS = {
    'gk_df': None, 'spot': None, 'zero_cross': None,
    'ceil_zone': None, 'floor_zone': None,
    'last_fetch': None, 'last_update': datetime.now(),
}
for _k, _v in _SS_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ──────────────────────────────────────────
# 7. HEADER
# ──────────────────────────────────────────
st.markdown(f"""
<div class="fintrix-header">
  <span class="fintrix-logo">FINTRIX | DEX · VANNA · CHARM</span>
  <span class="fintrix-sub">
    <span class="pulse"></span>
    {st.session_state.underlying} &nbsp;·&nbsp; EXPIRY {st.session_state.expiry_input} &nbsp;·&nbsp; REFRESH {selected_label}
  </span>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 8. DASHBOARD MANUAL CONTROLS
# ──────────────────────────────────────────
col_manual1, col_manual2, col_manual3 = st.columns([2,2,1])
with col_manual1:
    new_underlying = st.selectbox(
        "📊 UNDERLYING",
        ["NIFTY", "SENSEX"],
        index=0 if st.session_state.underlying == "NIFTY" else 1,
        key="dashboard_underlying"
    )
with col_manual2:
    new_expiry = st.text_input(
        "📅 EXPIRY (YYYYMMDD)",
        value=st.session_state.expiry_input,
        key="dashboard_expiry"
    )
with col_manual3:
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    force_refresh = st.button("🔄 REFRESH DATA", use_container_width=True)

if new_underlying != st.session_state.underlying:
    st.session_state.underlying = new_underlying
    force_refresh = True
if new_expiry != st.session_state.expiry_input:
    st.session_state.expiry_input = new_expiry
    force_refresh = True

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 9. FETCH LOGIC
# ──────────────────────────────────────────
def should_refresh():
    if manual_refresh or force_refresh: return True
    if st.session_state.get("gk_df") is None: return True
    if auto_refresh:
        last = st.session_state.get("last_fetch")
        return last is None or (datetime.now() - last).total_seconds() >= refresh_seconds
    return False

if should_refresh():
    with st.spinner(f"FETCHING {st.session_state.underlying} CHAIN ..."):
        chain_df, spot = fetch_chain(st.session_state.underlying, st.session_state.expiry_input)
        if chain_df is not None and spot is not None:
            expiry_date = datetime.strptime(st.session_state.expiry_input, "%Y%m%d").date()
            days = max(0.1, (expiry_date - datetime.now().date()).days)
            T    = days / 365.0
            gk_df = calculate_greeks(chain_df, spot, T)
            st.session_state.update({
                'gk_df':       gk_df,
                'spot':        spot,
                'zero_cross':  find_dex_cross(gk_df),
                'ceil_zone':   find_vanna_clusters(gk_df)[0],
                'floor_zone':  find_vanna_clusters(gk_df)[1],
                'last_fetch':  datetime.now(),
                'last_update': datetime.now(),
                'T_years':     T,
            })
        else:
            st.warning("No data. Keeping prior snapshot.")

if st.session_state.gk_df is None:
    st.info("↑ Click REFRESH NOW or enable auto-refresh to load data.")
    st.stop()

gk_df      = st.session_state.gk_df
spot       = st.session_state.spot
zero_cross = st.session_state.zero_cross
ceil_zone  = st.session_state.ceil_zone
floor_zone = st.session_state.floor_zone
last_upd   = st.session_state.last_update
T_years    = st.session_state.get('T_years', 0.05)
decay_df   = build_decay_table(gk_df, top_n=8)

net_dex   = gk_df['dex'].sum()
net_vanna = gk_df['vanna'].sum()
net_charm = gk_df['charm'].sum()

# ──────────────────────────────────────────
# 10. TOP METRIC CARDS
# ──────────────────────────────────────────
def card_cls(v): return "bear" if v < 0 else "bull"
def val_cls(v):  return "red"  if v < 0 else "green"

st.markdown(f"""
<div class="cards-row">
  <div class="card {card_cls(net_dex)}">
    <div class="card-label">Net GEX</div>
    <div class="card-val {val_cls(net_dex)}">{net_dex:+.2f}</div>
    <div class="card-sub">Gamma Exposure</div>
    <span class="card-badge {'badge-red' if net_dex<0 else 'badge-green'}">{'SHORT GAMMA' if net_dex<0 else 'LONG GAMMA'}</span>
  </div>
  <div class="card {card_cls(net_dex)}">
    <div class="card-label">Net DEX</div>
    <div class="card-val {val_cls(net_dex)}">{net_dex:+.2f}</div>
    <div class="card-sub">Dealer Delta Exposure</div>
    <span class="card-badge {'badge-red' if net_dex<0 else 'badge-green'}">{'NET SHORT δ' if net_dex<0 else 'NET LONG δ'}</span>
  </div>
  <div class="card {card_cls(net_vanna)}">
    <div class="card-label">Net Vanna</div>
    <div class="card-val {val_cls(net_vanna)}">{net_vanna:+.4f}</div>
    <div class="card-sub">IV sensitivity</div>
    <span class="card-badge {'badge-red' if net_vanna<0 else 'badge-green'}">{'IV↑ = SELL δ' if net_vanna<0 else 'IV↑ = BUY δ'}</span>
  </div>
  <div class="card {'bear' if net_charm<0 else 'bull'}">
    <div class="card-label">Net Charm</div>
    <div class="card-val {val_cls(net_charm)}">{net_charm:+.4f}</div>
    <div class="card-sub">Time-decay hedging</div>
    <span class="card-badge {'badge-red' if net_charm<0 else 'badge-green'}">{'ΘDECAY DRAG' if net_charm<0 else 'ΘDECAY SUPPORT'}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 11. TABS
# ──────────────────────────────────────────
tab1, tab2 = st.tabs([
    "  ▣  DEX · CHARM · DECAY  ",
    "  ▤  VANNA · TABLE  "
])

# ════════════════════════════════════════════
# TAB 1
# ════════════════════════════════════════════
with tab1:

    # Key levels strip
    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    kc1.metric("SPOT",          f"{spot:,.1f}")
    kc2.metric("DEX ZERO",      f"{zero_cross:,.0f}" if zero_cross else "—")
    kc3.metric("VANNA CEILING", f"{ceil_zone[0]:.0f}–{ceil_zone[1]:.0f}" if ceil_zone else "—")
    kc4.metric("VANNA FLOOR",   f"{floor_zone[0]:.0f}–{floor_zone[1]:.0f}" if floor_zone else "—")
    kc5.metric("RANGE pts",     f"{ceil_zone[1]-floor_zone[0]:.0f}" if (ceil_zone and floor_zone) else "—")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── STRIKE RANGE SELECTION (shared for DEX and CHARM charts) ──
    all_strikes = gk_df.index.tolist()
    min_strike_default = int(min(all_strikes))
    max_strike_default = int(max(all_strikes))
    if 'dex_range' not in st.session_state:
        st.session_state.dex_range = (min_strike_default, max_strike_default)
    if 'charm_range' not in st.session_state:
        st.session_state.charm_range = (min_strike_default, max_strike_default)

    st.markdown('<div class="section-head">🔍 MANUAL STRIKE RANGE</div>', unsafe_allow_html=True)
    range_col1, range_col2 = st.columns(2)
    with range_col1:
        st.session_state.dex_range = st.slider(
            "DEX Chart range",
            min_value=min_strike_default, max_value=max_strike_default,
            value=st.session_state.dex_range, step=50,
            key="dex_range_slider"
        )
    with range_col2:
        st.session_state.charm_range = st.slider(
            "Charm Chart range",
            min_value=min_strike_default, max_value=max_strike_default,
            value=st.session_state.charm_range, step=50,
            key="charm_range_slider"
        )

    # ── DEX + CHARM side-by-side with selected ranges ──
    col_dex, col_charm = st.columns(2)
    with col_dex:
        st.markdown('<div class="section-head">DEX BY STRIKE</div>', unsafe_allow_html=True)
        dex_fig = make_dex_chart(gk_df, spot, zero_cross, height=370, x_range=st.session_state.dex_range)
        st.plotly_chart(dex_fig, use_container_width=True, config={"displayModeBar": False})
    with col_charm:
        st.markdown('<div class="section-head">CHARM BY STRIKE</div>', unsafe_allow_html=True)
        charm_fig = make_charm_chart(gk_df, spot, height=370, x_range=st.session_state.charm_range)
        st.plotly_chart(charm_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # DEX EXTREMES & CHARM EXTREMES
    # ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">⚡ EXTREMES & PRESSURE POINTS</div>', unsafe_allow_html=True)

    pos_strike, pos_dex, neg_strike, neg_dex = get_dex_extremes(gk_df)
    b_strike, b_charm, a_strike, a_charm = get_charm_extremes(gk_df, spot)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**DEX Extremes**")
        if pos_strike is not None:
            st.markdown(f"""
            <div class="extreme-card">
                <div class="extreme-title">📈 MAX POSITIVE DEX (Long Gamma)</div>
                <div class="extreme-value">{int(pos_strike):,}</div>
                <div class="extreme-sub">DEX: {pos_dex:+.3f}</div>
                <span class="extreme-badge">CALL OI dominant → dealer delta support</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="extreme-card">⚠️ No positive DEX strike with OI > 0</div>', unsafe_allow_html=True)

        if neg_strike is not None:
            st.markdown(f"""
            <div class="extreme-card">
                <div class="extreme-title">📉 MAX NEGATIVE DEX (Short Gamma)</div>
                <div class="extreme-value">{int(neg_strike):,}</div>
                <div class="extreme-sub">DEX: {neg_dex:+.3f}</div>
                <span class="extreme-badge">PUT OI heavy → dealer delta hedge accelerates</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="extreme-card">⚠️ No negative DEX strike with OI > 0</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("**Charm Extremes (Decay Pressure Range)**")
        if b_strike is not None:
            st.markdown(f"""
            <div class="extreme-card">
                <div class="extreme-title">🔻 BELOW SPOT · Max Negative Put Charm</div>
                <div class="extreme-value">{int(b_strike):,}  <span style="font-size:1rem;">(PE)</span></div>
                <div class="extreme-sub">Charm: {b_charm:.4f}</div>
                <span class="extreme-badge">Fastest put time‑decay below spot</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="extreme-card">⚠️ No negative put charm below spot</div>', unsafe_allow_html=True)

        if a_strike is not None:
            st.markdown(f"""
            <div class="extreme-card">
                <div class="extreme-title">🔺 ABOVE SPOT · Max Negative Call Charm</div>
                <div class="extreme-value">{int(a_strike):,}  <span style="font-size:1rem;">(CE)</span></div>
                <div class="extreme-sub">Charm: {a_charm:.4f}</div>
                <span class="extreme-badge">Fastest call time‑decay above spot</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="extreme-card">⚠️ No negative call charm above spot</div>', unsafe_allow_html=True)

        if b_strike and a_strike:
            st.markdown(f"""
            <div style='background:#0f1117;border:1px solid #f0a500;border-radius:8px;padding:12px;margin-top:8px;text-align:center;'>
                <span style='font-family:IBM Plex Mono;font-size:0.7rem;color:#f0a500;'>TRADING RANGE</span><br>
                <span style='font-family:IBM Plex Mono;font-size:1.2rem;font-weight:600;'>{int(b_strike):,}  ↔  {int(a_strike):,}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════
    # HIGHEST DECAY PRESSURE (with clear numbering)
    # ══════════════════════════════════════
    if not decay_df.empty:

        hd_col, share_col = st.columns([6, 1])
        with hd_col:
            st.markdown("""
            <div class="decay-header">
              <span class="decay-title">⚡ Highest Decay Pressure</span>
              <span style='font-family:IBM Plex Mono;font-size:0.65rem;color:#484f58;'>
                CE = orange &nbsp;·&nbsp; PE = green
              </span>
            </div>""", unsafe_allow_html=True)

        r1, r2 = st.columns(2)
        cols_cycle = [r1, r2]
        for i, (_, row) in enumerate(decay_df.iterrows()):
            worst = decay_df['charm_val'].min()
            pct   = int(abs(row['charm_val'] / worst) * 100)
            bar_class  = "decay-bar-ce"  if row['type'] == 'CE' else "decay-bar-pe"
            badge_class = "decay-type-ce" if row['type'] == 'CE' else "decay-type-pe"
            with cols_cycle[i % 2]:
                st.markdown(f"""
                <div class="decay-row">
                  <div class="decay-rank">#{i+1}</div>
                  <div class="decay-strike">{int(row['strike']):,}</div>
                  <div class="{badge_class}">{row['type']}</div>
                  <div class="decay-val">{row['charm_val']:.4f}</div>
                  <div class="decay-bar-wrap">
                    <div class="{bar_class}" style="width:{pct}%"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.markdown('<div class="section-head">DECAY CHART</div>', unsafe_allow_html=True)
        decay_fig = make_decay_bar_chart(decay_df, height=300)
        st.plotly_chart(decay_fig, use_container_width=True, config={
            "displayModeBar": True,
            "modeBarButtonsToKeep": ["toImage"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"fintrix_decay_{st.session_state.underlying}_{st.session_state.expiry_input}",
                "width": 1000, "height": 400, "scale": 2
            }
        })

    else:
        st.info("No negative Charm strikes found in current data.")

# ════════════════════════════════════════════
# TAB 2 — VANNA + TABLE
# ════════════════════════════════════════════
with tab2:

    st.markdown('<div class="section-head">VANNA BY STRIKE</div>', unsafe_allow_html=True)
    st.plotly_chart(make_vanna_chart(gk_df, spot, ceil_zone, floor_zone, height=360),
                    use_container_width=True, config={"displayModeBar": False})

    col_ceil, col_floor = st.columns(2)
    with col_ceil:
        if ceil_zone:
            st.markdown(f"""
            <div style='background:#0f1117;border:1px solid #3b82f6;border-left:3px solid #3b82f6;
            border-radius:4px;padding:14px 18px;margin-bottom:12px;'>
              <div style='font-family:IBM Plex Mono;font-size:0.6rem;color:#3b82f6;
              letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;'>Vanna Ceiling Zone</div>
              <div style='font-family:IBM Plex Mono;font-size:1.5rem;font-weight:600;color:#e6edf3;'>
                {int(ceil_zone[0]):,} – {int(ceil_zone[1]):,}
              </div>
              <div style='font-size:0.65rem;color:#484f58;font-family:IBM Plex Mono;margin-top:4px;'>
                IV crush → dealer BUY pressure above spot
              </div>
            </div>""", unsafe_allow_html=True)
    with col_floor:
        if floor_zone:
            st.markdown(f"""
            <div style='background:#0f1117;border:1px solid #ef4444;border-left:3px solid #ef4444;
            border-radius:4px;padding:14px 18px;margin-bottom:12px;'>
              <div style='font-family:IBM Plex Mono;font-size:0.6rem;color:#ef4444;
              letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;'>Vanna Floor Zone</div>
              <div style='font-family:IBM Plex Mono;font-size:1.5rem;font-weight:600;color:#e6edf3;'>
                {int(floor_zone[0]):,} – {int(floor_zone[1]):,}
              </div>
              <div style='font-size:0.65rem;color:#484f58;font-family:IBM Plex Mono;margin-top:4px;'>
                IV spike → dealer SELL pressure below spot
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-head">FULL STRIKE TABLE</div>', unsafe_allow_html=True)
    disp = gk_df[['dex','vanna','charm','charm_ce','charm_pe','call_oi','put_oi','call_iv','put_iv']].copy()
    disp.columns = ['DEX','Vanna','Charm','Charm CE','Charm PE','Call OI','Put OI','Call IV','Put IV']
    disp = disp[(disp['Call OI'] > 0) | (disp['Put OI'] > 0)]
    st.dataframe(
        disp.style.format({
            'DEX':'{:+.3f}','Vanna':'{:+.4f}','Charm':'{:+.4f}',
            'Charm CE':'{:+.4f}','Charm PE':'{:+.4f}',
            'Call OI':'{:.0f}','Put OI':'{:.0f}',
            'Call IV':'{:.4f}','Put IV':'{:.4f}'
        }).map(   # <--- FIX: changed from applymap to map
            lambda v: 'color:#ef4444' if isinstance(v,float) and v<0
                      else 'color:#22c55e' if isinstance(v,float) and v>0 else '',
            subset=['DEX','Vanna','Charm','Charm CE','Charm PE']
        ),
        use_container_width=True, height=440
    )

# ──────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────
st.markdown(f"""
<div style='margin-top:24px;padding-top:10px;border-top:1px solid #21262d;
font-family:IBM Plex Mono;font-size:0.6rem;color:#30363d;
display:flex;justify-content:space-between;'>
  <span>FINTRIX ANALYTICS · AVFINANCIAL</span>
  <span>LAST UPDATE: {last_upd.strftime('%Y-%m-%d %H:%M:%S')}</span>
  <span>SOURCE: NUBRA PROD · BS GREEKS</span>
</div>
""", unsafe_allow_html=True)
