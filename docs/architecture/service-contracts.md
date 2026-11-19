# Service contracts

Every service function the stories need, with its owner. The foundation (Prompt E) created them with final signatures; the Release 1 stories filled them all in.

**Rules**
- Pages call services; pages never call Supabase directly (CLAUDE.md layers).
- A story fills in its function **without changing the signature**. If a signature turns out wrong, change it in a small separate PR first and tell the other users who call it.
- Full docstrings (what it returns, edge cases, which requirement) are in the code.

Status: **works** = built and covered by unit tests in `tests/unit/`.

## `app/services/catalog.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `list_base_chips` | `(*, include_inactive=False) -> list[BaseChip]` | US-102 (U1-01), US-701 (U3-03) | works |
| `get_base_chip` | `(chip_id: str) -> BaseChip \| None` | US-201 (U2-01) | works |
| `list_flavors` | `(*, include_inactive=False) -> list[Flavor]` | US-102 (U1-01), US-202 (U2-02), US-301 (U2-03), US-702 (U3-04) | works |
| `featured_chips` | `() -> list[BaseChip]` | US-101 (U1-03) | works |
| `search` | `(query: str, filters: SearchFilters \| None = None, sort: str = "featured") -> SearchResults` | US-103 (U1-02), US-104 (U1-04), US-105 (U1-05) | works |
| `list_staff_picks` | `(base_chip_id: str \| None = None) -> list[StaffPick]` | US-601 (U2-08) | works |
| `random_combo` | `() -> tuple[str, list[str]]` | US-602 (U1-07) | works |
| `get_settings` | `() -> StoreSettings` | US-301 (U2-03), US-706 (U1-06) | works |

## `app/services/cart.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `get_cart` | `() -> list[CartLine]` | US-303 (U2-06), US-401 (L-02) | works |
| `count_bags` | `() -> int` | US-302 (U2-04). The header shows no count until this works | works |
| `add_bag` | `(base_chip_id: str, flavor_ids: Sequence[str], quantity: int) -> None` | US-302 (U2-04) | works |
| `update_qty` | `(line_id: str, quantity: int) -> None` | US-304 (U2-07) | works |
| `remove_line` | `(line_id: str) -> None` | US-304 (U2-07) | works |
| `merge_guest_cart` | `() -> None` | US-305 (L-05). Also add the call in `app/utils/session.py` `on_sign_in()` | works |

## `app/services/orders.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `place_order` | `(delivery_name: str, delivery_address: str, idempotency_key: str) -> PlacedOrder` | US-402 (L-03). Calls the `place_order` database function | works |
| `get_order` | `(order_id: str) -> Order \| None` | US-403 (L-04), US-704 (L-07) | works |
| `list_my_orders` | `() -> list[Order]` | US-504 (L-06) | works |
| `list_all_orders` | `(*, status=None, date_from=None, date_to=None) -> list[Order]` | US-704 (L-07) | works |
| `set_status` | `(order_id: str, status: str) -> None` | US-704 (L-07) | works |
| `cancel_order` | `(order_id: str) -> None` | US-704 (L-07). Database function in migration 11 | works |
| `flavors_tried` | `() -> set[str]` | US-603 (U2-09) | works |

## `app/services/admin.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `save_base_chip` | `(chip: BaseChip) -> BaseChip` | US-701 (U3-03) | works |
| `save_flavor` | `(flavor: Flavor) -> Flavor` | US-702 (U3-04) | works |
| `save_staff_pick` | `(base_chip_id: str, position: int, title: str, flavor_ids: Sequence[str]) -> None` | US-702 AC3 (U3-04) | works |
| `upload_image` | `(file_name: str, data: bytes, content_type: str) -> str` | US-701 (U3-03). Bucket in migration 12 | works |
| `set_stock` | `(item_type: str, item_id: str, new_stock: int, reason: str) -> None` | US-703 (U3-05). Database function in migration 11 | works |
| `stock_history` | `(item_type=None, item_id=None) -> list[StockChange]` | US-703 AC4 (U3-05) | works |
| `find_user` | `(email: str) -> UserSummary \| None` | US-705 (U3-06) | works |
| `set_role` | `(user_id: str, role: str) -> None` | US-705 (U3-06). Database function in migration 11 | works |
| `save_settings` | `(settings: StoreSettings) -> None` | US-706 (U1-06) | works |
| `dashboard_stats` | `() -> DashboardStats` | US-707 (U1-08) | works |

