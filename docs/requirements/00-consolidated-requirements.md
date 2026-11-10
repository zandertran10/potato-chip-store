# 00: Consolidated Requirements (start here)

- **Status:** Draft v0.2
- **Product:** An online store that sells bags of potato chips. A shopper picks a **base chip** (Classic, Kettle, Wavy, Sweet Potato) and adds **1 to 3 flavor add-ons** (Sea Salt, Smoky BBQ, Zesty Lime…) to build their own bag. Owner and staff manage the chips, flavors, stock and orders.
- **Purpose:** A classroom demo for learning to build a real app. No real payments, no real emails, no real customer data.
- **Stack:** Streamlit (Python) · Supabase (Postgres, Auth, Storage) · GitHub · Streamlit Community Cloud (recommended)

| Doc | Contents |
|-----|----------|
| `00-consolidated-requirements.md` | This one-page summary |
| `01-product-features-user-stories.md` | Epics E1–E7, user stories with acceptance criteria, seed data |
| `02-ui-ux-requirements.md` | Design vision, screens S1–S16, user flows, Streamlit limits |
| `03-non-functional-requirements.md` | Security, privacy, data integrity, performance, deployment |

---

## 1. Goals

| # | Goal | How we know it's met |
|---|------|----------------------|
| G1 | A shopper can build a custom bag and order it in under 3 minutes | Flow A (doc 02) works from start to finish |
| G2 | Stock is always correct | Orders deduct stock in one step; stock never goes below 0; no double orders |
| G3 | Staff run the store without touching code | Chips, flavors, stock and orders can all be managed in the admin pages |
| G4 | It's a clean teaching example of a production-style app | RLS on every table, no committed keys, CI, reviews, tagged releases |
| G5 | The store sparks curiosity in an honest way | Staff picks, Surprise me and the flavor passport, with no pressure tactics |

## 2. Users and roles

| Role | Who | Can do |
|------|-----|--------|
| Guest | Not signed in | Browse, search, view, build bags, use the cart |
| Customer | Registered shopper | Plus check out, see own orders, flavor passport |
| Staff | Store employee | Plus manage chips, flavors, stock and orders |
| Owner | Store owner | Plus manage staff roles and store settings |

A guest must sign in to check out. Their cart is kept when they do.

## 3. Feature summary

| Epic | Feature | Summary | Must stories |
|------|---------|---------|--------------|
| E1 | Product search and catalog | Home page, shop grid, keyword search, filters, sort | US-101, 102, 103 |
| E2 | Product detail | Chip page, flavor details with taste profile, combined allergens | US-201, 202, 203 |
| E3 | Add to cart | Build Your Bag (base + 1–3 flavors), quantity, cart, edit, keep cart on sign-in | US-301 to 305 |
| E4 | Checkout and confirmation | No card needed; stock deducted; confirmation email saved to `outbox/` | US-401 to 404 |
| E5 | Register / sign in | Register, sign in/out, reset password, my orders, profile | US-501, 502, 504 |
| E6 | Flavor discovery | Staff picks, Surprise me, flavor passport (ethical, no pressure) | (none; Should/Could) |
| E7 | Owner and staff management | Chips, flavors, stock, orders, staff roles, settings, dashboard | US-701 to 705 |

### 3.1 Key business rules

| ID | Rule |
|----|------|
| BR-01 | A bag has exactly one base chip and 1 to 3 flavors. The maximum is a store setting. |
| BR-02 | Bag price = base chip price + each flavor's price. |
| BR-03 | One bag uses 1 unit of stock of the base chip and 1 unit of each chosen flavor. |
| BR-04 | Sold-out items are shown but can't be added. |
| BR-05 | Stock is checked again at checkout. If anything ran out, no order is created. |
| BR-06 | An order deducts all of its stock in one step (all or nothing). |
| BR-07 | No payment is taken. The order status starts as "Placed". |
| BR-08 | Order numbers look like `CHIP-YYYYMMDD-####`. |
| BR-09 | Each confirmation email is saved as `outbox/order-<number>.eml` and never sent. |
| BR-10 | Chips and flavors that appear in orders are made inactive, never deleted. |

