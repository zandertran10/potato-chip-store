"""S2 Shop / Search results. Stories: US-102, US-103, US-104, US-105. Owner: User 1 (U1-01, U1-02, U1-04, U1-05)."""

import re

import streamlit as st

from app.components.flavor_tile import flavor_tile
from app.components.product_card import product_card
from app.components.search_filters import search_filters
from app.components.states import offline
from app.models.catalog import FLAVOR_FAMILIES, SORT_OPTIONS
from app.services import catalog

CHIP_COLUMNS = 3  # on phones Streamlit stacks them into one column (US-102)
FLAVOR_COLUMNS = 4


def _plain(text: str) -> str:
    """Show what the shopper typed as plain text, not as Markdown (NFR-SEC-15)."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>~<:])", r"\\\1", text)


def _grid(items, columns: int, draw) -> None:
    for start in range(0, len(items), columns):
        for column, item in zip(st.columns(columns), items[start : start + columns], strict=False):
            with column:
                draw(item)


st.title("Shop")

try:
    settings = catalog.get_settings()
    styles = sorted({chip.style for chip in catalog.list_base_chips()})
except catalog.CatalogUnavailable:
    offline()
    st.stop()

# bind="query-params" keeps the search word and sort in the link (?q=bbq&sort=name),
# so the header search and shared links open the same results (US-103, US-105).
search_column, sort_column = st.columns([3, 1], vertical_alignment="bottom")
with search_column:
    query = st.text_input(
        "Search chips and flavors", key="q", bind="query-params", placeholder="Try bbq, lime or kettle"
    )
with sort_column:
    sort = st.selectbox(
        "Sort by", list(SORT_OPTIONS), format_func=SORT_OPTIONS.get, key="sort", bind="query-params"
    )
filters = search_filters(styles=styles, families=FLAVOR_FAMILIES)

try:
    results = catalog.search(query, filters, sort)
except catalog.CatalogUnavailable:
    offline()
    st.stop()

if query.strip():
    count = results.count
    st.markdown(f"**{count} result{'s' if count != 1 else ''}** for “{_plain(query.strip())}”")

if results.count == 0:
    # US-103 AC4: a friendly message and some suggestions.
    st.info("No chips or flavors match that. Try another word, or clear the filters.", icon=":material/search_off:")
    st.subheader("You might like")
    try:
        suggestions = catalog.featured_chips()
    except catalog.CatalogUnavailable:
        suggestions = []
    _grid(suggestions, CHIP_COLUMNS, lambda chip: product_card(chip, low_stock_threshold=settings.low_stock_threshold))
    st.stop()

if results.chips:
    st.subheader("Chips")
    _grid(results.chips, CHIP_COLUMNS, lambda chip: product_card(chip, low_stock_threshold=settings.low_stock_threshold))

if results.flavors:
    st.subheader("Flavor library")
    st.caption("Pick these on a chip's page when you build your bag.")
    _grid(
        results.flavors,
        FLAVOR_COLUMNS,
        lambda flavor: flavor_tile(flavor, key=f"library_{flavor.id}", selectable=False),
    )
