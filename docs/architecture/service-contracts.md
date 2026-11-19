# Service contracts

Every service function the stories need, with its owner. The foundation (Prompt E) created them all with final signatures; **stubs** raise `NotImplementedError` until their story fills them in.

**Rules**
- Pages call services; pages never call Supabase directly (CLAUDE.md layers).
- A story fills in its function **without changing the signature**. If a signature turns out wrong, change it in a small separate PR first and tell the other users who call it.
- Full docstrings (what it returns, edge cases, which requirement) are in the code.

Status: **stub** = raises `NotImplementedError`; **works** = already done in the foundation.

## `app/services/catalog.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `list_base_chips` | `(*, include_inactive=False) -> list[BaseChip]` | US-102 (U1-01), US-701 (U3-03) | stub |
| `get_base_chip` | `(chip_id: str) -> BaseChip \| None` | US-201 (U2-01) | stub |
| `list_flavors` | `(*, include_inactive=False) -> list[Flavor]` | US-102 (U1-01), US-202 (U2-02), US-301 (U2-03), US-702 (U3-04) | stub |
| `featured_chips` | `() -> list[BaseChip]` | US-101 (U1-03) | stub |
| `search` | `(query: str, filters: SearchFilters \| None = None, sort: str = "featured") -> SearchResults` | US-103 (U1-02), US-104 (U1-04), US-105 (U1-05) | stub |
| `list_staff_picks` | `(base_chip_id: str \| None = None) -> list[StaffPick]` | US-601 (U2-08) | stub |
| `random_combo` | `() -> tuple[str, list[str]]` | US-602 (U1-07) | stub |
| `get_settings` | `() -> StoreSettings` | US-301 (U2-03), US-706 (U1-06) | stub |

## `app/services/cart.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `get_cart` | `() -> list[CartLine]` | US-303 (U2-06) | stub |
| `count_bags` | `() -> int` | US-302 (U2-04). The header shows no count until this works | stub |
| `add_bag` | `(base_chip_id: str, flavor_ids: Sequence[str], quantity: int) -> None` | US-302 (U2-04) | stub |
| `update_qty` | `(line_id: str, quantity: int) -> None` | US-304 (U2-07) | stub |
| `remove_line` | `(line_id: str) -> None` | US-304 (U2-07) | stub |
| `merge_guest_cart` | `() -> None` | US-305 (L-05). Also add the call in `app/utils/session.py` `on_sign_in()` | stub |

## `app/services/orders.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `place_order` | `(delivery_name: str, delivery_address: str, idempotency_key: str) -> PlacedOrder` | US-402 (L-03). Calls the `place_order` database function | stub |
| `get_order` | `(order_id: str) -> Order \| None` | US-403 (L-04), US-704 (L-07) | stub |
| `list_my_orders` | `() -> list[Order]` | US-504 (L-06) | stub |
| `list_all_orders` | `(*, status=None, date_from=None, date_to=None) -> list[Order]` | US-704 (L-07) | stub |
| `set_status` | `(order_id: str, status: str) -> None` | US-704 (L-07) | stub |
| `cancel_order` | `(order_id: str) -> None` | US-704 (L-07). **Needs a `cancel_order` database function** | stub |
| `flavors_tried` | `() -> set[str]` | US-603 (U2-09) | stub |

## `app/services/admin.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `save_base_chip` | `(chip: BaseChip) -> BaseChip` | US-701 (U3-03) | stub |
| `save_flavor` | `(flavor: Flavor) -> Flavor` | US-702 (U3-04) | stub |
| `save_staff_pick` | `(base_chip_id: str, position: int, title: str, flavor_ids: Sequence[str]) -> None` | US-702 AC3 (U3-04) | stub |
| `upload_image` | `(file_name: str, data: bytes, content_type: str) -> str` | US-701 (U3-03). **Needs the `product-images` bucket** | stub |
| `set_stock` | `(item_type: str, item_id: str, new_stock: int, reason: str) -> None` | US-703 (U3-05). **Needs a `set_stock` database function** | stub |
| `stock_history` | `(item_type=None, item_id=None) -> list[StockChange]` | US-703 AC4 (U3-05) | stub |
| `find_user` | `(email: str) -> UserSummary \| None` | US-705 (U3-06) | stub |
| `set_role` | `(user_id: str, role: str) -> None` | US-705 (U3-06). **Needs a `set_role` database function** | stub |
| `save_settings` | `(settings: StoreSettings) -> None` | US-706 (U1-06) | stub |
| `dashboard_stats` | `() -> DashboardStats` | US-707 (U1-08) | stub |

