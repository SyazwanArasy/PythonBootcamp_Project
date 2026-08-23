import streamlit as st
from database.db_manager import DatabaseManager
from components.topnav import render_topnav

db = DatabaseManager()

render_topnav()
st.title("History")


# --- CSS ---
st.markdown("""
<style>
.history-item-name { font-weight: 600; font-size: 16px; }
.history-item-meta { font-size: 12px; opacity: 0.55; }
.history-item-amount { font-size: 20px; font-weight: 700; text-align: right; }
.history-tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 10px;
    margin-bottom: 4px;
}
.tag-komitmen { background-color: #7a1010; color: white; }
.tag-hutang { background-color: #1c7a44; color: white; }
</style>
""", unsafe_allow_html=True)

st.caption("All Komitmen and Hutang entries, sorted by date.")

# --- Combine Komitmen + Hutang into one list, sorted by date ---
history_items = db.get_history()

if not history_items:
    st.caption("No history yet.")

for item in history_items:
    with st.container(border=True):
        tag_class = "tag-komitmen" if item["source"] == "Komitmen" else "tag-hutang"
        info_col, amount_col = st.columns([1.4, 1])
        with info_col:
            st.markdown(f"""
            <span class="history-tag {tag_class}">{item['source']}</span><br>
            <div class="history-item-name">{item['name']}</div>
            <div class="history-item-meta">{item['date']} · {item['status']}</div>
            """, unsafe_allow_html=True)
        with amount_col:
            st.markdown(f'<div class="history-item-amount">RM {item["amount"]:,.2f}</div>', unsafe_allow_html=True)