## `app/services/profile.py`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `update_profile` | `(display_name: str, default_address: str \| None) -> None` | US-505 (U3-08) | works |

## `app/services/auth.py` (built in Prompt D)

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `sign_in` | `(email: str, password: str) -> CurrentUser` | US-502 (U3-01) | works |
| `register` | `(display_name: str, email: str, password: str) -> CurrentUser \| None` | US-501 (U3-02) | works |
| `sign_out` | `() -> None` | US-502 (U3-01) | works |
| `current_user` | `() -> CurrentUser \| None` | all pages | works |
| `require_role` | `(*allowed_roles: str) -> CurrentUser` | every protected page | works |
| `password_problems` | `(password: str) -> list[str]` | US-501 (U3-02) | works |
| `reset_password` | `(email: str) -> None` | US-503 (U3-07) | works |

## Helpers in `app/utils/`

| Function | Signature | Story (pick code) | Status |
|---|---|---|---|
| `pricing.bag_price` | `(base: BaseChip, flavors: Sequence[Flavor]) -> Decimal` | US-301 (U2-03), checkout | works |
| `pricing.check_flavor_limit` | `(chosen: int, max_flavors: int) -> str \| None` | US-301 (U2-03) | works |
| `pricing.combined_allergens` | `(base: BaseChip, flavors: Sequence[Flavor]) -> list[str]` | US-203 (U2-05) | works |
| `outbox.write_confirmation_email` | `(order: Order, to_email: str, from_email: str, outbox_dir: Path) -> Path` | US-404 (L-01) | works |
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
| `search_filters.search_filters` | `(*, styles, families) -> SearchFilters` | US-104 (U1-04) |
| `flavor_tile.flavor_tile` | `(flavor: Flavor, *, selected=False, disabled=False, key: str) -> bool` | US-202 (U2-02) |
| `bag_builder.bag_builder` | `(chip, flavors, *, max_flavors, preselected_flavor_ids=()) -> None` | US-301/302/203 (U2-03 to U2-05) |
| `price_summary.price_summary` | `(base, flavors, quantity) -> None` | US-301 (U2-03) |
| `qty_stepper.qty_stepper` | `(label, *, value, max_value, key, min_value=1) -> int` | US-302 (U2-04), US-304 (U2-07) |
| `staff_picks.staff_picks_row` | `(picks: Sequence[StaffPick]) -> None` | US-601 (U2-08) |
| `order_history.order_history` | `(user: CurrentUser) -> None` | US-504 (L-06) |
| `profile_form.profile_form` | `(user: CurrentUser) -> None` | US-505 (U3-08) |
| `flavor_passport.flavor_passport` | `(user: CurrentUser) -> None` | US-603 (U2-09) |

## Added while building the stories

Additions only; no existing signature changed.

| Function | Signature | Why | Story |
|---|---|---|---|
| `catalog.image_url` | `(image_path: str \| None) -> str \| None` | Models keep the storage path; pages need a URL | US-201, US-102 |
| `catalog.CatalogUnavailable` | exception | Pages show the offline message (NFR-REL-01) | all catalog stories |
| `catalog.random_combo` | adds `*, rng=None` | Tests can fix the random seed | US-602 |
| `cart.max_quantity` | `(base_chip, flavors) -> int` | Lowest stock of a bag's parts | US-302, US-304 |
| `cart.CartError`, `orders.OrderError`, `admin.AdminError`, `profile.ProfileError` | exceptions | Friendly, safe-to-show messages | all |
| `profile.get_default_address` | `() -> str \| None` | Checkout pre-fills the address | US-505, US-401 |
| `auth.PASSWORD_RULES` | constant | The live checklist on Register | US-501 |
| `pages.page_for`, `pages.current_url_path` | helpers | Safe `?next=` after sign-in | US-502 |
| `admin.dashboard_stats` | adds `*, now=None` | Tests can fix the date | US-707 |
| `outbox.build_confirmation_email` | `(order, to_email, from_email) -> EmailMessage` | Lets tests read the email | US-404 |
| `flavor_tile` | adds `selectable=True` | Display-only tiles in the flavor library | US-102 |
| `bag_builder` | adds `all_chips=None` | Switch the base chip (S3 step 1) | US-301 |

**US-401 (review the order)** has no function of its own: it uses `auth.require_role`, `cart.get_cart` and `profile.get_default_address`.
