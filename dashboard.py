from database.db_manager import DatabaseManager
import streamlit as st
from components.topnav import render_topnav
from components.translations import t

render_topnav()
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

.sub-card.hover-box:hover {
    filter: brightness(1.15);
}

[class*="sub-label"] { display: block; margin-bottom: 4px; }

.bill-box {
    background-color: #2b2b2b;
    border-radius: 10px;
    padding: 16px;
    margin-top: 10px;
}

.hover-box {
    cursor: pointer;
    transition: background-color 0.15s ease;
}
.hover-box:hover {
    background-color: #333333;
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
.bill-row-urgent {
    background-color: rgba(255, 82, 82, 0.12);
    border-left: 3px solid #ff5252;
    padding-left: 10px !important;
    margin-left: -13px;
}
.bill-name { font-weight: bold; font-size: 15px; }
.bill-due { font-size: 12px; opacity: 0.6; }
.bill-amount { color: #ff5252; font-weight: bold; text-align: right; }
.bill-days { font-size: 12px; opacity: 0.6; text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- Connect to database and calculate real totals ---
db = DatabaseManager()

hutang = db.get_total_hutang("saya_hutang")
komitmen = db.get_total_komitmen()
tunggakan = db.get_total_tunggakan()
jumlah_hutang = hutang + komitmen + tunggakan  # auto-calculated, not hardcoded!

tetap = db.get_total_pendapatan("Tetap")
tambahan = db.get_total_pendapatan("Tambahan")
lain_lain = db.get_total_pendapatan("Lain-lain")
belanja_total = db.get_total_belanja()
baki_bersih = tetap + tambahan + lain_lain - belanja_total  # income minus spending
belanja_this_month = db.get_total_belanja_this_month()

# --- Build the "Apa belum dibayar" list from real unpaid bills ---
from datetime import datetime

def format_due_date(due_date_str):
    # Converts '2026-08-31' into 'Due: 31 August 2026'
    dt = datetime.strptime(due_date_str, "%Y-%m-%d")
    return f"Due: {dt.strftime('%d %B %Y')}"

def days_remaining(due_date_str):
    dt = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    delta = (dt - datetime.today().date()).days
    if delta < 0:
        return f"{abs(delta)} hari lewat"
    return f"{delta} hari lagi"

def days_until(due_date_str):
    dt = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    return (dt - datetime.today().date()).days

raw_bills = db.get_upcoming_bills(limit=6)
bills = [
    (
        row["name"],
        format_due_date(row["due_date"]),
        row["amount"],
        days_remaining(row["due_date"]),
        days_until(row["due_date"]) <= 3  # is this urgent?
    )
    for row in raw_bills
]

# --- Row 1: red and green cards, full width, side by side ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
<div class="metric-card red-card">
    <div class="label">{t('jumlah_hutang')}</div>
    <div class="value">-RM {jumlah_hutang:,.2f}</div>
    <div class="sub">{t('perlu_dibayar')}</div>
</div>
""", unsafe_allow_html=True)

    sub1, sub2, sub3 = st.columns(3)
    with sub1:
        st.markdown(f"""
        <a href="/hutang" target="_self" style="text-decoration:none; color:inherit; display:block;">
        <div class="sub-card hover-box" style="background:#8a1c1c;">
            <span class="sub-label">{t('hutang')}</span>RM {hutang:,.2f}</div>
        </a>""", unsafe_allow_html=True)
    with sub2:
        st.markdown(f"""
        <a href="/komitmen" target="_self" style="text-decoration:none; color:inherit; display:block;">
        <div class="sub-card hover-box" style="background:#8a1c1c;">
            <span class="sub-label">{t('komitmen')}</span>RM {komitmen:,.2f}</div>
        </a>""", unsafe_allow_html=True)
    with sub3:
        st.markdown(f"""
        <a href="/tunggakan" target="_self" style="text-decoration:none; color:inherit; display:block;">
        <div class="sub-card hover-box" style="background:#c56a1f;">
            <span class="sub-label">{t('tunggakan')}</span>RM {tunggakan:,.2f}</div>
        </a>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div class="metric-card green-card">
    <div class="label">{t('pendapatan_anda')}</div>
    <div class="value">RM {baki_bersih:,.2f}</div>
    <div class="sub">{t('baki_bersih')}</div>
</div>
""", unsafe_allow_html=True)

    sub4, sub5, sub6 = st.columns(3)
    with sub4:
            st.markdown(f"""
            <a href="/pendapatan" target="_self" style="text-decoration:none; color:inherit; display:block;">
            <div class="sub-card hover-box" style="background:#1c7a44;">
                <span class="sub-label">{t('tetap')}</span>RM {tetap:,.2f}</div>
            </a>""", unsafe_allow_html=True)
    with sub5:
            st.markdown(f"""
            <a href="/pendapatan" target="_self" style="text-decoration:none; color:inherit; display:block;">
            <div class="sub-card hover-box" style="background:#1c7a44;">
                <span class="sub-label">{t('tambahan')}</span>RM {tambahan:,.2f}</div>
            </a>""", unsafe_allow_html=True)
    with sub6:
            st.markdown(f"""
            <a href="/pendapatan" target="_self" style="text-decoration:none; color:inherit; display:block;">
            <div class="sub-card hover-box" style="background:#1c7a44;">
                <span class="sub-label">{t('lain_lain')}</span>RM {lain_lain:,.2f}</div>
            </a>""", unsafe_allow_html=True)
            
 # --- Belanja summary card (this month) ---
st.markdown(f"""
<a href="/belanja" target="_self" style="text-decoration:none; color:inherit; display:block;">
<div class="sub-card hover-box" style="background: linear-gradient(135deg, #4a1a7a, #7b2fb3); padding: 16px; margin-top: 10px; text-align:left;">
    <span class="sub-label" style="font-size:14px;">{t('belanja_bulan_ini')}</span>
    <span style="font-size:24px; font-weight:700;">RM {belanja_this_month:,.2f}</span>
</div>
</a>
""", unsafe_allow_html=True)   

# --- Row 2: "Apa belum dibayar" list, full width, below the cards ---
# Note: no leading spaces on each line - indentation confuses Streamlit's
# markdown parser into treating this as a code block instead of HTML.
rows_html = ""
for name, due, amount, days_left, is_urgent in bills:
    row_class = "bill-row bill-row-urgent" if is_urgent else "bill-row"
    urgent_flag = " 🔥" if is_urgent else ""
    rows_html += (
        f'<div class="{row_class}">'
        '<div>'
        f'<div class="bill-name">{name}{urgent_flag}</div>'
        f'<div class="bill-due">{due}</div>'
        '</div>'
        '<div>'
        f'<div class="bill-amount">RM {amount:,.2f}</div>'
        f'<div class="bill-days">{days_left}</div>'
        '</div>'
        '</div>'
    )

st.markdown(
    '<a href="/komitmen" target="_self" style="text-decoration:none; color:inherit; display:block;">'
    '<div class="bill-box hover-box">'
    f'<div class="bill-box-title">{t('apa_belum_dibayar')}</div>'
    f'<div class="bill-box-sub">{t('bulan_ini')}</div>'
    f'{rows_html}'
    '</div>'
    '</a>',
    unsafe_allow_html=True
)