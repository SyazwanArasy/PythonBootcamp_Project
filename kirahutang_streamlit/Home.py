import streamlit as st

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

# Define each page - matching your Flask sidebar menu
dashboard_page = st.Page("dashboard.py", title="Dashboard", icon="🏠", default=True)
pendapatan_page = st.Page("pages/1_Pendapatan.py", title="Pendapatan", icon="💵")
komitmen_page = st.Page("pages/2_Komitmen.py", title="Komitmen", icon="📋")
tunggakan_page = st.Page("pages/3_Tunggakan.py", title="Tunggakan", icon="⚠️")
hutang_page = st.Page("pages/4_Hutang.py", title="Hutang", icon="🤝")
belanja_page = st.Page("pages/5_Belanja.py", title="Belanja", icon="🛒")

# Build the navigation sidebar
pg = st.navigation([
    dashboard_page,
    pendapatan_page,
    komitmen_page,
    tunggakan_page,
    hutang_page,
    belanja_page,
])

# This must be called to actually render the selected page
pg.run()