## 4. UI/UX summary

Professional yet lighthearted, with warm golden colors, friendly wording and clean layouts. **Build Your Bag** (screen S3) is the hero: flavor tiles with taste profiles, a live price, allergens and one clear "Add to cart" button. Curiosity comes from staff picks, Surprise me and the flavor passport, never from fake timers or fake scarcity. There are 16 screens (S1–S16), and every one has loading, empty and error states and works on phones. Full details: doc 02.

## 5. Non-functional summary

- **Sign-in:** Supabase Auth with email and password, rate limits on, a general error message on failed sign-in
- **Security:** RLS on every table; roles enforced in the database; anon key only in the app; no keys in the repo
- **Privacy and child safety:** minimal data, fictional demo data, age-appropriate content, no tracking, no pressure tactics
- **Data integrity:** one `place_order` database function; no overselling; no double orders
- **Quality:** ruff, pytest (unit + integration), CI on every pull request, reviews, migrations only
- **Deployment:** Local → Staging → Production; Streamlit Community Cloud; tagged releases
- **Limits:** about 30 people at once, free tiers only

Full details: doc 03.

## 6. Logical data model

All tables have **RLS enabled**. `id` columns are `uuid` unless noted. Money uses `numeric(6,2)`. Timestamps use `timestamptz`.

| Table | Key fields | Notes |
|-------|-----------|-------|
| `profiles` | `id` (= `auth.users.id`), `display_name`, `role` (`customer` / `staff` / `owner`), `default_address`, `created_at` | Created automatically for each new user, with role `customer` |
| `base_chips` | `id`, `name`, `description`, `style`, `thickness`, `crunch_level` (0–3), `price` (> 0), `stock` (≥ 0), `image_path`, `image_alt`, `is_featured`, `is_active`, `created_at`, `updated_at` | Anyone can read active rows; staff can write |
| `flavors` | `id`, `name`, `description`, `family`, `salty`, `tangy`, `sweet`, `heat` (each 0–3), `allergens` (text[]), `price` (> 0), `stock` (≥ 0), `icon`, `is_active`, `created_at`, `updated_at` | Same access as `base_chips` |
| `staff_picks` | `id`, `base_chip_id` → `base_chips`, `title`, `position` (1–3) | Up to 3 per chip |
| `staff_pick_flavors` | `staff_pick_id` → `staff_picks`, `flavor_id` → `flavors` | The flavors in a pick |
| `carts` | `id`, `user_id` → `profiles` (unique), `updated_at` | One saved cart per customer; guest carts live in the session |
| `cart_items` | `id`, `cart_id` → `carts`, `base_chip_id` → `base_chips`, `quantity` (> 0), `created_at` | One line = one bag design |
| `cart_item_flavors` | `cart_item_id` → `cart_items`, `flavor_id` → `flavors` | 1–3 per line |
| `orders` | `id`, `order_number` (unique), `user_id` → `profiles`, `status` (`placed` / `packed` / `shipped` / `cancelled`), `delivery_name`, `delivery_address`, `total`, `idempotency_key` (unique), `created_at` | Created only by `place_order` |
| `order_items` | `id`, `order_id` → `orders`, `base_chip_id`, `base_name`, `base_price`, `unit_price`, `quantity`, `line_total` | Names and prices copied at purchase time |
| `order_item_flavors` | `order_item_id` → `order_items`, `flavor_id`, `flavor_name`, `flavor_price` | Copied at purchase time; also feeds the flavor passport |
| `stock_history` | `id`, `item_type` (`base` / `flavor`), `item_id`, `change` (+/−), `reason`, `order_id` (optional), `changed_by` → `profiles`, `created_at` | Written by database functions only |
| `settings` | `id` (always 1), `max_flavors` (1–5, default 3), `low_stock_threshold` (default 10), `from_email` | A single row |

