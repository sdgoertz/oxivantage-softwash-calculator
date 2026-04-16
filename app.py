import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Soft Wash OxiVantage LF™ Savings Calculator", layout="wide", page_icon="🧪")

# BRANDING
st.markdown("""
    <style>
    .main-header {font-size: 42px; font-weight: bold; color: #1E3A8A;}
    .tagline {font-size: 18px; color: #0F172A; font-style: italic;}
    .metric-positive {color: #16a34a !important;}
    .metric-negative {color: #dc2626 !important;}
    section[data-testid="stSidebar"] {overflow: hidden;}
    </style>
""", unsafe_allow_html=True)

logo_path = "logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=420)

st.markdown('<h1 class="main-header">IG Chemical Solutions</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">OxiVantage LF™ • Soft Wash Bleach Savings Calculator</p>', unsafe_allow_html=True)
st.caption("Reduces bleach (NaOCl) consumption by up to 50% (top-end) • 2000 ppm dosing per TDS")

# ====================== INPUTS ======================
with st.sidebar:
    st.header("📍 Job Details")

    job_size = st.number_input("Job size (sq ft)", value=2000.0, min_value=500.0, step=100.0,
                               help="Total surface coverage area for the job — e.g. roof footprint, house siding, or combined surfaces being treated")
    app_rate = st.number_input("Application rate (gal of mix per 100 sq ft)", value=2.0, min_value=0.1, step=0.1,
                               help="How many gallons of final spray mix you apply per 100 sq ft. Typical: 1–2 gal/100 sq ft for roofs, 2–3 gal/100 sq ft for siding")

    bleach_concentrate_pct = 12.5  # Standard industrial soft wash strength

    final_naocl_pct = st.number_input("Final active NaOCl % in spray mix", value=3.0, min_value=0.5, max_value=6.0, step=0.1,
                                      help="Typical ranges: 0.5–2% for house siding, 2–4% for concrete/stucco, 3–6% for roofs")

    st.subheader("OxiVantage LF™")
    reduction_pct = st.slider("Bleach reduction % (25–50% per TDS)", 25, 50, 38, step=1,
                              help="25–50% is the effective range per TDS; 50% is top-end success")

    additive_price = st.number_input("Quoted OxiVantage LF™ price per lb", value=5.30, step=0.05)

    st.subheader("Pricing")
    bleach_price_per_gal = st.number_input("Bleach price per gal of concentrate", value=3.50, step=0.10,
                                           help="Typical 12.5% delivered price")

# ====================== CALCULATIONS ======================
total_mix_vol = (job_size / 100) * app_rate  # gallons

density = 8.34  # lb/gal

baseline_naocl_per_job = total_mix_vol * (final_naocl_pct / 100) * density  # lb active
with_naocl_per_job = baseline_naocl_per_job * (1 - reduction_pct / 100)

additive_per_job = total_mix_vol * density * 0.002  # 2000 ppm = 0.20% by mass, lb

# Convert active lb to concentrate gallons
baseline_conc_vol = (baseline_naocl_per_job / density) / (bleach_concentrate_pct / 100)
with_conc_vol = (with_naocl_per_job / density) / (bleach_concentrate_pct / 100)

baseline_chem_cost = baseline_conc_vol * bleach_price_per_gal
with_chem_cost = with_conc_vol * bleach_price_per_gal + (additive_per_job * additive_price)

savings = baseline_chem_cost - with_chem_cost
break_even = (baseline_chem_cost - with_conc_vol * bleach_price_per_gal) / additive_per_job if additive_per_job > 0 else 0

# ====================== DISPLAY ======================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bleach Used (no additive)", f"{baseline_conc_vol:.1f} gal")
with col2:
    st.metric("Bleach Used (with OxiVantage)", f"{with_conc_vol:.1f} gal",
              delta=f"-{baseline_conc_vol - with_conc_vol:.1f} gal", delta_color="inverse")
with col3:
    st.metric("Net Savings per Job", f"${savings:.0f}", delta_color="normal" if savings >= 0 else "inverse")

st.divider()
st.subheader("📊 Job Summary")
df = pd.DataFrame({
    "Metric": ["Job size", "Total mix volume", "Bleach cost (no additive)", "Total chemical cost (with OxiVantage)", "Net savings",
               "Bleach saved", "Break-even OxiVantage price (per lb)"],
    "Value": [f"{job_size:,.0f} sq ft", f"{total_mix_vol:.1f} gal", f"${baseline_chem_cost:.0f}",
              f"${with_chem_cost:.0f}", f"${savings:.0f}", f"{baseline_conc_vol - with_conc_vol:.1f} gal",
              f"${break_even:.2f}"]
})
st.dataframe(df, use_container_width=True, hide_index=True)

st.info("**Dosing per TDS:** OxiVantage LF™ = 2000 ppm (0.20%) in final working solution. 50% reduction is the absolute maximum — 30% is more typical.")
