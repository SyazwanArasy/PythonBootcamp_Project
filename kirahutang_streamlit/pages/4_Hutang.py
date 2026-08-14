import streamlit as st
from database.db_manager import DatabaseManager
from datetime import date, datetime

db = DatabaseManager()

st.title("Hutang")

# --- CSS ---
st.markdown("""
<style>
.hutang-total-red {
    background: linear-gradient(135deg, #7a1010, #b71c1c);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
}
.hutang-total-green {
    background: linear-gradient(135deg, #0d5c2f, #1b8f4c);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
}
.hutang-total .label { font-size: 14px; opacity: 0.85; }
.hutang-total .value { font-size: 36px; font-weight: bold; margin: 8px 0; }
.hutang-total .sub { font-size: 13px; opacity: 0.85; }

.hutang-item-name { font-weight: 600; font-size: 16px; }
.hutang-item-date { font-size: 12px; opacity: 0.55; margin-bottom: 10px; }
.hutang-item-amount { font-size: 26px; font-weight: 700; }
.status-belum { color: #ff5252; font-size: 12px; font-weight: 600; text-transform: uppercase; }
.status-selesai { color: #4caf50; font-size: 12px; font-weight: 600; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- Two totals at the top: Saya hutang / Orang hutang ---
saya_hutang_total = db.get_total_hutang("saya_hutang")
orang_hutang_total = db.get_total_hutang("orang_hutang")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="hutang-total-red hutang-total">
        <div class="label">Saya hutang</div>
        <div class="value">-RM {saya_hutang_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="hutang-total-green hutang-total">
        <div class="label">Orang hutang</div>
        <div class="value">RM {orang_hutang_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")  # small spacing gap

# --- Two sections: "Hutang kepada" (I owe) and "Peminjam" (owed to me) ---
sections = [
    ("Hutang kepada", "saya_hutang"),
    ("Peminjam", "orang_hutang"),
]

list_col1, list_col2 = st.columns(2)
list_cols = [list_col1, list_col2]

for col, (label, direction) in zip(list_cols, sections):
    with col:
        title_col, addbtn_col = st.columns([3, 1])
        with title_col:
            st.subheader(label)
        with addbtn_col:
            with st.popover("➕"):
                with st.form(key=f"add_hutang_form_{direction}", clear_on_submit=True):
                    name = st.text_input("Name", key=f"hutang_name_{direction}")
                    amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01, key=f"hutang_amount_{direction}")
                    date_recorded = st.date_input("Date", value=date.today(), key=f"hutang_date_{direction}")
                    submitted = st.form_submit_button("Save")

                    if submitted:
                        if name.strip() == "":
                            st.warning("Please enter a name.")
                        else:
                            db.add_hutang(name, direction, amount_input, date_recorded.isoformat())
                            st.success(f"{name} added!")
                            st.rerun()

        entries = db.get_hutang_by_direction(direction)

        if not entries:
            st.caption("No entries yet.")

        for entry in entries:
            edit_key = f"editing_hutang_{entry['id']}"

            if st.session_state.get(edit_key, False):
                # ---- EDIT MODE ----
                with st.container(border=True):
                    with st.form(key=f"edit_hutang_form_{entry['id']}"):
                        new_name = st.text_input("Name", value=entry["name"])
                        new_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01, value=entry["amount"])
                        new_date = st.date_input(
                            "Date",
                            value=datetime.strptime(entry["date_recorded"], "%Y-%m-%d").date()
                        )

                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.form_submit_button("Save changes"):
                                db.update_hutang(entry["id"], new_name, new_amount, new_date.isoformat())
                                st.session_state[edit_key] = False
                                st.rerun()
                        with cancel_col:
                            if st.form_submit_button("Cancel"):
                                st.session_state[edit_key] = False
                                st.rerun()
            else:
                # ---- NORMAL VIEW ----
                status_class = "status-selesai" if entry["status"] == "Selesai" else "status-belum"

                with st.container(border=True):
                    info_col, amount_col = st.columns([1.4, 1])
                    with info_col:
                        st.markdown(f"""
                        <div class="hutang-item-name">{entry['name']}</div>
                        <div class="hutang-item-date">{entry['date_recorded']}</div>
                        """, unsafe_allow_html=True)
                    with amount_col:
                        st.markdown(f"""
                        <div class="hutang-item-amount" style="text-align:right;">RM {entry['amount']:,.2f}</div>
                        """, unsafe_allow_html=True)

                    st.markdown(f'<div class="{status_class}">{entry["status"]}</div>', unsafe_allow_html=True)

                    paid_col, edit_col, spacer_col, delete_col = st.columns([1.4, 1.4, 3.5, 1.2])
                    with paid_col:
                        if entry["status"] != "Selesai":
                            if st.button("Mark paid", key=f"hutang_paid_{entry['id']}"):
                                db.update_hutang_status(entry["id"], "Selesai")
                                st.rerun()
                        else:
                            if st.button("Mark unpaid", key=f"hutang_unpaid_{entry['id']}"):
                                db.update_hutang_status(entry["id"], "Belum bayar")
                                st.rerun()
                    with edit_col:
                        if st.button("Edit", key=f"hutang_edit_{entry['id']}"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    with delete_col:
                        if st.button("Delete", key=f"hutang_delete_{entry['id']}"):
                            db.delete_hutang(entry["id"])
                            st.rerun()