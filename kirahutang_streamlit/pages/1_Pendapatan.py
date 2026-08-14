import streamlit as st
from database.db_manager import DatabaseManager

db = DatabaseManager()

st.title("Pendapatan")

# --- CSS (same style family as Komitmen page) ---
st.markdown("""
<style>
.pendapatan-total {
    background: linear-gradient(135deg, #0d5c2f, #1b8f4c);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}
.pendapatan-total .label { font-size: 14px; opacity: 0.85; }
.pendapatan-total .value { font-size: 36px; font-weight: bold; margin: 8px 0; }

.income-item-name { font-weight: 600; font-size: 16px; }
.income-item-amount { font-size: 26px; font-weight: 700; text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- Total at the top ---
total = db.get_total_pendapatan()
st.markdown(f"""
<div class="pendapatan-total">
    <div class="label">Jumlah pendapatan</div>
    <div class="value">RM {total:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# --- Three category columns: Tetap, Tambahan, Lain-lain ---
categories = ["Tetap", "Tambahan", "Lain-lain"]
cols = st.columns(3)

for col, category in zip(cols, categories):
    with col:
        # ---- Title row: category name + "Add" side by side ----
        title_col, addbtn_col = st.columns([4.5, 1])
        with title_col:
            st.subheader(category)
        with addbtn_col:
            with st.popover("➕"):
                with st.form(key=f"add_income_form_{category}", clear_on_submit=True):
                    name = st.text_input("Source name", key=f"income_name_{category}")
                    amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01, key=f"income_amount_{category}")
                    submitted = st.form_submit_button("Save")

                    if submitted:
                        if name.strip() == "":
                            st.warning("Please enter a name.")
                        else:
                            db.add_pendapatan(name, category, amount_input)
                            st.success(f"{name} added!")
                            st.rerun()

        # ---- List existing income entries ----
        entries = db.get_pendapatan_by_category(category)

        if not entries:
            st.caption("No entries yet.")

        for entry in entries:
            edit_key = f"editing_{entry['id']}"

            # Check if this specific entry is currently in "edit mode"
            if st.session_state.get(edit_key, False):
                # ---- EDIT MODE: show an inline form to update this entry ----
                with st.container(border=True):
                    with st.form(key=f"edit_form_{entry['id']}"):
                        new_name = st.text_input("Source name", value=entry["name"])
                        new_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01, value=entry["amount"])

                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.form_submit_button("Save changes"):
                                db.update_pendapatan(entry["id"], new_name, new_amount)
                                st.session_state[edit_key] = False
                                st.rerun()
                        with cancel_col:
                            if st.form_submit_button("Cancel"):
                                st.session_state[edit_key] = False
                                st.rerun()
            else:
                # ---- NORMAL VIEW: show the entry with Edit/Delete buttons ----
                with st.container(border=True):
                    info_col, amount_col = st.columns([1, 1])
                    with info_col:
                        st.markdown(f'<div class="income-item-name">{entry["name"]}</div>', unsafe_allow_html=True)
                    with amount_col:
                        st.markdown(f'<div class="income-item-amount">RM {entry["amount"]:,.2f}</div>', unsafe_allow_html=True)

                    edit_col, spacer_col, delete_col = st.columns([1, 3, 1])
                    with edit_col:
                        if st.button("Edit", key=f"edit_btn_{entry['id']}"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    with delete_col:
                        if st.button("Delete", key=f"delete_income_{entry['id']}"):
                            db.delete_pendapatan(entry["id"])
                            st.rerun()