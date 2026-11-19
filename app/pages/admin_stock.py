"""S13 Admin: Stock. Stories: US-703. Owner: User 3 (U3-05)."""

import streamlit as st

from app.components.states import offline
from app.services import admin, auth, catalog

# Checked on every load, before anything is shown (staff and owner only, NFR-SEC-06).
auth.require_role("staff", "owner")

st.caption(":material/storefront: Store Admin")
st.title("Stock")

if "admin_stock_msg" in st.session_state:
    st.success(st.session_state.pop("admin_stock_msg"), icon=":material/check_circle:")

try:
    threshold = catalog.get_settings().low_stock_threshold
    items = [("base", c) for c in catalog.list_base_chips(include_inactive=True)]
    items += [("flavor", f) for f in catalog.list_flavors(include_inactive=True)]
except catalog.CatalogUnavailable:
    offline()
    st.stop()

stock_tab, history_tab = st.tabs(["Stock levels", "History"])

with stock_tab:
    # US-703 AC1-2: every chip and flavor; low stock gets an icon AND words, not only a color.
    rows = [
        {
            "Status": "⚠ Low" if item.stock <= threshold else "OK",
            "Type": "Chip" if kind == "base" else "Flavor",
            "Name": item.name + ("" if item.is_active else " (hidden)"),
            "Stock": item.stock,
        }
        for kind, item in items
    ]
    st.caption(f"Items at or below {threshold} are marked ⚠ Low. Edit the Stock column, then save with a reason.")
    edited = st.data_editor(
        rows, hide_index=True, key="stock_editor", disabled=["Status", "Type", "Name"],
        column_config={"Stock": st.column_config.NumberColumn("Stock", min_value=0, step=1, format="%d")},
        alt="Editable table of stock levels for every chip and flavor",
    )
    changes = [
        (kind, item, int(new["Stock"]))
        for (kind, item), new in zip(items, edited, strict=True)
        if new["Stock"] is not None and int(new["Stock"]) != item.stock
    ]
    reason = st.text_input("Reason for the change (required)", max_chars=200,
                           placeholder="Restocked from the kitchen, stock count, damaged bags...")
    if changes:
        st.caption("Changes: " + ", ".join(f"{item.name} {item.stock} → {new}" for _, item, new in changes))
    if st.button("Save stock changes", type="primary", icon=":material/save:",
                 disabled=not changes or not reason.strip()):
        saved = 0
        for kind, item, new in changes:
            try:
                admin.set_stock(kind, item.id, new, reason)
                saved += 1
            except admin.AdminError as error:
                st.error(f"{item.name}: {error}", icon=":material/error:")
        if saved == len(changes):
            st.session_state.pop("stock_editor", None)
            st.session_state["admin_stock_msg"] = f"Saved {saved} stock change{'s' if saved != 1 else ''}."
            st.rerun()

with history_tab:
    # US-703 AC4: who changed what, when, by how much and why.
    try:
        history = admin.stock_history()
    except (admin.AdminError, catalog.CatalogUnavailable):
        offline()
        st.stop()
    if not history:
        st.info("No stock changes yet.", icon=":material/history:")
    else:
        st.dataframe(
            [{"When (UTC)": f"{h.created_at:%d %b %Y %H:%M}", "Item": h.item_name,
              "Change": f"{h.change:+d}", "Reason": h.reason, "By": h.changed_by_name or "-"} for h in history],
            hide_index=True, alt="Table of recent stock changes",
        )
