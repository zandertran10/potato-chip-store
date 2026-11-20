"""S11 Admin: Base chips. Stories: US-701. Owner: User 3 (U3-03)."""

import dataclasses
from decimal import Decimal

import streamlit as st

from app.components.states import offline
from app.models.catalog import BaseChip
from app.services import admin, auth, catalog

COMMON_ALLERGENS = ["gluten", "milk", "mustard", "nuts", "sesame", "soy"]
NEW = ""  # the "Add new" choice

# Checked on every load, before anything is shown (staff and owner only, NFR-SEC-06).
auth.require_role("staff", "owner")

st.caption(":material/storefront: Store Admin")
st.title("Base chips")

if "admin_chips_msg" in st.session_state:
    st.success(st.session_state.pop("admin_chips_msg"), icon=":material/check_circle:")

try:
    chips = catalog.list_base_chips(include_inactive=True)
except catalog.CatalogUnavailable:
    offline()
    st.stop()

# A searchable table (doc 02, S11).
search = st.text_input("Search chips", placeholder="Name or style")
shown = [c for c in chips if search.lower() in c.name.lower() or search.lower() in c.style.lower()]
st.dataframe(
    [{"Photo": catalog.image_url(c.image_path), "Name": c.name, "Style": c.style, "Price": f"${c.price:.2f}",
      "Stock": c.stock, "Shown in shop": c.is_active, "Featured": c.is_featured} for c in shown],
    # A small picture of each chip (doc 02 S11); empty when it has no photo yet.
    column_config={"Photo": st.column_config.ImageColumn("Photo", width="small")},
    hide_index=True, alt="Table of base chips with photo, price, stock and whether they are shown in the shop",
)

by_id = {c.id: c for c in chips}
choice = st.selectbox("Add or edit", [NEW, *by_id], format_func=lambda cid: by_id[cid].name if cid else "Add a new chip")
chip = by_id.get(choice) or BaseChip(id="", name="", description="", style="", thickness="Regular",
                                     crunch_level=2, price=Decimal("2.50"), stock=0)

with st.form(f"chip_form_{choice or 'new'}"):
    name = st.text_input("Name", value=chip.name, max_chars=60)
    description = st.text_area("Description", value=chip.description, max_chars=500)
    left, right = st.columns(2)
    style = left.text_input("Style", value=chip.style, max_chars=30, placeholder="Classic, Kettle, Wavy...")
    thickness = right.text_input("Thickness", value=chip.thickness, max_chars=30)
    crunch = left.slider("Crunch level", 0, 3, value=chip.crunch_level)
    price = right.number_input("Price ($)", min_value=0.01, max_value=99.99, value=float(chip.price), step=0.05,
                               format="%.2f")
    if chip.id:
        st.caption(f"Stock: {chip.stock}. Change it on the Stock page, so every change is recorded.")
        stock = chip.stock
    else:
        stock = int(st.number_input("Starting stock", min_value=0, max_value=100000, value=0, step=1))
    allergens = st.multiselect("Allergens", sorted(set(COMMON_ALLERGENS) | set(chip.allergens)),
                               default=list(chip.allergens), accept_new_options=True)
    featured = st.checkbox("Featured on the home page", value=chip.is_featured)
    # US-701 AC3: JPG, PNG or WebP, 2 MB or smaller. Supabase checks this too.
    upload = st.file_uploader("Image (JPG, PNG or WebP, up to 2 MB)", type=["jpg", "jpeg", "png", "webp"])
    if chip.image_path and not upload:
        st.image(catalog.image_url(chip.image_path), alt=chip.image_alt or chip.name, width=200)
    image_alt = st.text_input("Image alt text (describe the photo)", value=chip.image_alt or "", max_chars=150)
    saved = st.form_submit_button("Save chip", type="primary", icon=":material/save:")

if saved:
    try:
        image_path = chip.image_path
        if upload is not None:
            st.image(upload, alt="Preview of the uploaded image", width=200)
            image_path = admin.upload_image(upload.name, upload.getvalue(), upload.type or "")
        result = admin.save_base_chip(dataclasses.replace(
            chip, name=name, description=description, style=style, thickness=thickness, crunch_level=crunch,
            price=Decimal(str(round(price, 2))), stock=stock, allergens=tuple(allergens), is_featured=featured,
            image_path=image_path, image_alt=image_alt,
        ))
    except admin.AdminError as error:
        st.error(str(error), icon=":material/error:")
    else:
        st.session_state["admin_chips_msg"] = f"Saved {result.name}."
        st.rerun()

# US-701 AC4: hide instead of delete, after a confirmation step.
if chip.id:
    st.divider()
    action = "Hide from the shop" if chip.is_active else "Show in the shop again"
    sure = st.checkbox(f"Yes, {action.lower()}: {chip.name}", key=f"confirm_hide_{chip.id}")
    if st.button(action, icon=":material/visibility_off:" if chip.is_active else ":material/visibility:",
                 disabled=not sure):
        try:
            admin.save_base_chip(dataclasses.replace(chip, is_active=not chip.is_active))
        except admin.AdminError as error:
            st.error(str(error), icon=":material/error:")
        else:
            st.session_state["admin_chips_msg"] = f"{chip.name} is now {'hidden' if chip.is_active else 'shown'}."
            st.rerun()
