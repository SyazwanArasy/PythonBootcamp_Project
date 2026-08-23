import streamlit as st
from database.db_manager import DatabaseManager
from datetime import date, datetime
from components.topnav import render_topnav
from components.translations import t

db = DatabaseManager()

render_topnav()
st.title(t("komitmen"))


# --- CSS matching the Dashboard's card style ---
st.markdown("""
<style>
.komitmen-total {
    background: linear-gradient(135deg, #7a1010, #b71c1c);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}
.komitmen-total .label { font-size: 14px; opacity: 0.85; }
.komitmen-total .value { font-size: 36px; font-weight: bold; margin: 8px 0; }

.bill-item-name { font-weight: 600; font-size: 16px; margin-bottom: 2px; }
.bill-item-due { font-size: 12px; opacity: 0.55; margin-bottom: 10px; }
.bill-item-amount { font-size: 26px; font-weight: 700; margin-bottom: 4px; }
.status-belum {
    color: #ff5252;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-top: 3px;
    margin-bottom: 12px
}
.status-selesai {
    color: #4caf50;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px; 
    margin-top: 3px; 
    margin-bottom: 12px
}
</style>
""", unsafe_allow_html=True)

# --- Total at the top ---
total = db.get_total_komitmen()
outstanding = db.get_total_komitmen_unpaid()
st.markdown(f"""
<div class="komitmen-total">
    <div class="label">{t("jumlah_komitmen_bulanan")}</div>
    <div class="value">-RM {total:,.2f}</div>
    <div class="label">{t("belum_dibayar")}: RM {outstanding:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# --- Three category columns: Tetap, Berubah, Lain-lain ---
# Internal category values NEVER change - these match what's stored in the
# database. Only the LABEL shown on screen gets translated.
categories = ["Tetap", "Berubah", "Lain-lain"]
category_labels = {"Tetap": t("tetap"), "Berubah": t("berubah"), "Lain-lain": t("lain_lain")}
cols = st.columns(3)

for col, category in zip(cols, categories):
    with col:
        # ---- Title row: category name + "Add bill" side by side ----
        # 👉 ADJUST HERE: change [3, 1] to control how much space the title
        # takes vs the button. Bigger first number = title takes more room,
        # pushing "Add bill" further right.
        title_col, addbtn_col = st.columns([4.5, 1])
        with title_col:
            st.subheader(category_labels[category])
        with addbtn_col:
            with st.popover("➕"):
                with st.form(key=f"add_form_{category}", clear_on_submit=True):
                    name = st.text_input("Bill name", key=f"name_{category}")
                    amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01, key=f"amount_{category}")
                    due_date = st.date_input("Due date", value=date.today(), key=f"due_{category}")
                    is_recurring = st.checkbox("🔁 Repeats monthly", key=f"recurring_{category}")
                    submitted = st.form_submit_button("Save")

                    if submitted:
                        if name.strip() == "":
                            st.warning("Please enter a bill name.")
                        else:
                            db.add_komitmen(name, category, amount_input, due_date.isoformat(), is_recurring)
                            st.success(f"{name} added!")
                            st.rerun()

        # ---- List existing bills in this category ----
        bills = db.get_komitmen_by_category(category)

        if not bills:
            st.caption("No bills yet.")

        for bill in bills:
            edit_key = f"editing_komitmen_{bill['id']}"

            if st.session_state.get(edit_key, False):
                # ---- EDIT MODE ----
                with st.container(border=True):
                    with st.form(key=f"edit_komitmen_form_{bill['id']}"):
                        new_name = st.text_input("Bill name", value=bill["name"])
                        new_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01, value=bill["amount"])
                        new_due_date = st.date_input(
                            "Due date",
                            value=datetime.strptime(bill["due_date"], "%Y-%m-%d").date()
                        )
                        new_recurring = st.checkbox("🔁 Repeats monthly", value=bool(bill["is_recurring"]))

                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.form_submit_button("Save changes"):
                                db.update_komitmen(
                                    bill["id"], new_name, new_amount, new_due_date.isoformat(),
                                    is_recurring=new_recurring
                                )
                                st.session_state[edit_key] = False
                                st.rerun()
                        with cancel_col:
                            if st.form_submit_button("Cancel"):
                                st.session_state[edit_key] = False
                                st.rerun()
            else:
                # ---- NORMAL VIEW ----
                status_class = "status-selesai" if bill["status"] == "Selesai" else "status-belum"

                with st.container(border=True):
                    info_col, amount_col = st.columns([1.4, 1])
                    with info_col:
                        recurring_badge = " 🔁" if bill["is_recurring"] else ""
                        st.markdown(f"""
                        <div class="bill-item-name">{bill['name']}{recurring_badge}</div>
                        <div class="bill-item-due">Due: {bill['due_date']}</div>
                        """, unsafe_allow_html=True)
                    with amount_col:
                        st.markdown(f"""
                        <div class="bill-item-amount" style="text-align:right;">RM {bill['amount']:,.2f}</div>
                        """, unsafe_allow_html=True)

                    st.markdown(f'<div class="{status_class}">{bill["status"]}</div>', unsafe_allow_html=True)

                    # 👉 ADJUST HERE: 4 columns now instead of 3.
                    # [paid_btn, edit_btn, spacer, delete_btn]
                    paid_col, edit_col, spacer_col, delete_col = st.columns([1.4, 1, 2, 0.8])
                    with paid_col:
                        if bill["status"] != "Selesai":
                            if st.button("Mark paid", key=f"paid_{bill['id']}"):
                                db.update_komitmen_status(bill["id"], "Selesai")
                                st.rerun()
                        else:
                            if st.button("Mark unpaid", key=f"unpaid_{bill['id']}"):
                                db.update_komitmen_status(bill["id"], "Belum bayar")
                                st.rerun()
                    with edit_col:
                        if st.button("Edit", key=f"edit_btn_komitmen_{bill['id']}"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    with delete_col:
                        if st.button("Delete", key=f"delete_{bill['id']}"):
                            db.delete_komitmen(bill["id"])
                            st.rerun()