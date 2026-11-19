"""S3 Product detail + Build Your Bag. Stories: US-201, US-202, US-203, US-301, US-302, US-601.
Owner: User 2 (U2-01 to U2-05, U2-08).

The chip's details on the left, the Build Your Bag panel on the right.
Streamlit stacks the two columns on phones (doc 02, S3).
"""

import streamlit as st

from app.components.badges import stock_badge
from app.components.bag_builder import bag_builder
from app.components.staff_picks import staff_picks_row
from app.components.states import not_found, offline
from app.services import catalog
from app.utils import pages

chip_id = st.query_params.get("id", "")  # product cards link here with ?id=<chip id>

try:
    chip = catalog.get_base_chip(chip_id)
    if chip is not None:
        settings = catalog.get_settings()
        flavors = catalog.list_flavors()
        chips = catalog.list_base_chips()
        picks = catalog.list_staff_picks(chip.id)
except catalog.CatalogUnavailable:
    offline()
    st.stop()

if chip is None:
    # A wrong, old or hidden id (US-201 AC4).
    not_found("chip")
    st.page_link(pages.SHOP, label="See all chips", icon=":material/storefront:")
    st.stop()

details_column, builder_column = st.columns(2, gap="large")

with details_column:
    # US-201 AC1: large image, name, description, base price and stock status.
    image = catalog.image_url(chip.image_path)
    if image:
        st.image(image, alt=chip.image_alt or chip.name, width="stretch")
    else:
        with st.container(border=True, horizontal_alignment="center"):
            st.markdown("# :material/bakery_dining:")
            st.caption("Photo coming soon")

    st.title(chip.name)
    st.markdown(f"### ${chip.price:.2f}")
    st.caption("Base price. Each flavor adds a little more.")
    stock_badge(chip.stock, low_stock_threshold=settings.low_stock_threshold)
    st.markdown(chip.description)

    # US-201 AC2: chip facts. The crunch meter shows a bar AND a number, never color alone.
    with st.container(border=True):
        st.markdown(f":material/category: **Style:** {chip.style}")
        st.markdown(f":material/straighten: **Thickness:** {chip.thickness}")
        st.progress(chip.crunch_level / 3, text=f"Crunch level: {chip.crunch_level} of 3")

with builder_column:
    # US-201 AC3: the Build Your Bag panel is right here, so shoppers never leave the page.
    st.subheader("Build your bag")
    bag_builder(
        chip,
        flavors,
        max_flavors=settings.max_flavors,
        # Staff picks and Surprise me send ?flavors=id1,id2 (US-301 AC6).
        preselected_flavor_ids=[f for f in st.query_params.get("flavors", "").split(",") if f],
        all_chips=chips,
    )

# US-601 AC1: up to 3 staff pick combos for this chip; choosing one fills in the builder.
if picks:
    st.subheader("Staff picks for this chip")
    staff_picks_row(picks)
