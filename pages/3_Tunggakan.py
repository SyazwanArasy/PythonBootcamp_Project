import streamlit as st
from database.db_manager import DatabaseManager
from datetime import date, datetime, timedelta
from components.topnav import render_topnav
from components.translations import t

db = DatabaseManager()

render_topnav()
st.title(t("tunggakan"))

# --- CSS (same family as Komitmen page) ---
st.markdown("""
<style>
.tunggakan-total {
    background: linear-gradient(135deg, #c56a1f, #e08e3e);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}
.tunggakan-total .label { font-size: 14px; opacity: 0.85; }
.tunggakan-total .value { font-size: 36px; font-weight: bold; margin: 8px 0; }

.bill-item-name { font-weight: 600; font-size: 16px; }
.bill-item-due { font-size: 12px; opacity: 0.55; margin-bottom: 10px; }
.bill-item-amount { font-size: 26px; font-weight: 700; }
.bill-item-category { font-size: 12px; opacity: 0.6; }
.status-belum { color: #ff5252; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-top: 3px; margin-bottom: 12px }
</style>
""", unsafe_allow_html=True)

# --- Total at the top ---
total = db.get_total_tunggakan()
st.markdown(f"""
<div class="tunggakan-total">
    <div class="label">{t("jumlah_tunggakan_semasa")}</div>
    <div class="value">-RM {total:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# --- Add tunggakan form ---
# This is really just "add a Komitmen bill" - but framed here specifically
# for entering bills that are ALREADY overdue (backdated), or ones you
# know will become overdue soon. The due date defaults to yesterday to
# make backdating the common case, but you can pick any date.
with st.popover("➕ Add tunggakan"):
    with st.form(key="add_tunggakan_form", clear_on_submit=True):
        name = st.text_input("Bill name")
        category = st.selectbox("Category", ["Tetap", "Berubah", "Lain-lain"])
        amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
        due_date = st.date_input("Due date", value=date.today() - timedelta(days=1))
        is_recurring = st.checkbox("🔁 Repeats monthly")
        submitted = st.form_submit_button("Save")

        if submitted:
            if name.strip() == "":
                st.warning("Please enter a bill name.")
            else:
                db.add_komitmen(name, category, amount_input, due_date.isoformat(), is_recurring)
                st.success(f"{name} added!")
                st.rerun()

st.divider()

# --- List existing tunggakan items ---
items = db.get_tunggakan_items()

if not items:
    st.caption("No tunggakan right now. 🎉")

for item in items:
    edit_key = f"editing_tunggakan_{item['id']}"

    if st.session_state.get(edit_key, False):
        # ---- EDIT MODE ----
        with st.container(border=True):
            with st.form(key=f"edit_tunggakan_form_{item['id']}"):
                new_name = st.text_input("Bill name", value=item["name"])
                new_category = st.selectbox(
                    "Category", ["Tetap", "Berubah", "Lain-lain"],
                    index=["Tetap", "Berubah", "Lain-lain"].index(item["category"])
                )
                new_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01, value=item["amount"])
                new_due_date = st.date_input(
                    "Due date",
                    value=datetime.strptime(item["due_date"], "%Y-%m-%d").date()
                )
                new_recurring = st.checkbox("🔁 Repeats monthly", value=bool(item["is_recurring"]))

                save_col, cancel_col = st.columns(2)
                with save_col:
                    if st.form_submit_button("Save changes"):
                        db.update_komitmen(
                            item["id"], new_name, new_amount, new_due_date.isoformat(),
                            category=new_category, is_recurring=new_recurring
                        )
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
                recurring_badge = " 🔁" if item["is_recurring"] else ""
                st.markdown(f"""
                <div class="bill-item-name">{item['name']}{recurring_badge}</div>
                <div class="bill-item-due">Due: {item['due_date']} · {item['category']}</div>
                """, unsafe_allow_html=True)
            with amount_col:
                st.markdown(f"""
                <div class="bill-item-amount" style="text-align:right;">RM {item['amount']:,.2f}</div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="status-belum">Lewat</div>', unsafe_allow_html=True)

            paid_col, edit_col, spacer_col, delete_col = st.columns([1, 1, 1, 1])
            with paid_col:
                if st.button("Mark paid", key=f"tunggakan_paid_{item['id']}"):
                    db.update_komitmen_status(item["id"], "Selesai")
                    st.rerun()
            with edit_col:
                if st.button("Edit", key=f"tunggakan_edit_{item['id']}"):
                    st.session_state[edit_key] = True
                    st.rerun()
            with delete_col:
                if st.button("Delete", key=f"tunggakan_delete_{item['id']}"):
                    db.delete_komitmen(item["id"])
                    st.rerun()