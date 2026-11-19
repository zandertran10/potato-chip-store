"""S15 Admin: Store settings (owner only). Stories: US-706. Owner: User 1 (U1-06)."""

import dataclasses

import streamlit as st

from app.components.states import offline
from app.models.catalog import StoreSettings
from app.services import admin, auth, catalog

# Checked on every load, before anything is shown (owner only, NFR-SEC-06).
auth.require_role("owner")

st.caption(":material/storefront: Store Admin")
st.title("Store settings")

if "admin_settings_msg" in st.session_state:
    st.success(st.session_state.pop("admin_settings_msg"), icon=":material/check_circle:")

try:
    settings = catalog.get_settings()
    chips = catalog.list_base_chips()
except catalog.CatalogUnavailable:
    offline()
    st.stop()

names = {c.id: c.name for c in chips}
with st.form("settings_form"):
    max_flavors = st.number_input("Maximum flavors per bag", min_value=1, max_value=5, value=settings.max_flavors,
                                  step=1)
    threshold = st.number_input("Low-stock level", min_value=0, max_value=10000, value=settings.low_stock_threshold,
                                step=1, help="Items at or below this show 'Few left' and are marked on the Stock page.")
    from_email = st.text_input("'From' email address", value=settings.from_email, max_chars=254)
    featured = st.multiselect("Featured chips (home page, 3 or 4 is best)", list(names), format_func=names.get,
                              default=[c.id for c in chips if c.is_featured])
    saved = st.form_submit_button("Save settings", type="primary", icon=":material/save:")

if saved:
    try:
        admin.save_settings(StoreSettings(int(max_flavors), int(threshold), from_email))
        # Featured chips are a flag on each chip, so only changed chips are saved.
        for chip in chips:
            wanted = chip.id in featured
            if chip.is_featured != wanted:
                admin.save_base_chip(dataclasses.replace(chip, is_featured=wanted))
    except admin.AdminError as error:
        st.error(str(error), icon=":material/error:")
    else:
        # US-706 AC2: changes take effect right away (every page reads them fresh).
        st.session_state["admin_settings_msg"] = "Settings saved. They apply right away."
        st.rerun()
