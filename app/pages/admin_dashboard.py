"""S15 Admin: Dashboard (owner only). Stories: US-707. Owner: User 1 (U1-08)."""

import streamlit as st

from app.components.states import offline
from app.services import admin, auth, catalog

# Checked on every load, before anything is shown (owner only, NFR-SEC-06).
auth.require_role("owner")

st.caption(":material/storefront: Store Admin")
st.title("Dashboard")

try:
    stats = admin.dashboard_stats()
except (admin.AdminError, catalog.CatalogUnavailable):
    offline()
    st.stop()

# US-707 AC1: three stat tiles. Days are counted in UTC.
with st.container(horizontal=True):
    st.metric("Orders today", stats.orders_today, border=True, help="Cancelled orders don't count. UTC day.")
    st.metric("Bags sold this week", stats.bags_this_week, border=True, help="The last 7 days.")
    st.metric("Low-stock items", stats.low_stock_items, border=True,
              help="Chips and flavors at or below the low-stock level. See the Stock page.")

# US-707 AC2: top 5 flavors.
st.subheader("Top 5 flavors")
if stats.top_flavors:
    st.bar_chart(
        {"Flavor": [name for name, _ in stats.top_flavors], "Bags": [bags for _, bags in stats.top_flavors]},
        x="Flavor", y="Bags", horizontal=True, sort="-Bags",
        alt="Bar chart of the five flavors in the most bags sold",
    )
    st.caption(", ".join(f"{name}: {bags} bags" for name, bags in stats.top_flavors))
else:
    st.info("No orders yet, so no top flavors.", icon=":material/bar_chart:")
