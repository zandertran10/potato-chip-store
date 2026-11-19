"""S4 Your cart. Stories: US-303, US-304. Owner: User 2 (U2-06, U2-07)."""

from decimal import Decimal

import streamlit as st

from app.components.states import empty_state
from app.services import cart
from app.utils import pages


def _change_quantity(line_id: str, key: str) -> None:
    """Callback: save the new quantity; 0 removes the line (US-304 AC1, AC2)."""
    try:
        cart.update_qty(line_id, int(st.session_state[key]))
    except cart.CartError as error:
        st.session_state["cart_error"] = str(error)


def _remove(line_id: str) -> None:
    try:
        cart.remove_line(line_id)
    except cart.CartError as error:
        st.session_state["cart_error"] = str(error)


st.title("Your cart")

if "cart_error" in st.session_state:
    st.error(st.session_state.pop("cart_error"), icon=":material/error:")

try:
    lines = cart.get_cart()
except cart.CartError as error:
    st.error(str(error), icon=":material/cloud_off:")
    st.stop()

if not lines:
    # US-303 AC3: a friendly empty state with a way back to the shop.
    empty_state("Your cart is snack-free. Let's fix that.", action_label="Build your bag", action_page=pages.SHOP)
    st.stop()

# US-303 AC1: each line shows the chip, flavors, unit price, quantity and line total.
for line in lines:
    limit = cart.max_quantity(line.base_chip, line.flavors)
    with st.container(border=True):
        info, quantity_column, total_column = st.columns([3, 1, 1], vertical_alignment="center")
        with info:
            st.markdown(f"**{line.base_chip.name}**")
            st.markdown(" ".join(f":gray-badge[{flavor.name}]" for flavor in line.flavors))
            st.caption(f"${line.unit_price:.2f} per bag")
        with quantity_column:
            key = f"cart_qty_{line.id}"
            st.number_input(
                "Bags", min_value=0, max_value=max(limit, line.quantity), value=line.quantity, step=1,
                key=key, on_change=_change_quantity, args=(line.id, key),
                help="Set to 0 to remove this bag.",
            )
        with total_column:
            st.markdown(f"**${line.line_total:.2f}**")
            st.button("Remove", icon=":material/delete:", key=f"cart_remove_{line.id}",
                      on_click=_remove, args=(line.id,))
        # US-304 AC4: stock dropped below the quantity in the cart.
        if line.quantity > limit:
            left = f"Only {limit} left" if limit > 0 else "Sold out"
            st.warning(f"{left}. Please lower the number of bags before checking out.", icon=":material/warning:")

# US-303 AC2: number of bags and subtotal.
bags = sum(line.quantity for line in lines)
subtotal = sum((line.line_total for line in lines), Decimal(0))
with st.container(border=True):
    st.markdown(f"**{bags} bag{'s' if bags != 1 else ''}** · Subtotal **${subtotal:.2f}**")
    st.caption("Demo store: no payment needed.")
    can_check_out = all(line.quantity <= cart.max_quantity(line.base_chip, line.flavors) for line in lines)
    if st.button("Checkout", type="primary", icon=":material/shopping_bag:", disabled=not can_check_out,
                 width="stretch"):
        st.switch_page(pages.CHECKOUT)
    st.page_link(pages.SHOP, label="Keep shopping", icon=":material/storefront:")
