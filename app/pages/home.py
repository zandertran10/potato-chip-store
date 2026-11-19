"""S1 Home. Stories: US-101, US-601, US-602. Owner: User 1 (U1-03, U1-07), User 2 (U2-08)."""

import streamlit as st

from app.components.flavor_tile import flavor_tile
from app.components.product_card import product_card
from app.components.staff_picks import staff_picks_row
from app.components.states import offline
from app.services import catalog
from app.utils import pages

try:
    settings = catalog.get_settings()
    featured = catalog.featured_chips()
    picks = catalog.list_staff_picks()
    flavors = [flavor for flavor in catalog.list_flavors() if flavor.stock > 0]
except catalog.CatalogUnavailable:
    offline()
    st.stop()

# Hero: one main action (doc 02 principle 4).
st.title("Build your own bag of chips")
st.markdown("Home-made, organic potato chips. You pick the chip, you pick the flavors.")
with st.container(horizontal=True):
    if st.button("Build your bag", type="primary", icon=":material/bakery_dining:"):
        st.switch_page(pages.SHOP)
    if st.button("Browse flavors", icon=":material/category:"):
        st.switch_page(pages.SHOP)

# How it works in 3 steps (US-101 AC2).
st.subheader("How it works")
for column, (icon, title, text) in zip(
    st.columns(3),
    (
        (":material/looks_one:", "Pick your chip", "Thin, kettle, wavy or sweet potato."),
        (":material/looks_two:", f"Add up to {settings.max_flavors} flavors", "Mix salty, tangy, sweet and spicy."),
        (":material/looks_3:", "Crunch", "We pack your bag by hand."),
    ),
    strict=True,
):
    with column, st.container(border=True):
        st.markdown(f"### {icon}")
        st.markdown(f"**{title}**")
        st.caption(text)

# Featured chips, chosen by staff (US-101 AC3).
if featured:
    st.subheader("Featured chips")
    for column, chip in zip(st.columns(len(featured)), featured, strict=True):
        with column:
            product_card(chip, low_stock_threshold=settings.low_stock_threshold)

# Staff picks and Surprise me (US-601, US-602): curiosity without pressure.
st.subheader("Not sure? Try one of these")
staff_picks_row(picks)
if st.button("Surprise me", icon=":material/casino:", help="Picks a random chip and flavors. You can still change them."):
    try:
        chip_id, flavor_ids = catalog.random_combo()
    except catalog.CatalogUnavailable:
        st.warning("Nothing is in stock right now. Back soon!", icon=":material/hourglass_empty:")
    else:
        st.switch_page(pages.PRODUCT, query_params={"id": chip_id, "flavors": ",".join(flavor_ids)})

# A row of flavor tiles that leads to the flavor library (US-101 AC4).
if flavors:
    st.subheader("Flavors to try")
    shown = flavors[:4]
    for column, flavor in zip(st.columns(len(shown)), shown, strict=True):
        with column:
            flavor_tile(flavor, key=f"home_flavor_{flavor.id}", selectable=False)
    st.page_link(pages.SHOP, label="See every flavor", icon=":material/arrow_forward:")
