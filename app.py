import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Soft Wash OxiVantage LF™ Savings Calculator", layout="wide", page_icon="🧪")

# BRANDING
st.markdown("""
    <style>
    .main-header {font-size: 42px; font-weight: bold; color: #1E3A8A;}
    .tagline {font-size: 18px; color: #0F172A; font-style: italic;}
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
    st.header("📍 Usage Details")

    monthly_bleach_gal = st.number_input(
        "Monthly bleach usage (gal of concentrate)",
        value=100.0, min_value=1.0, step=5.0,
        help="How many gallons of 12.5% bleach concentrate your operation goes through in a typical month"
    )

    final_naocl_pct = st.number_input(
        "Final NaOCl % in spray mix",
        value=3.0, min_value=0.5, max_value=6.0, step=0.1,
        help="Typical ranges: 0.5–2% for house siding, 2–4% for concrete/stucco, 3–6% for roofs"
    )

    st.subheader("OxiVantage LF™")
    reduction_pct = st.slider(
        "Bleach reduction % (25–50% per TDS)", 25, 50, 38, step=1,
        help="25–50% is the effective range per TDS; 50% is top-end success"
    )
    additive_price = st.number_input("Quoted OxiVantage LF™ price per lb", value=5.30, step=0.05)

    st.subheader("Pricing")
    bleach_price_per_gal = st.number_input(
        "Bleach price per gal of concentrate", value=3.50, step=0.10,
        help="Typical 12.5% delivered price"
    )

# ====================== CALCULATIONS ======================
bleach_concentrate_pct = 12.5
density = 8.34  # lb/gal

# Total working solution volume per month derived from concentrate usage and dilution ratio
total_mix_vol = monthly_bleach_gal * (bleach_concentrate_pct / final_naocl_pct)

# Bleach volumes
with_bleach_gal = monthly_bleach_gal * (1 - reduction_pct / 100)
bleach_saved = monthly_bleach_gal - with_bleach_gal

# Additive: 2000 ppm by mass in total working solution
additive_per_month = total_mix_vol * density * 0.002  # lb

# Costs
baseline_cost = monthly_bleach_gal * bleach_price_per_gal
with_cost = with_bleach_gal * bleach_price_per_gal + additive_per_month * additive_price

savings = baseline_cost - with_cost
break_even = (baseline_cost - with_bleach_gal * bleach_price_per_gal) / additive_per_month if additive_per_month > 0 else 0

# ====================== DISPLAY ======================
view = st.radio("View", ["Monthly", "Annual"], horizontal=True)
multiplier = 12 if view == "Annual" else 1
period = "Annual" if view == "Annual" else "Monthly"

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"Bleach Used (no additive)", f"{monthly_bleach_gal * multiplier:.1f} gal")
with col2:
    st.metric(f"Bleach Used (with OxiVantage)", f"{with_bleach_gal * multiplier:.1f} gal",
              delta=f"-{bleach_saved * multiplier:.1f} gal", delta_color="inverse")
with col3:
    st.metric(f"Net {period} Savings", f"${savings * multiplier:.0f}",
              delta_color="normal" if savings >= 0 else "inverse")

st.divider()
st.subheader(f"📊 {period} Summary")
df = pd.DataFrame({
    "Metric": [
        "Bleach used (no additive)",
        "Bleach used (with OxiVantage)",
        "Bleach saved",
        "Bleach cost (no additive)",
        "Total chemical cost (with OxiVantage)",
        f"Net {period.lower()} savings",
        "Break-even OxiVantage price (per lb)",
    ],
    "Value": [
        f"{monthly_bleach_gal * multiplier:.1f} gal",
        f"{with_bleach_gal * multiplier:.1f} gal",
        f"{bleach_saved * multiplier:.1f} gal",
        f"${baseline_cost * multiplier:.0f}",
        f"${with_cost * multiplier:.0f}",
        f"${savings * multiplier:.0f}",
        f"${break_even:.2f}",
    ]
})
st.dataframe(df, use_container_width=True, hide_index=True)

st.info("**Dosing per TDS:** OxiVantage LF™ = 2000 ppm (0.20%) in final working solution. 50% reduction is the absolute maximum — 30% is more typical.")
