import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

st.set_page_config(page_title="Soft Wash OxiVantage LF™ Savings Calculator", layout="wide", page_icon="🧪")

# BRANDING
st.markdown("""
    <style>
    .main-header {font-size: 42px; font-weight: bold; color: #1E3A8A;}
    .tagline {font-size: 18px; color: #0F172A; font-style: italic;}
    .metric-positive {color: #16a34a !important;}
    .metric-negative {color: #dc2626 !important;}
    </style>
""", unsafe_allow_html=True)

logo_path = "logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=420)

st.markdown('<h1 class="main-header">IG Chemical Solutions</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">OxiVantage LF™ • Soft Wash Bleach Savings Calculator</p>', unsafe_allow_html=True)
st.caption("Reduces bleach (NaOCl) consumption by up to 50% (top-end) • 2000 ppm dosing per TDS • Job-size focused for roof & house washing")

# ====================== INPUTS ======================
with st.sidebar:
    st.header("📍 Job & Units")
    units = st.radio("Units", ["Imperial (gal, lb, sq ft, USD)", "Metric (L, kg, m², USD)"], horizontal=True)
    is_imperial = units.startswith("Imperial")
    vol_unit = "gal" if is_imperial else "L"
    area_unit = "sq ft" if is_imperial else "m²"
    mass_unit = "lb" if is_imperial else "kg"

    st.subheader("Job Details")
    job_size = st.number_input(f"Job size ({area_unit})", value=2000.0, min_value=500.0, step=100.0,
                               help="Typical roof or house surface area")
    mix_coverage = st.number_input(f"Mix coverage (gallons or L of final mix per 100 {area_unit})",
                                   value=2.0 if is_imperial else 7.57, step=0.1,
                                   help="Industry rule of thumb ≈ 1 gal mix per 50 sq ft roof (2 gal per 100 sq ft)")

    bleach_concentrate_pct = st.number_input("Bleach concentrate strength (%)", value=12.5, min_value=5.0, step=0.5,
                                             help="Most common industrial strength is 12.5%")
    final_naocl_pct = st.number_input("Final active NaOCl % in spray mix", value=3.0, min_value=0.5, step=0.1,
                                      help="Typical soft wash: 1–4% for roofs, 0.5–2.5% for house siding")

    st.subheader("OxiVantage LF™")
    reduction_pct = st.slider("Bleach reduction % (0–50% max per TDS)", 0, 50, 30, step=1,
                              help="30% is realistic; 50% is top-end success")

    your_price_to_dist = st.number_input(f"Your price to distributor per {mass_unit}", value=2.15, step=0.01)
    additive_price = st.number_input(f"Customer quoted price per {mass_unit}", value=2.50, step=0.01)

    st.subheader("Pricing")
    bleach_price_per_gal = st.number_input(f"Bleach price per {vol_unit} of concentrate", value=3.50, step=0.10,
                                           help="Typical 12.5% delivered price")

# ====================== CALCULATIONS ======================
mix_per_100 = mix_coverage
total_mix_vol = (job_size / 100) * mix_per_100

density = 8.34 if is_imperial else 1.0  # lb/gal or kg/L approx

baseline_naocl_per_job = total_mix_vol * (final_naocl_pct / 100) * density   # lb or kg active
with_naocl_per_job = baseline_naocl_per_job * (1 - reduction_pct / 100)

additive_per_job = total_mix_vol * density * 0.002   # 2000 ppm = 0.20%

# Convert active to concentrate gallons/liters
baseline_conc_vol = (baseline_naocl_per_job / density) / (bleach_concentrate_pct / 100)
with_conc_vol = (with_naocl_per_job / density) / (bleach_concentrate_pct / 100)

baseline_chem_cost = baseline_conc_vol * bleach_price_per_gal
with_chem_cost = with_conc_vol * bleach_price_per_gal + (additive_per_job * additive_price)

savings = baseline_chem_cost - with_chem_cost
break_even = (baseline_chem_cost - with_conc_vol * bleach_price_per_gal) / additive_per_job if additive_per_job > 0 else 0

# ====================== DISPLAY ======================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bleach used per job (baseline)", f"{baseline_conc_vol:.1f} {vol_unit}")
with col2:
    st.metric("Bleach used per job (with OxiVantage)", f"{with_conc_vol:.1f} {vol_unit}",
              delta=f"-{baseline_conc_vol - with_conc_vol:.1f} {vol_unit}")
with col3:
    st.metric("Net Savings per Job", f"${savings:.0f}", delta_color="normal" if savings >= 0 else "inverse")

st.divider()
st.subheader("📊 Job Summary")
df = pd.DataFrame({
    "Metric": ["Job size", "Final mix volume", "Baseline bleach cost", "New chemical cost", "Net savings per job",
               "Bleach gallons/liters saved", "Break-even OxiVantage price"],
    "Value": [f"{job_size:,.0f} {area_unit}", f"{total_mix_vol:.1f} {vol_unit}", f"${baseline_chem_cost:.0f}",
              f"${with_chem_cost:.0f}", f"${savings:.0f}", f"{baseline_conc_vol - with_conc_vol:.1f} {vol_unit}",
              f"${break_even:.2f}"]
})
st.dataframe(df, use_container_width=True, hide_index=True)

st.info("**Dosing per TDS:** OxiVantage LF™ = 2000 ppm (0.20%) in final working solution. 50% reduction is the absolute maximum — 30% is more typical.")

# PDF & CSV
csv = df.to_csv(index=False).encode()
st.download_button("📥 Download CSV", csv, "SoftWash_OxiVantage_Savings.csv", "text/csv")


def create_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 50, 700, width=220, height=70, preserveAspectRatio=True)
        except Exception:
            pass
    c.setFont("Helvetica-Bold", 20)
    c.drawString(300, 750, "Soft Wash OxiVantage LF™ Savings Report")
    y = 680
    for _, row in df.iterrows():
        c.drawString(50, y, f"{row['Metric']}: {row['Value']}")
        y -= 25
    c.save()
    buffer.seek(0)
    return buffer


pdf_bytes = create_pdf()
st.download_button("📄 Save PDF Report (with logo)", pdf_bytes, "SoftWash_OxiVantage_Report.pdf", "application/pdf")

st.caption("✅ Quick & lean for soft wash • Job-size focused • Bleach reduction 0–50% (50% = top end)")