**Database functions:** `place_order(address, idempotency_key)`, `cancel_order(order_id)`, `set_stock(item_type, item_id, new_stock, reason)`, `set_role(user_id, role)` (owner only).

**Storage:** bucket `product-images` (anyone can read, staff and owner can upload).

## 7. Scope

**In scope (Release 1):** all Must stories in E1–E5 and E7, the seed data, 3 environments, CI, and a tagged release.

**If time allows:** the Should and Could stories (filters, sort, reset password, profile, staff picks, Surprise me, flavor passport, settings, dashboard).

**Out of scope:** real payments, taxes, shipping, sending real emails, reviews, several bag sizes, social sign-in, a mobile app, leaderboards or streaks.

## 8. Open questions (with default answers)

Decide these as a class. If nobody decides, the default answer applies.

| # | Question | Default answer |
|---|----------|----------------|
| Q1 | What is the store called? | **Chip Lab** |
| Q2 | Maximum flavors per bag? | **3** (a store setting, so it can change later) |
| Q3 | Email confirmation at sign-up? | **Off** for local and class demos, **on** in production |
| Q4 | Where is the app hosted? | **Streamlit Community Cloud** (ADR 0001) |
| Q5 | Can guests check out without an account? | **No.** Sign-in is needed to check out, but guests can browse and use the cart. |
| Q6 | Currency? | **USD ($)**, shown with 2 decimals |
| Q7 | Where do product images come from? | Free-to-use stock photos or simple drawn illustrations, stored in Supabase Storage |
| Q8 | Team size? | **4:** a tech lead plus 3 developers |

## 9. Suggested build order

1. **Foundation (tech lead):** repo setup, CI, settings loading, data models, database migrations (section 6), RLS policies, database functions, seed data, services, sign-in helpers, app shell with every page as a placeholder, shared components, tests. See `docs/planning/work-division-plan.md`.
2. **Core shopping (in parallel):** E1 catalog and search · E2 + E3 product and cart · E5 sign-in and register · E4 checkout (tested with seeded carts)
3. **Management:** E7 admin pages
4. **Extras:** E6 flavor discovery, and the Should/Could stories
5. **Release:** full test on staging → `v1.0.0` → production

## 10. Traceability

| Epic | Stories | Screens (doc 02) | Main NFRs (doc 03) |
|------|---------|------------------|--------------------|
| E1 Search and catalog | US-101 to US-105 | S1, S2, S16 | NFR-PERF-02, NFR-PERF-03, NFR-PERF-05, NFR-SEC-04, NFR-UX-01 |
| E2 Product detail | US-201 to US-203 | S3 | NFR-PRIV-07, NFR-SEC-15, NFR-UX-01 |
| E3 Add to cart | US-301 to US-305 | S3, S4 | NFR-DI-02, NFR-SEC-03, NFR-AUTH-05, NFR-UX-03 |
| E4 Checkout and confirmation | US-401 to US-404 | S5, S6 | NFR-DI-01 to 05, NFR-DI-08, NFR-SEC-03, NFR-SEC-07, NFR-PRIV-03, NFR-DEP-07 |
| E5 Register / sign in | US-501 to US-505 | S7, S8, S9, S10 | NFR-AUTH-01 to 08, NFR-SEC-01, NFR-PRIV-01, NFR-LOG-03 |
| E6 Flavor discovery | US-601 to US-603 | S1, S3, S10 | NFR-PRIV-05, NFR-UX-01 |
| E7 Owner and staff management | US-701 to US-707 | S11 to S15 | NFR-SEC-04 to 07, NFR-SEC-16, NFR-DI-06, NFR-DI-07, NFR-LOG-02 |
| All | n/a | S16, footer | NFR-REL-01 to 03, NFR-PRIV-04, NFR-MNT-01 to 08 |