## `app/services/profile.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `update_profile` | `(display_name: str, default_address: str \| None) -> None` | US-505 (U3-08) | stub |

## `app/services/auth.py` (built in Prompt D)

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `sign_in` | `(email: str, password: str) -> CurrentUser` | US-502 (U3-01) | works |
| `register` | `(display_name: str, email: str, password: str) -> CurrentUser \| None` | US-501 (U3-02) | works |
| `sign_out` | `() -> None` | US-502 (U3-01) | works |
| `current_user` | `() -> CurrentUser \| None` | all pages | works |
| `require_role` | `(*allowed_roles: str) -> CurrentUser` | every protected page | works |
| `password_problems` | `(password: str) -> list[str]` | US-501 (U3-02) | works |
| `reset_password` | `(email: str) -> None` | US-503 (U3-07) | stub |

## Helpers in `app/utils/`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `pricing.bag_price` | `(base: BaseChip, flavors: Sequence[Flavor]) -> Decimal` | US-301 (U2-03), checkout | works |
| `pricing.check_flavor_limit` | `(chosen: int, max_flavors: int) -> str \| None` | US-301 (U2-03) | works |
| `pricing.combined_allergens` | `(base: BaseChip, flavors: Sequence[Flavor]) -> list[str]` | US-203 (U2-05) | works |
| `outbox.write_confirmation_email` | `(order: Order, to_email: str, from_email: str, outbox_dir: Path) -> Path` | US-404 (L-01) | stub |
| `session.on_sign_in` | `() -> None` | US-305 (L-05) adds the cart merge | works (empty) |

## Data types

All in `app/models/`: `BaseChip`, `Flavor`, `StaffPick`, `StoreSettings`, `SearchFilters`, `SearchResults` (`catalog.py`); `CartLine` (`cart.py`); `Order`, `OrderLine`, `PlacedOrder` (`orders.py`); `UserSummary`, `StockChange`, `DashboardStats` (`admin.py`). `CurrentUser` is in `app/services/auth.py`.

## Shared components (`app/components/`)

Final signatures; stories fill in the ones marked "coming soon" inside.

| Component | Signature | Story |
|---|---|---|
| `states.coming_soon` / `empty_state` / `error_state` / `not_found` / `access_denied` / `offline` / `demo_footer` | see `states.py` | S16, all |
| `badges.stock_badge` / `order_status_badge` / `new_badge` | see `badges.py` | all |
| `header.render_header` | `(user: CurrentUser \| None) -> None` | US-502 (U3-01) |
| `product_card.product_card` | `(chip: BaseChip, *, low_stock_threshold=10) -> None` | US-102 (U1-01) |
| `search_filters.search_filters` | `(*, styles, families) -> SearchFilters` | US-104 (U1-04), coming soon |
| `flavor_tile.flavor_tile` | `(flavor: Flavor, *, selected=False, disabled=False, key: str) -> bool` | US-202 (U2-02) |
| `bag_builder.bag_builder` | `(chip, flavors, *, max_flavors, preselected_flavor_ids=()) -> None` | US-301/302/203 (U2-03 to U2-05), coming soon |
| `price_summary.price_summary` | `(base, flavors, quantity) -> None` | US-301 (U2-03) |
| `qty_stepper.qty_stepper` | `(label, *, value, max_value, key, min_value=1) -> int` | US-302 (U2-04), US-304 (U2-07) |
| `staff_picks.staff_picks_row` | `(picks: Sequence[StaffPick]) -> None` | US-601 (U2-08) |
| `order_history.order_history` | `(user: CurrentUser) -> None` | US-504 (L-06), coming soon |
| `profile_form.profile_form` | `(user: CurrentUser) -> None` | US-505 (U3-08), coming soon |
| `flavor_passport.flavor_passport` | `(user: CurrentUser) -> None` | US-603 (U2-09), coming soon |
