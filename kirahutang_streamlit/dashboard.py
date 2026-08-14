import streamlit as st

st.title("Dashboard")

# --- Custom CSS ---
st.markdown("""
<style>
.metric-card {
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    margin-bottom: 10px;
}
.metric-card .label { font-size: 14px; opacity: 0.85; }
.metric-card .value { font-size: 36px; font-weight: bold; margin: 8px 0; }
.metric-card .sub { font-size: 13px; opacity: 0.85; }
.red-card { background: linear-gradient(135deg, #7a1010, #b71c1c); }
.green-card { background: linear-gradient(135deg, #0d5c2f, #1b8f4c); }

.sub-card {
    border-radius: 8px;
    padding: 14px;
    text-align: center;
    color: white;
    font-weight: bold;
}
.sub-card .sub-label {
    font-weight: normal;
    font-size: 13px;
    display: block;
    margin-bottom: 4px;
}

.bill-box {
    background-color: #2b2b2b;
    border-radius: 10px;
    padding: 16px;
    margin-top: 10px;
}
.bill-box-title { font-size: 18px; font-weight: bold; margin-bottom: 2px; }
.bill-box-sub { font-size: 13px; opacity: 0.7; margin-bottom: 12px; }
.bill-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 10px 0;
    border-bottom: 1px solid #3a3a3a;
}
.bill-row:last-child { border-bottom: none; }
.bill-name { font-weight: bold; font-size: 15px; }
.bill-due { font-size: 12px; opacity: 0.6; }
.bill-amount { color: #ff5252; font-weight: bold; text-align: right; }
.bill-days { font-size: 12px; opacity: 0.6; text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- Hardcoded summary data ---
jumlah_hutang = 9282.25
hutang = 550.00
komitmen = 5889.75
tunggakan = 2842.50

baki_bersih = 6599.62
tetap = 3599.62
tambahan = 2500.00
lain_lain = 500.00

bills = [
    ("House Loan", "Due: 31 August 2026", 1650.00, "7 hari lagi"),
    ("Credit Card", "Due: 13 September 2026", 560.95, "14 hari lagi"),
    ("Internet", "Due: 13 September 2026", 104.92, "14 hari lagi"),
    ("TNB", "Due: 31 August 2026", 240.63, "7 hari lagi"),
    ("Car Services", "Due: 31 August 2026", 350.00, "7 hari lagi"),
    ("Road Tax & Insurances", "Due: 31 August 2026", 376.85, "7 hari lagi"),
]

# --- Row 1: red and green cards, full width, side by side ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card red-card">
        <div class="label">Jumlah hutang</div>
        <div class="value">-RM {jumlah_hutang:,.2f}</div>
        <div class="sub">Perlu dibayar</div>
    </div>
    """, unsafe_allow_html=True)

    sub1, sub2, sub3 = st.columns(3)
    with sub1:
        st.markdown(f"""<div class="sub-card" style="background:#8a1c1c;">
            <span class="sub-label">Hutang</span>RM {hutang:,.2f}</div>""", unsafe_allow_html=True)
    with sub2:
        st.markdown(f"""<div class="sub-card" style="background:#8a1c1c;">
            <span class="sub-label">Komitmen</span>RM {komitmen:,.2f}</div>""", unsafe_allow_html=True)
    with sub3:
        st.markdown(f"""<div class="sub-card" style="background:#c56a1f;">
            <span class="sub-label">Tunggakan</span>RM {tunggakan:,.2f}</div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card green-card">
        <div class="label">Baki bersih</div>
        <div class="value">RM {baki_bersih:,.2f}</div>
        <div class="sub">Pendapatan anda</div>
    </div>
    """, unsafe_allow_html=True)

    sub4, sub5, sub6 = st.columns(3)
    with sub4:
        st.markdown(f"""<div class="sub-card" style="background:#1c7a44;">
            <span class="sub-label">Tetap</span>RM {tetap:,.2f}</div>""", unsafe_allow_html=True)
    with sub5:
        st.markdown(f"""<div class="sub-card" style="background:#1c7a44;">
            <span class="sub-label">Tambahan</span>RM {tambahan:,.2f}</div>""", unsafe_allow_html=True)
    with sub6:
        st.markdown(f"""<div class="sub-card" style="background:#1c7a44;">
            <span class="sub-label">Lain-lain</span>RM {lain_lain:,.2f}</div>""", unsafe_allow_html=True)

# --- Row 2: "Apa belum dibayar" list, full width, below the cards ---
# Note: no leading spaces on each line - indentation confuses Streamlit's
# markdown parser into treating this as a code block instead of HTML.
rows_html = ""
for name, due, amount, days_left in bills:
    rows_html += (
        '<div class="bill-row">'
        '<div>'
        f'<div class="bill-name">{name}</div>'
        f'<div class="bill-due">{due}</div>'
        '</div>'
        '<div>'
        f'<div class="bill-amount">RM {amount:,.2f}</div>'
        f'<div class="bill-days">{days_left}</div>'
        '</div>'
        '</div>'
    )

st.markdown(
    '<div class="bill-box">'
    '<div class="bill-box-title">Apa belum dibayar</div>'
    '<div class="bill-box-sub">Bulan ini</div>'
    f'{rows_html}'
    '</div>',
    unsafe_allow_html=True
)