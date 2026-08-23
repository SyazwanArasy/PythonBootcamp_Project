import streamlit as st
from components.translations import t


# Page configuration - controls browser tab title, icon, and layout width
st.set_page_config(
    page_title="KiraHutang.com",
    page_icon="💰",
    layout="wide"
)

# # App title shown at the top of the sidebar, above the nav menu
# st.sidebar.markdown("## 💰 KiraHutang.com")
# st.sidebar.markdown("---")

# st.logo() places branding ABOVE the nav menu (not regular sidebar content)
st.logo("static/logo.png", size="large")

# --- Language selector ---
if "lang" not in st.session_state:
    st.session_state["lang"] = "ms"  # default language

lang_choice = st.sidebar.radio(
    "🌐 Language / Bahasa",
    options=["ms", "en"],
    format_func=lambda x: "Bahasa Melayu" if x == "ms" else "English",
    index=0 if st.session_state["lang"] == "ms" else 1,
    key="lang_selector"
)
st.session_state["lang"] = lang_choice

st.markdown("""
<style>
/* Give bordered cards (Komitmen/Tunggakan/Hutang/Belanja) a slightly
   lighter shade than the page background, so they stand out instead of
   blending in */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #333333 !important;
    border-radius: 10px !important;
}

/* Hide the 7th and 8th sidebar nav items (History, Analytics) -
   still valid pages/routes, just not shown in the sidebar menu.
   Only reachable via the top navbar links instead. */
div[data-testid="stSidebarNav"] ul li:nth-child(7),
div[data-testid="stSidebarNav"] ul li:nth-child(8) {
    display: none;
}

/* Prevent button labels (Mark paid, Edit, Delete) from wrapping onto two
   lines when the sidebar is open and columns get narrower */
.stButton > button p {
    white-space: nowrap !important;
    font-size: 13px !important;
}
.stButton > button {
    padding-left: 10px !important;
    padding-right: 10px !important;
}

/* Prevent amount text (RM X,XXX.XX) from wrapping onto two lines when
   the sidebar narrows the content area - matches any class name ending
   in "-amount" across all pages (bill-item-amount, hutang-item-amount,
   belanja-item-amount, etc.) */
[class*="-amount"] {
    white-space: nowrap !important;
    font-size: 20px !important;
}
</style>
""", unsafe_allow_html=True)

# Define each page - matching your Flask sidebar menu
dashboard_page = st.Page("dashboard.py", title=t("dashboard"), icon=":material/home:", default=True, url_path="dashboard")
pendapatan_page = st.Page("pages/1_Pendapatan.py", title=t("pendapatan"), icon=":material/payments:", url_path="pendapatan")
komitmen_page = st.Page("pages/2_Komitmen.py", title=t("komitmen"), icon=":material/receipt:", url_path="komitmen")
tunggakan_page = st.Page("pages/3_Tunggakan.py", title=t("tunggakan"), icon=":material/report_problem:", url_path="tunggakan")
hutang_page = st.Page("pages/4_Hutang.py", title=t("hutang"), icon=":material/handshake:", url_path="hutang")
belanja_page = st.Page("pages/5_Belanja.py", title=t("belanja"), icon=":material/shopping_cart:", url_path="belanja")
history_page = st.Page("pages/6_History.py", title=t("history"), icon=":material/history:", url_path="history")
analytics_page = st.Page("pages/7_Analytics.py", title=t("analytics"), icon=":material/bar_chart:", url_path="analytics")

# Build the navigation sidebar
pg = st.navigation([
    dashboard_page,
    pendapatan_page,
    komitmen_page,
    tunggakan_page,
    hutang_page,
    belanja_page,
    history_page,
    analytics_page
    
])

# This must be called to actually render the selected page
pg.run()