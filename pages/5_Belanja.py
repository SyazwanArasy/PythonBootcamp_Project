import streamlit as st
import plotly.express as px
import pandas as pd
from database.db_manager import DatabaseManager
from datetime import date, datetime
from components.topnav import render_topnav
from itertools import groupby
from components.translations import t

db = DatabaseManager()

render_topnav()
st.title(t("belanja"))

BASE_CATEGORIES = [
    "Food", "Beverages", "Shopping", "Grocery", "Transport",
    "Self-care", "Health", "Family", "Entertainment", "Education"
]

def get_category_options(db):
    # Combine the base list with any custom categories already used,
    # so once you type a new one, it's available to pick again later.
    used = db.get_distinct_belanja_categories()
    combined = BASE_CATEGORIES + [c for c in used if c not in BASE_CATEGORIES]
    return combined + ["+ Add new category"]

def format_day_header(date_str):
    # Converts '2026-08-17' into 'Mon, 17/08/2026'
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%a, %d/%m/%Y")

# --- CSS ---
st.markdown("""
<style>
.belanja-total {
    background: linear-gradient(135deg, #4a1a7a, #7b2fb3);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}
.belanja-total .label { font-size: 14px; opacity: 0.85; }
.belanja-total .value { font-size: 36px; font-weight: bold; margin: 8px 0; }

.belanja-item-name { font-weight: 600; font-size: 16px; }
.belanja-item-meta { font-size: 12px; opacity: 0.55; margin-bottom: 10px; }
.belanja-item-amount { font-size: 22px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- Total spending ---
total = db.get_total_belanja()
st.markdown(f"""
<div class="belanja-total">
    <div class="label">{t("jumlah_belanja")}</div>
    <div class="value">RM {total:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# --- Add new expense ---
with st.popover("➕ Add " + t("belanja")):
    category_options = get_category_options(db)
    with st.form(key="add_belanja_form", clear_on_submit=True):
        name = st.text_input("What did you spend on?")
        category_choice = st.selectbox("Category", category_options)
        # Only shows up if "+ Add new category" is picked - Streamlit still
        # renders this input either way, but it's ignored unless selected above
        custom_category = st.text_input("New category name (only if selected above)")
        amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
        date_spent = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Save")

        if submitted:
            final_category = custom_category.strip() if category_choice == "+ Add new category" else category_choice
            if name.strip() == "":
                st.warning("Please enter a name.")
            elif category_choice == "+ Add new category" and custom_category.strip() == "":
                st.warning("Please enter the new category name.")
            else:
                db.add_belanja(name, final_category, amount_input, date_spent.isoformat())
                st.success(f"{name} added!")
                st.rerun()

# --- Category breakdown pie chart ---
category_totals = db.get_belanja_category_totals()
if category_totals:
    df = pd.DataFrame([dict(row) for row in category_totals])
    fig = px.pie(df, names="category", values="total", hole=0.4)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Filter by category ---
# --- Filters: category, month, and custom date range ---
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    filter_category = st.selectbox("Filter by category", ["All"] + get_category_options(db)[:-1])

with filter_col2:
    available_months = db.get_distinct_belanja_months()
    month_options = ["All"] + available_months
    filter_month = st.selectbox("Filter by month", month_options)

use_custom_range = st.checkbox("📅 Use custom date range instead")

start_date_filter = None
end_date_filter = None

if use_custom_range:
    range_col1, range_col2 = st.columns(2)
    with range_col1:
        start_date_filter = st.date_input("From", value=date.today().replace(day=1)).isoformat()
    with range_col2:
        end_date_filter = st.date_input("To", value=date.today()).isoformat()
    # When using a custom range, month filter is ignored
    filter_month = None

entries = db.get_belanja_filtered(
    category=filter_category,
    month=filter_month,
    start_date=start_date_filter,
    end_date=end_date_filter
)

if not entries:
    st.caption("No expenses recorded yet.")

# Group entries by date so we can show a day header above each cluster.
# groupby requires the list to already be sorted by the grouping key -
# entries come pre-sorted by date_spent DESC from the database, so this
# works directly without re-sorting.
grouped_entries = groupby(entries, key=lambda e: e["date_spent"])

for day, day_entries in grouped_entries:
    st.markdown(f"#### {format_day_header(day)}")

    for entry in day_entries:
        edit_key = f"editing_belanja_{entry['id']}"

        if st.session_state.get(edit_key, False):
            # ---- EDIT MODE ----
            with st.container(border=True):
                with st.form(key=f"edit_belanja_form_{entry['id']}"):
                    new_name = st.text_input("What did you spend on?", value=entry["name"])
                    edit_category_options = get_category_options(db)[:-1]
                    new_category = st.selectbox(
                        "Category", edit_category_options,
                        index=edit_category_options.index(entry["category"]) if entry["category"] in edit_category_options else 0
                    )
                    new_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01, value=entry["amount"])
                    new_date = st.date_input(
                        "Date",
                        value=datetime.strptime(entry["date_spent"], "%Y-%m-%d").date()
                    )

                    save_col, cancel_col = st.columns(2)
                    with save_col:
                        if st.form_submit_button("Save changes"):
                            db.update_belanja(entry["id"], new_name, new_category, new_amount, new_date.isoformat())
                            st.session_state[edit_key] = False
                            st.rerun()
                    with cancel_col:
                        if st.form_submit_button("Cancel"):
                            st.session_state[edit_key] = False
                            st.rerun()
        else:
            # ---- NORMAL VIEW ----
            with st.container(border=True):
                info_col, amount_col = st.columns([1.4, 1])
                with info_col:
                    st.markdown(f"""
                    <div class="belanja-item-name">{entry['name']}</div>
                    <div class="belanja-item-meta">{entry['category']}</div>
                    """, unsafe_allow_html=True)
                with amount_col:
                    st.markdown(f"""
                    <div class="belanja-item-amount" style="text-align:right;">RM {entry['amount']:,.2f}</div>
                    """, unsafe_allow_html=True)

                edit_col, spacer_col, delete_col = st.columns([1, 2, 1])
                with edit_col:
                    if st.button("Edit", key=f"belanja_edit_{entry['id']}"):
                        st.session_state[edit_key] = True
                        st.rerun()
                with delete_col:
                    if st.button("Delete", key=f"belanja_delete_{entry['id']}"):
                        db.delete_belanja(entry["id"])
                        st.rerun()

# for entry in entries:
#     edit_key = f"editing_belanja_{entry['id']}"

#     if st.session_state.get(edit_key, False):
#         # ---- EDIT MODE ----
#         with st.container(border=True):
#             with st.form(key=f"edit_belanja_form_{entry['id']}"):
#                 new_name = st.text_input("What did you spend on?", value=entry["name"])
#                 edit_category_options = get_category_options(db)[:-1]
#                 new_category = st.selectbox(
#                     "Category", edit_category_options,
#                     index=edit_category_options.index(entry["category"]) if entry["category"] in edit_category_options else 0
#                 )
#                 new_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01, value=entry["amount"])
#                 new_date = st.date_input(
#                     "Date",
#                     value=datetime.strptime(entry["date_spent"], "%Y-%m-%d").date()
#                 )

#                 save_col, cancel_col = st.columns(2)
#                 with save_col:
#                     if st.form_submit_button("Save changes"):
#                         db.update_belanja(entry["id"], new_name, new_category, new_amount, new_date.isoformat())
#                         st.session_state[edit_key] = False
#                         st.rerun()
#                 with cancel_col:
#                     if st.form_submit_button("Cancel"):
#                         st.session_state[edit_key] = False
#                         st.rerun()
#     else:
#         # ---- NORMAL VIEW ----
#         with st.container(border=True):
#             info_col, amount_col = st.columns([1.4, 1])
#             with info_col:
#                 st.markdown(f"""
#                 <div class="belanja-item-name">{entry['name']}</div>
#                 <div class="belanja-item-meta">{entry['category']} · {entry['date_spent']}</div>
#                 """, unsafe_allow_html=True)
#             with amount_col:
#                 st.markdown(f"""
#                 <div class="belanja-item-amount" style="text-align:right;">RM {entry['amount']:,.2f}</div>
#                 """, unsafe_allow_html=True)

#             edit_col, spacer_col, delete_col = st.columns([1, 2, 1])
#             with edit_col:
#                 if st.button("Edit", key=f"belanja_edit_{entry['id']}"):
#                     st.session_state[edit_key] = True
#                     st.rerun()
#             with delete_col:
#                 if st.button("Delete", key=f"belanja_delete_{entry['id']}"):
#                     db.delete_belanja(entry["id"])
#                     st.rerun()