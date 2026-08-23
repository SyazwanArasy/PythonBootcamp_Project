import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from components.topnav import render_topnav
from components.translations import t

db = DatabaseManager()

render_topnav()
st.title("Analytics")

hutang = db.get_total_hutang("saya_hutang")
komitmen = db.get_total_komitmen()
tunggakan = db.get_total_tunggakan()
pendapatan = db.get_total_pendapatan()

st.subheader("Overview")

import plotly.graph_objects as go

# Keep internal keys in Malay (used for the color lookup), but display
# translated labels on the chart itself
category_keys = ["pendapatan", "komitmen", "tunggakan", "hutang"]
category_display_labels = [t(k) for k in category_keys]

chart_data = pd.DataFrame({
    "Category": category_display_labels,
    "Amount (RM)": [pendapatan, komitmen, tunggakan, hutang]
})

# Color map now keyed by the TRANSLATED label, since that's what's
# actually in chart_data["Category"] now
color_map = {
    t("hutang"): "#E0115F",
    t("komitmen"): "#8B0000",
    t("pendapatan"): "#2E8B57",
    t("tunggakan"): "#FFBF00",
}
bar_colors = [color_map[cat] for cat in chart_data["Category"]]

fig = go.Figure(data=[
    go.Bar(
        x=chart_data["Category"],
        y=chart_data["Amount (RM)"],
        marker_color=bar_colors
    )
])
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    margin=dict(t=20, b=20, l=20, r=20)
)
st.plotly_chart(fig, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric(t("pendapatan"), f"RM {pendapatan:,.2f}")
col2.metric(t("komitmen"), f"RM {komitmen:,.2f}")
col3.metric(t("tunggakan"), f"RM {tunggakan:,.2f}")
col4.metric(t("hutang"), f"RM {hutang:,.2f}")

st.divider()

# --- Spending trend over time ---
st.subheader("Spending trend (Belanja)")
daily_totals = db.get_belanja_daily_totals()
if daily_totals:
    trend_df = pd.DataFrame([dict(row) for row in daily_totals])
    trend_df = trend_df.set_index("date_spent")
    st.line_chart(trend_df)
else:
    st.caption("No spending recorded yet.")

st.divider()

# --- Top 5 biggest expenses ---
st.subheader("Top 5 biggest expenses")
top_expenses = db.get_top_belanja(limit=5)
if top_expenses:
    for item in top_expenses:
        exp_col1, exp_col2 = st.columns([2, 1])
        with exp_col1:
            st.write(f"**{item['name']}** · {item['category']} · {item['date_spent']}")
        with exp_col2:
            st.write(f"RM {item['amount']:,.2f}")
else:
    st.caption("No expenses recorded yet.")

st.divider()

# --- Debt payoff projection ---
st.subheader("Debt payoff projection")
st.caption("Estimate how long it'll take to clear your current debt at a fixed monthly payment.")

monthly_payment = st.number_input("Monthly payment (RM)", min_value=0.0, step=50.0, value=500.0)

if monthly_payment > 0 and hutang > 0:
    months_needed = hutang / monthly_payment
    st.metric("Months to pay off", f"{months_needed:.1f} months")
    st.caption(f"Paying RM {monthly_payment:,.2f}/month clears RM {hutang:,.2f} in about {months_needed:.1f} months.")
elif hutang == 0:
    st.success("You currently have no personal debt (Saya hutang) to pay off! 🎉")
else:
    st.info("Enter a monthly payment amount above RM 0 to see a projection.")