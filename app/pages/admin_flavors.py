"""S12 Admin: Flavors and staff picks. Stories: US-702. Owner: User 3 (U3-04)."""

import dataclasses
from decimal import Decimal

import streamlit as st

from app.components.states import offline
from app.models.catalog import FLAVOR_FAMILIES, Flavor
from app.services import admin, auth, catalog

COMMON_ALLERGENS = ["gluten", "milk", "mustard", "nuts", "sesame", "soy"]
NEW = ""

# Checked on every load, before anything is shown (staff and owner only, NFR-SEC-06).
auth.require_role("staff", "owner")

st.caption(":material/storefront: Store Admin")
st.title("Flavors and staff picks")

if "admin_flavors_msg" in st.session_state:
    st.success(st.session_state.pop("admin_flavors_msg"), icon=":material/check_circle:")

try:
    flavors = catalog.list_flavors(include_inactive=True)
    chips = catalog.list_base_chips()
except catalog.CatalogUnavailable:
    offline()
    st.stop()

flavors_tab, picks_tab = st.tabs(["Flavors", "Staff picks"])

with flavors_tab:
    search = st.text_input("Search flavors", placeholder="Name or family")
    shown = [f for f in flavors if search.lower() in f.name.lower() or search.lower() in f.family.lower()]
    st.dataframe(
        [{"Name": f.name, "Family": f.family, "Price": f"${f.price:.2f}", "Stock": f.stock,
          "Heat": f.heat, "Shown in shop": f.is_active} for f in shown],
        hide_index=True, alt="Table of flavors with family, price, stock, heat and whether they are shown",
    )
    by_id = {f.id: f for f in flavors}
    choice = st.selectbox("Add or edit", [NEW, *by_id],
                          format_func=lambda fid: by_id[fid].name if fid else "Add a new flavor")
    flavor = by_id.get(choice) or Flavor(id="", name="", description="", family=FLAVOR_FAMILIES[0], salty=0,
                                         tangy=0, sweet=0, heat=0, price=Decimal("0.50"), stock=0)

    with st.form(f"flavor_form_{choice or 'new'}"):
        name = st.text_input("Name", value=flavor.name, max_chars=60)
        description = st.text_area("Description", value=flavor.description, max_chars=500)
        left, right = st.columns(2)
        family = left.selectbox("Family", FLAVOR_FAMILIES, index=FLAVOR_FAMILIES.index(flavor.family))
        price = right.number_input("Add-on price ($)", min_value=0.01, max_value=9.99, value=float(flavor.price),
                                   step=0.05, format="%.2f")
        st.markdown("**Taste profile** (0 to 3)")
        scores = st.columns(4)
        salty = scores[0].slider("Salty", 0, 3, value=flavor.salty)
        tangy = scores[1].slider("Tangy", 0, 3, value=flavor.tangy)
        sweet = scores[2].slider("Sweet", 0, 3, value=flavor.sweet)
        heat = scores[3].slider("Heat", 0, 3, value=flavor.heat)
        allergens = st.multiselect("Allergens", sorted(set(COMMON_ALLERGENS) | set(flavor.allergens)),
                                   default=list(flavor.allergens), accept_new_options=True)
        icon = st.text_input("Icon (an emoji, optional)", value=flavor.icon or "", max_chars=10)
        if flavor.id:
            st.caption(f"Stock: {flavor.stock}. Change it on the Stock page, so every change is recorded.")
            stock = flavor.stock
        else:
            stock = int(st.number_input("Starting stock", min_value=0, max_value=100000, value=0, step=1))
        saved = st.form_submit_button("Save flavor", type="primary", icon=":material/save:")

    if saved:
        try:
            result = admin.save_flavor(dataclasses.replace(
                flavor, name=name, description=description, family=family, salty=salty, tangy=tangy,
                sweet=sweet, heat=heat, price=Decimal(str(round(price, 2))), stock=stock,
                allergens=tuple(allergens), icon=icon,
            ))
        except admin.AdminError as error:
            st.error(str(error), icon=":material/error:")
        else:
            st.session_state["admin_flavors_msg"] = f"Saved {result.name}."
            st.rerun()

    if flavor.id:
        st.divider()
        action = "Hide from the shop" if flavor.is_active else "Show in the shop again"
        sure = st.checkbox(f"Yes, {action.lower()}: {flavor.name}", key=f"confirm_hide_flavor_{flavor.id}")
        if st.button(action, disabled=not sure,
                     icon=":material/visibility_off:" if flavor.is_active else ":material/visibility:"):
            try:
                admin.save_flavor(dataclasses.replace(flavor, is_active=not flavor.is_active))
            except admin.AdminError as error:
                st.error(str(error), icon=":material/error:")
            else:
                st.session_state["admin_flavors_msg"] = f"{flavor.name} is now {'hidden' if flavor.is_active else 'shown'}."
                st.rerun()

with picks_tab:
    # US-702 AC3: up to 3 staff picks per base chip.
    if not chips:
        st.info("Add a base chip first.", icon=":material/info:")
        st.stop()
    chip_names = {c.id: c.name for c in chips}
    chip_id = st.selectbox("Base chip", list(chip_names), format_func=chip_names.get)
    try:
        existing = {pick.position: pick for pick in catalog.list_staff_picks(chip_id)}
    except catalog.CatalogUnavailable:
        offline()
        st.stop()
    active_flavors = {f.id: f.name for f in flavors if f.is_active}
    st.caption("Leave the flavors empty to remove a pick.")
    for position in (1, 2, 3):
        pick = existing.get(position)
        with st.form(f"pick_{chip_id}_{position}"):
            st.markdown(f"**Staff pick {position}**")
            title = st.text_input("Title", value=pick.title if pick else "", max_chars=60, key=f"pt_{chip_id}_{position}")
            chosen = st.multiselect("Flavors (1 to 3)", list(active_flavors), format_func=active_flavors.get,
                                    default=[f for f in (pick.flavor_ids if pick else ()) if f in active_flavors],
                                    max_selections=3, key=f"pf_{chip_id}_{position}")
            if st.form_submit_button("Save pick", icon=":material/save:"):
                try:
                    admin.save_staff_pick(chip_id, position, title, chosen)
                except admin.AdminError as error:
                    st.error(str(error), icon=":material/error:")
                else:
                    st.session_state["admin_flavors_msg"] = f"Staff pick {position} saved."
                    st.rerun()
