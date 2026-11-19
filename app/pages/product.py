"""S3 Build your bag. Stories: US-201, US-202, US-203, US-301, US-302, US-601. Owner: User 2 (U2-01 to U2-05, U2-08).

US-201 (U2-01): the chip's details on the left, the Build Your Bag panel on the
right. Streamlit stacks the two columns on phones (doc 02, S3).
"""

import streamlit as st

from app.components.badges import stock_badge
from app.components.bag_builder import bag_builder
from app.components.states import not_found, offline
from app.models.catalog import Flavor, StoreSettings
from app.services import catalog
from app.utils import pages


def _store_settings() -> StoreSettings:
    """The real settings once US-706 builds get_settings(); the defaults until then."""
    try:
        return catalog.get_settings()
    except NotImplementedError:
        return StoreSettings()


def _flavors() -> list[Flavor]:
    """All flavors once US-102 builds list_flavors(); none until then."""
    try:
        return catalog.list_flavors()
    except NotImplementedError:
        return []


chip_id = st.query_params.get("id", "")  # product cards link here with ?id=<chip id>

try:
    chip = catalog.get_base_chip(chip_id)
except catalog.CatalogUnavailable:
    offline()
    st.stop()

if chip is None:
    # A wrong, old or hidden id (US-201 AC4).
    not_found("chip")
    st.page_link(pages.SHOP, label="See all chips", icon=":material/storefront:")
    st.stop()

settings = _store_settings()
details_column, builder_column = st.columns(2, gap="large")

with details_column:
    # AC1: large image, name, description, base price and stock status.
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

    # AC2: chip facts. The crunch meter shows a bar AND a number, never color alone.
    with st.container(border=True):
        st.markdown(f":material/category: **Style:** {chip.style}")
        st.markdown(f":material/straighten: **Thickness:** {chip.thickness}")
        st.progress(chip.crunch_level / 3, text=f"Crunch level: {chip.crunch_level} of 3")

with builder_column:
    # AC3: the Build Your Bag panel lives right here, so shoppers never leave the page.
    st.subheader("Build your bag")
    bag_builder(
        chip,
        _flavors(),
        max_flavors=settings.max_flavors,
        # Staff picks and Surprise me send ?flavors=id1,id2 (US-301 AC6).
        preselected_flavor_ids=[f for f in st.query_params.get("flavors", "").split(",") if f],
    )
