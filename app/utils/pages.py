"""Page file paths, in one place. Use these with st.page_link and st.switch_page.

Paths are relative to app/streamlit_app.py, which is how Streamlit wants them.
Example: st.page_link(pages.PRODUCT, label="Build this bag", query_params={"id": chip.id})
"""

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
