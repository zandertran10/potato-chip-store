"""Page file paths, in one place. Use these with st.page_link and st.switch_page.

Paths are relative to app/streamlit_app.py, which is how Streamlit wants them.
Example: st.page_link(pages.PRODUCT, label="Build this bag", query_params={"id": chip.id})
"""

from urllib.parse import urlsplit

import streamlit as st

HOME = "pages/home.py"
SHOP = "pages/shop.py"
PRODUCT = "pages/product.py"
CART = "pages/cart.py"
CHECKOUT = "pages/checkout.py"
CONFIRMATION = "pages/confirmation.py"
SIGN_IN = "pages/sign_in.py"
REGISTER = "pages/register.py"
RESET_PASSWORD = "pages/reset_password.py"
MY_ACCOUNT = "pages/my_account.py"
ADMIN_CHIPS = "pages/admin_chips.py"
ADMIN_FLAVORS = "pages/admin_flavors.py"
ADMIN_STOCK = "pages/admin_stock.py"
ADMIN_ORDERS = "pages/admin_orders.py"
ADMIN_STAFF = "pages/admin_staff.py"
ADMIN_SETTINGS = "pages/admin_settings.py"
ADMIN_DASHBOARD = "pages/admin_dashboard.py"

ALL_PAGES = (
    HOME, SHOP, PRODUCT, CART, CHECKOUT, CONFIRMATION, SIGN_IN, REGISTER, RESET_PASSWORD, MY_ACCOUNT,
    ADMIN_CHIPS, ADMIN_FLAVORS, ADMIN_STOCK, ADMIN_ORDERS, ADMIN_STAFF, ADMIN_SETTINGS, ADMIN_DASHBOARD,
)
# Streamlit names each page's address after its file: pages/checkout.py -> /checkout.
_BY_URL_PATH = {path.removeprefix("pages/").removesuffix(".py"): path for path in ALL_PAGES}
# Never send someone back to these after signing in.
_NOT_A_RETURN_PAGE = {"sign_in", "register", "reset_password"}


def page_for(url_path: str | None) -> str | None:
    """The page file for an address like "checkout", or None if it isn't one of ours.

    Used for ?next= after sign-in (US-502 AC3). Only our own pages are accepted,
    so a crafted link can't send people anywhere else.
    """
    if not url_path or url_path in _NOT_A_RETURN_PAGE:
        return None
    return _BY_URL_PATH.get(url_path.strip("/"))


def current_url_path() -> str:
    """The current page's address, e.g. "checkout" ("" for the home page)."""
    url = getattr(st.context, "url", None) or ""
    return urlsplit(url).path.strip("/").split("/")[-1]
