"""S15 Admin: Dashboard (owner only). Stories: US-707. Owner: User 1 (U1-08).

Two tabs: the store's numbers (US-707), and the Activity log of who changed
what (NFR-LOG-02, migration 13).
"""

import json

import streamlit as st

from app.components.states import offline
from app.services import admin, auth, catalog

# Checked on every load, before anything is shown (owner only, NFR-SEC-06).
auth.require_role("owner")

st.caption(":material/storefront: Store Admin")
st.title("Dashboard")

overview_tab, activity_tab = st.tabs(["Overview", "Activity"])

with overview_tab:
    try:
        stats = admin.dashboard_stats()
    except (admin.AdminError, catalog.CatalogUnavailable):
        offline()
    else:
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

with activity_tab:
    # Who changed what, newest first. Stock changes are on the Stock page's History tab.
    try:
        entries = admin.audit_entries()
    except admin.AuditLogMissing:
        st.info("The activity log isn't set up yet. Run `supabase/migrations/20261119000013_audit_log.sql` "
                "in the Supabase SQL Editor.", icon=":material/history:")
    except admin.AdminError as error:
        st.error(str(error), icon=":material/error:")
    else:
        if not entries:
            st.info("Nothing recorded yet. Changes to chips, flavors, staff picks, orders, roles and "
                    "settings will show up here.", icon=":material/history:")
        else:
            st.caption("The last 200 changes, newest first. Stock changes are on the Stock page's History tab.")
            st.dataframe(
                [
                    {
                        "When (UTC)": f"{e.created_at:%d %b %Y %H:%M}",
                        "Who": e.actor_name + (f" ({e.actor_role})" if e.actor_role else ""),
                        "What": e.summary,
                        "Details": json.dumps(e.changes, ensure_ascii=False) if e.changes else "",
                    }
                    for e in entries
                ],
                hide_index=True,
                alt="Table of recent changes to the store: when, who, and what changed",
            )
