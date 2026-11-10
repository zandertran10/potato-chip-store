# Work Division Plan

Who builds what, in what order, and how it all comes together into the released product.

- **Team (4):** **Lead** (tech lead), **User 1**, **User 2**, **User 3**. The Lead builds the foundation first, then picks up stories like everyone else.
- **Based on:** `docs/requirements/`, which defines the stories (`US-301`), screens (`S3`), requirements (`NFR-SEC-02`), and the data model (doc 00, section 6).
- **Approach:** It's a demo, so we keep it simple. We still work like a real production team: protected `main`, pull requests, reviews, CI, migrations, staging, tagged releases.

---

## 1. Overview

```
WEEK 1                         WEEKS 2-3                                   WEEK 4
PHASE 1: FOUNDATION            PHASE 2: STORIES IN PARALLEL                PHASE 3: RELEASE
──────────────────────         ─────────────────────────────────────       ─────────────────────
Lead: F1 → F15                 Lead:   L-01 … L-07  Checkout & Orders      Feature freeze
                               User 1: U1-01 … U1-08 Discover              Release candidate
Users 1-3: setup + one docs    User 2: U2-01 … U2-09 Product & Cart        Test on staging
task each (U1-00, U2-00,       User 3: U3-01 … U3-08 Accounts & Admin      Fix → v1.0.0 → Demo
U3-00)                         (one story = one commit on main)
        │                                    │                                      │
        └── tag v0.1.0 ──────────────────────┴──── main always works ───────────────┘
```

**Why the lanes don't block each other:**
1. The Lead builds everything that's shared **first**: database, data functions, sign-in, an empty placeholder for every screen, shared components, seed data.
2. Each lane owns **its own files** (section 3), so two people never edit the same file at once.
3. Each lane tests with **seed data**. For example, checkout is tested with the seeded customer's cart, so it doesn't wait for the cart page.
4. **Every user's first story has no dependencies**, so everyone starts on day one of Phase 2.

---

## 2. The golden rule: one story = one commit

> **Every story and every foundation item arrives on `main` as exactly one commit.**

1. One story → one branch → one pull request (PR). Never two stories in one PR.
2. On your branch, commit as often as you like.
3. Merge with **Squash and merge**. GitHub turns the branch into **one** commit on `main`. (The repo only allows squash merging; see section 7.)
4. The PR title becomes the commit message. Use this format:

```
<type>(<area>): <pick code> <story ID> <short description>

feat(cart): U2-03 US-301 build your bag panel
feat(db): F8 migrations for all tables
fix(cart): U2-07 BUG-12 total not updating after remove
docs(design): U1-00 wireframes and visual style
```
Types: `feat`, `fix`, `docs`, `test`, `chore` (setup and tooling), `refactor`.

Result: `git log --oneline main` reads like a list of finished stories, and any story can be undone with one `git revert`.

---

## 3. File ownership

| Owner | Files (after the foundation) |
|-------|-----------------------------|
| **Lead** | `supabase/**`, `app/services/**`, `app/models/**`, `app/config/**`, `app/utils/**`, `app/main.py`, `.github/**`, `requirements*.txt`, `pages/checkout.py`, `pages/confirmation.py`, `pages/my_account.py`, `components/order_history.py`, `pages/admin_orders.py` |
| **User 1** | `pages/home.py`, `pages/shop.py`, `pages/admin_settings.py`, `pages/admin_dashboard.py`, `components/product_card.py`, `components/search_filters.py`, `.streamlit/config.toml`, `assets/styles/**`, `docs/design/**` |
| **User 2** | `pages/product.py`, `pages/cart.py`, `components/bag_builder.py`, `components/flavor_tile.py`, `components/price_summary.py`, `components/qty_stepper.py`, `components/staff_picks.py`, `components/flavor_passport.py` |
| **User 3** | `pages/sign_in.py`, `pages/register.py`, `pages/reset_password.py`, `components/header.py`, `components/profile_form.py`, `pages/admin_chips.py`, `pages/admin_flavors.py`, `pages/admin_stock.py`, `pages/admin_staff.py` |

(`pages/` = `app/pages/`, `components/` = `app/components/`.)

- You may **read and call** any file. You only **edit** files you own.
- Need a change in someone else's file (for example a new service function)? Make a small change in your PR and **add the owner as a reviewer**. `CODEOWNERS` does this automatically.
- Tests go in `tests/unit/` or `tests/integration/`, named after the file they test (for example `tests/unit/test_bag_builder.py`).
- The **My account** screen (S10) is one page with three tabs. Each tab shows a component owned by a different person: order history (Lead), profile form (User 3), and flavor passport (User 2). This way nobody has to wait for anyone else.

---

## 4. Phase 1: Foundation (Lead)

The Lead delivers the foundation as **15 small items, F1 to F15**. Each one is a single PR and a single commit, done in order. Users 1–3 review them, which is how they learn the codebase.

| Code | Item | Size | Depends on |
|------|------|------|------------|
| F1 | Repo settings and branch protection | S | none |
| F2 | Labels, milestones, project board and story issues | S | F1 |
| F3 | Dev tooling and test setup | S | F1 |
| F4 | CI workflow, PR/issue templates, CODEOWNERS | S | F3 |
| F5 | App config and logging | S | F3 |
| F6 | Supabase project setup and hosting decision | S | F1 |
| F7 | Data models | S | F3 |
| F8 | Migrations for all tables | L | F6 |
| F9 | RLS policies, storage bucket and RLS tests | M | F8 |
| F10 | Database functions | M | F9 |
| F11 | Seed data | S | F10 |
| F12 | Services layer | L | F5, F7, F11 |
| F13 | Sign-in, session and guards | M | F12 |
| F14 | App shell, theme, shared components and helpers | M | F13 |
| F15 | Developer docs, staging deploy, tag v0.1.0 | S | F14 |

### F1 Repo settings and branch protection · S
- **Branch:** `chore/F1-repo-settings`
- **Build:**
  - Protect `main`: require a PR with 1 approval and block force pushes. **Admins may bypass during the foundation phase**, so the Lead isn't blocked while working alone. Remove the bypass when F15 is merged.
  - Allow **squash merging only** and turn on "automatically delete head branches".
- **Commit:** `chore(repo): F1 branch protection and merge settings`

### F2 Labels, milestones, board and story issues · S
- **Build:**
  - The labels and milestones from section 7
  - A GitHub Project board with columns Backlog → To do → In progress → In review → Done
  - **One issue per story and per foundation item**, using the format in section 7.4
- **Commit:** `chore(repo): F2 labels, milestones, board and issues`. This is done on GitHub, not in code. If it's scripted, the script is saved as `scripts/create_issues.py`.

### F3 Dev tooling and test setup · S
- **Branch:** `chore/F3-dev-tooling`
- **Build:**
  - `requirements-dev.txt` with `pytest`, `ruff` and `pip-audit`
  - `pyproject.toml` with ruff and pytest settings
  - `tests/unit/` and `tests/integration/`, each with a `conftest.py`. Integration tests are skipped when there's no Supabase connection.
  - One sample test, so CI has something to run
- **Commit:** `chore(tooling): F3 ruff, pytest and test folders`

### F4 CI workflow, templates, CODEOWNERS · S
- **Branch:** `chore/F4-ci`
- **Build:**
  - `.github/workflows/ci.yml`: on every PR, use Python 3.11, install requirements, run `ruff check .` and `pytest tests/unit`
  - `.github/pull_request_template.md` with the Definition of Done (section 9)
  - `.github/ISSUE_TEMPLATE/story.md` and `bug.md`
  - `.github/CODEOWNERS` based on section 3
  - Make "CI must pass" a required check on `main`
- **Commit:** `chore(ci): F4 GitHub Actions, templates and CODEOWNERS`

### F5 App config and logging · S
- **Branch:** `feat/F5-config`
- **Files:** `app/config/settings.py`, `app/utils/logging_setup.py`
- **Build:**
  - Load the Supabase URL and anon key from `st.secrets`, or from environment variables or `.env` (NFR-SEC-09, NFR-DEP-03). If they're missing, show a clear error.
  - Logging set up following NFR-LOG-01 to 04
- **Commit:** `feat(config): F5 settings loading and logging`

### F6 Supabase project setup and hosting decision · S
- **Branch:** `chore/F6-supabase-setup`
- **Build:**
  - `supabase init` (adds `supabase/config.toml`); `supabase start` runs locally
  - Create the **staging** Supabase project (keys stay in the dashboard, never in the repo)
  - Set Auth: password rules (NFR-AUTH-02), email confirmation off for development
  - Mark ADR 0001 (hosting) as Accepted, with Streamlit Community Cloud
- **Commit:** `chore(db): F6 Supabase project setup and hosting ADR`

### F7 Data models · S
- **Branch:** `feat/F7-models`
- **Files:** `app/models/*.py`
- **Build:** typed dataclasses for `Profile`, `BaseChip`, `Flavor`, `StaffPick`, `Bag`, `CartLine`, `Order`, `OrderLine`, `Settings`, matching doc 00 section 6. Unit tests for any helper methods.
- **Commit:** `feat(models): F7 data classes for the domain`

### F8 Migrations for all tables · L
- **Branch:** `feat/F8-migrations`
- **Files:** `supabase/migrations/<timestamp>_initial_schema.sql`
- **Build:**
  - Every table in **doc 00 section 6**, with primary keys, foreign keys, `CHECK` constraints (`price > 0`, `stock >= 0`, the role and status values) and indexes (NFR-PERF-05)
  - **RLS enabled on every table in this migration** (NFR-SEC-02). With no policies yet, nobody can access anything, which is the safe default.
  - A trigger that creates a `profiles` row with role `customer` for each new user
  - Update `docs/architecture/data-model.md` with a diagram or a list of relationships
- **Done when:** `supabase db reset` runs cleanly
- **Labels:** `schema-change`
- **Commit:** `feat(db): F8 migrations for all tables`

### F9 RLS policies, storage bucket and RLS tests · M
- **Branch:** `feat/F9-rls`
- **Build:**
  - Policies for guest, customer, staff and owner (NFR-SEC-03 to 05)
  - The `product-images` bucket (anyone can read, staff can upload)
  - Integration tests: customer A can't read customer B's cart or orders; a customer can't edit a chip; staff can't change roles (NFR-SEC-08)
- **Labels:** `schema-change`
- **Commit:** `feat(db): F9 RLS policies, storage bucket and RLS tests`

### F10 Database functions · M
- **Branch:** `feat/F10-db-functions`
- **Build:**
  - `place_order`: in one transaction, lock the rows, check stock, deduct it, copy names and prices into the order, write `stock_history`, empty the cart, and return the order number (NFR-DI-01 to 05)
  - `cancel_order` (staff only; puts stock back)
  - `set_stock` (staff only; writes history)
  - `set_role` (owner only; nobody can change their own role)
- **Tests:** a normal order; out of stock; the last bag bought by two people at once; a double click with the same key (one order); cancel puts stock back; a non-owner calling `set_role` is rejected
- **Labels:** `schema-change`
- **Commit:** `feat(db): F10 place_order, cancel_order, set_stock and set_role`

### F11 Seed data · S
- **Branch:** `feat/F11-seed`
- **Files:** `supabase/seed/seed.sql`, `scripts/seed_users.py` (creates the demo users with the service role key, **locally only**)
- **Build:** everything in doc 01 section 5: 4 chips, 10 flavors, staff picks, 3 demo accounts, a cart with 2 bags and 2 past orders for the demo customer, default settings
- **Done when:** `supabase db reset` plus the seed script gives a store that's ready to demo
- **Commit:** `feat(db): F11 demo seed data and accounts`

### F12 Services layer · L
- **Branch:** `feat/F12-services`
- **Files:** `app/services/*.py`
- **Build:** all database access, with type hints, returning `app/models` objects:
  - `supabase_client.py`
  - `catalog.py`: `list_base_chips`, `get_base_chip`, `list_flavors`, `search(query, filters, sort)`, `list_staff_picks`, `random_combo`, `get_settings`
  - `cart.py`: `get_cart`, `add_bag`, `update_qty`, `remove_line`, `merge_guest_cart`
  - `orders.py`: `place_order`, `list_my_orders`, `get_order`, `list_all_orders`, `set_status`, `cancel_order`, `flavors_tried`
  - `admin.py`: `save_base_chip`, `save_flavor`, `save_staff_pick`, `set_stock`, `upload_image`, `find_user`, `set_role`, `save_settings`, `dashboard_stats`
  - Errors become friendly app errors; details are logged (NFR-REL-02)
  - Catalog reads are cached (NFR-PERF-03)
- **Tests:** integration tests for each service against the local Supabase
- **Commit:** `feat(services): F12 data access for catalog, cart, orders and admin`

### F13 Sign-in, session and guards · M
- **Branch:** `feat/F13-auth`
- **Files:** `app/services/auth.py`, `app/utils/session.py`, `app/utils/guards.py`
- **Build:**
  - `sign_up`, `sign_in`, `sign_out`, `reset_password`, `current_user`, `current_role`
  - The guest cart is kept in session state
  - An `on_sign_in()` hook, left empty for now (US-305 fills it in)
  - `require_login()` and `require_role(...)` (NFR-SEC-06)
- **Tests:** unit tests for the guards
- **Commit:** `feat(auth): F13 sign-in service, session and page guards`

### F14 App shell, theme, shared components and helpers · M
- **Branch:** `feat/F14-app-shell`
- **Build:**
  - `app/main.py` with `st.navigation` listing **every screen S1–S16**. Admin pages only show up for staff and owner.
  - **One placeholder file per screen** in `app/pages/`, each protected by the right guard and showing its title and "Coming soon". Product, checkout and order pages read their ID from the link (`?id=`).
  - Simple first versions of the components in section 3, including stub functions for the three My account tabs and `staff_picks_row()`
  - `app/utils/pricing.py` (`bag_price`, `check_flavor_limit`, with unit tests) and `app/utils/outbox.py` (a basic `.eml` writer)
  - Theme in `.streamlit/config.toml`; a "Demo store, no payment needed" footer; a friendly offline message (NFR-REL-01)
- **Done when:** every screen opens, and a customer sees "Not authorized" on admin pages
- **Commit:** `feat(app): F14 navigation, screen placeholders, components and helpers`

### F15 Developer docs, staging deploy, tag v0.1.0 · S
- **Branch:** `docs/F15-readme-deploy`
- **Build:**
  - `README.md` "Getting started": install Python 3.11+, Git, the Supabase CLI and Docker; clone; create a virtual environment; `pip install -r requirements.txt -r requirements-dev.txt`; copy the `.example` files; `supabase start`; `supabase db reset`; seed; `streamlit run app/main.py`; `pytest`
  - `docs/deployment/README.md`: how to deploy to Streamlit Community Cloud from `main`, with keys in the app's Secrets settings
  - Deploy staging. Remove the admin bypass on `main`.
- **Done when:** User 1 follows the README on a clean computer and the app runs
- **Commit:** `docs(repo): F15 setup guide and staging deployment`

Then tag the foundation:
```bash
git tag -a v0.1.0 -m "Foundation complete"
git push origin v0.1.0
```

**Early start:** if the foundation runs late, lanes can start as soon as **F14** is merged.

### Phase 1 tasks for Users 1–3 (docs only, no app code)

Everyone sets up their computer (step 0 of the playbook), clones the repo, reads `docs/requirements/`, and reviews the Lead's PRs. Each person also does one docs task:

| Code | User | Task | Commit |
|------|------|------|--------|
| U1-00 | User 1 | Mood board, final colors and fonts, low-fidelity wireframes for S1–S16 (doc 02, section 11) in `docs/design/wireframes/` | `docs(design): U1-00 wireframes and visual style` |
| U2-00 | User 2 | Test cases for the Product & Cart lane (from the acceptance criteria) in `docs/testing/product-cart-test-cases.md` | `docs(testing): U2-00 product and cart test cases` |
| U3-00 | User 3 | Test cases for the Accounts & Admin lane, including the security checks, in `docs/testing/accounts-admin-test-cases.md` | `docs(testing): U3-00 accounts and admin test cases` |

At the end of week 1 there is a **design review**: User 1 walks the team through the wireframes before anyone builds screens.

---

## 5. Phase 2: Stories by user

Work **top to bottom** through your own list, **one story at a time**. "Depends on" only lists stories **in the same list**. The few links between users are in section 6.

Sizes: **S** ≈ half a day · **M** ≈ 1 day · **L** ≈ 2 days. Copy the acceptance criteria from doc 01 into the issue.

### Workload

| Person | Lane | Stories | Effort |
|--------|------|---------|--------|
| Lead | Checkout & Orders | 7 (after F1–F15) | ≈ 6 days |
| User 1 | Discover | 8 (+ U1-00) | ≈ 7 days |
| User 2 | Product & Cart | 9 (+ U2-00) | ≈ 7.5 days |
| User 3 | Accounts & Admin | 8 (+ U3-00) | ≈ 8 days |

### Lead: Checkout & Orders lane

| Pick | Story | Pri | Size | Files | Depends on |
|------|-------|-----|------|-------|------------|
| **L-01** | US-404 Confirmation email saved to the outbox | Must | S | `utils/outbox.py`, `tests/unit/test_outbox.py` | none |
| **L-02** | US-401 Review the order | Must | M | `pages/checkout.py` | none |
| **L-03** | US-402 Place the order | Must | M | `pages/checkout.py`, `tests/integration/test_checkout.py` | L-02 |
| **L-04** | US-403 Order confirmation | Must | S | `pages/confirmation.py` | L-03 |
| **L-05** | US-305 Keep cart on sign-in | Must | S | `utils/session.py`, `services/cart.py`, `tests/unit/test_cart_merge.py` | none |
| **L-06** | US-504 My orders | Must | M | `pages/my_account.py`, `components/order_history.py` | none |
| **L-07** | US-704 Manage orders (admin) | Must | M | `pages/admin_orders.py` | none |

What to build:
- **L-01:** a full `.eml` file made with `email.message.EmailMessage` (text and simple HTML), with all fields from US-404 AC2. The file name uses only the order number. If writing fails, the error is logged and the order isn't affected.
- **L-02:** `require_login()`, which returns here after sign-in; steps Cart → Details → Done; a summary from `cart.get_cart()`; the address form with checks; the demo banner. Test it with the seeded customer.
- **L-03:** one idempotency key per checkout attempt, kept in the session; a spinner, with the button disabled while the order is placed; a message listing what ran out; on success, write the outbox email and open the confirmation page (`?order=`). Tests: success, out of stock, double click.
- **L-04:** the order number shown large, items, total, date, the "emailed to" line, `st.balloons()`, and buttons. Opening someone else's order shows "Not found".
- **L-05:** fill in `on_sign_in()` so guest lines are merged, quantities added up, never above stock. Unit tests: empty cart, the same bag in both carts, the stock limit.
- **L-06:** the My account page with 3 tabs; the order history component (newest first, status badges, details, empty state). Test with the seeded orders.
- **L-07:** `require_role("staff","owner")`; filters; order details; the status dropdown; cancel with a confirmation step.

### User 1: Discover lane

| Pick | Story | Pri | Size | Files | Depends on |
|------|-------|-----|------|-------|------------|
| **U1-01** | US-102 Browse the shop | Must | M | `pages/shop.py`, `components/product_card.py` | none |
| **U1-02** | US-103 Search by keyword | Must | S | `pages/shop.py` | U1-01 |
| **U1-03** | US-101 Home page | Must | M | `pages/home.py` | U1-01 (reuses the product card) |
| **U1-04** | US-104 Filter results | Should | M | `pages/shop.py`, `components/search_filters.py` | U1-02 |
| **U1-05** | US-105 Sort results | Should | S | `pages/shop.py` | U1-02 |
| **U1-06** | US-706 Store settings | Should | S | `pages/admin_settings.py` | none |
| **U1-07** | US-602 Surprise me | Could | S | `pages/home.py` | U1-03 |
| **U1-08** | US-707 Owner dashboard | Could | M | `pages/admin_dashboard.py` | none |

What to build:
- **U1-01:** a 3-column grid on desktop (1 on mobile) of product cards (image, name, "from $X.XX", stock badge, "Build this bag" button); a flavor library section; inactive items hidden.
- **U1-02:** a search box that calls `catalog.search()`; the search word kept in the link (`?q=`); a results count; a friendly no-results message with suggestions.
- **U1-03:** hero, "How it works", featured chips, a row of flavor tiles, and a slot for `staff_picks_row()`.
- **U1-04:** style, family, heat, in-stock and price filters (sidebar on desktop, expander on mobile), working together with search; "Clear filters".
- **U1-05:** the sort dropdown, with the choice kept when filters change.
- **U1-06:** `require_role("owner")`; the settings form with checks; save.
- **U1-07:** a "Surprise me" button that calls `catalog.random_combo()` and opens the product page with `?flavors=`.
- **U1-08:** `require_role("owner")`; 3 stat tiles and a "top 5 flavors" chart.

### User 2: Product & Cart lane

| Pick | Story | Pri | Size | Files | Depends on |
|------|-------|-----|------|-------|------------|
| **U2-01** | US-201 View chip details | Must | M | `pages/product.py` | none |
| **U2-02** | US-202 Flavor tile and details | Must | S | `components/flavor_tile.py` | none |
| **U2-03** | US-301 Build a bag | Must | L | `components/bag_builder.py`, `components/price_summary.py`, `tests/unit/test_bag_builder.py` | U2-01, U2-02 |
| **U2-04** | US-302 Add the bag to the cart | Must | S | `components/bag_builder.py`, `components/qty_stepper.py` | U2-03 |
| **U2-05** | US-203 Allergens before buying | Must | S | `components/bag_builder.py` | U2-03 |
| **U2-06** | US-303 View the cart | Must | M | `pages/cart.py` | none |
| **U2-07** | US-304 Change or remove cart items | Must | S | `pages/cart.py` | U2-06 |
| **U2-08** | US-601 Staff picks combos | Should | S | `components/staff_picks.py`, `pages/product.py` | U2-03 |
| **U2-09** | US-603 Flavor passport | Could | M | `components/flavor_passport.py` | none |

What to build:
- **U2-01:** reads `?id=`; image, name, description, price, stock badge, chip facts; 2 columns on desktop, stacked on mobile; "not found" for a bad ID.
- **U2-02:** icon, name, price, 4 profile bars with numbers; selected (check mark), sold-out and disabled states; a details popover with description and allergens.
- **U2-03:** base selector; flavor tiles grouped by family; the "2 of 3 chosen" counter (using `check_flavor_limit` and the max from settings); sold-out items can't be picked; a live price from `bag_price`; pre-fill from `?flavors=`. Unit tests: the limit, sold out, the price.
- **U2-04:** quantity 1 to the lowest stock; the button disabled until the choices are valid; `cart.add_bag` (or the guest cart); the "Bag added!" toast; the same bag adds to its quantity.
- **U2-05:** the combined, de-duplicated allergens above the button, updated as choices change.
- **U2-06:** cart lines, the summary card, the empty state; works for guests and customers. Test with the seeded cart.
- **U2-07:** quantity steppers capped at stock; remove; totals update right away; stock warnings.
- **U2-08:** up to 3 staff pick cards; choosing one fills in the builder; also fill in `staff_picks_row()` for the home page.
- **U2-09:** a stamp grid from `orders.flavors_tried()`; the "7 of 10" counter; 3 badges; no pressure wording.

### User 3: Accounts & Admin lane

| Pick | Story | Pri | Size | Files | Depends on |
|------|-------|-----|------|-------|------------|
| **U3-01** | US-502 Sign in and sign out | Must | M | `pages/sign_in.py`, `components/header.py` | none |
| **U3-02** | US-501 Register | Must | M | `pages/register.py` | none |
| **U3-03** | US-701 Manage base chips | Must | L | `pages/admin_chips.py` | none |
| **U3-04** | US-702 Manage flavors | Must | L | `pages/admin_flavors.py` | U3-03 (same page pattern) |
| **U3-05** | US-703 Manage stock | Must | M | `pages/admin_stock.py` | none |
| **U3-06** | US-705 Manage staff | Must | M | `pages/admin_staff.py`, `tests/integration/test_roles.py` | none |
| **U3-07** | US-503 Reset password | Should | S | `pages/reset_password.py` | U3-01 |
| **U3-08** | US-505 My profile | Could | S | `components/profile_form.py` | none |

What to build:
- **U3-01:** an email and password form; one general error message; return to the page in `?next=`; the header shows the name, cart count and "Sign out"; signing out clears the session. Test with the 3 seeded accounts.
- **U3-02:** the form with a live password-rules checklist; an "already registered" message; the user is signed in afterwards.
- **U3-03:** `require_role("staff","owner")`; a searchable table; an add/edit form with checks; image upload (type and size checked); alt text; hide with a confirmation step.
- **U3-04:** the same pattern, plus family, profile sliders, allergens, add-on price, and a staff picks tab.
- **U3-05:** an editable table (`st.data_editor`); low-stock rows highlighted with an icon; a reason is required; calls `set_stock`; a history tab.
- **U3-06:** `require_role("owner")`; find a user by email; change their role with a confirmation step; the owner's own row is locked. Integration test: staff can't change roles, even directly in the database.
- **U3-07:** the "Forgot password?" page; the same message whatever the email; the README says where to find the local reset email.
- **U3-08:** a display name and default address form, which checkout uses to fill in the address.

---

## 6. Cross-user dependencies

Only a few links cross between users. **None of them block merging**, because the foundation already has a placeholder on the other side. They only affect when the **full** experience can be seen working.

| Story | Needs | From | Until then |
|-------|-------|------|------------|
| U1-03 Home: staff picks row | U2-08 fills in `staff_picks_row()` | User 2 | The home page shows the placeholder (empty row) |
| U1-07 Surprise me | U2-03 reads `?flavors=` | User 2 | The product page opens without the flavors pre-filled |
| U2-06 Cart: "Checkout" button | L-02 checkout page | Lead | The button opens the "Coming soon" placeholder |
| L-02 Checkout: sign-in redirect | U3-01 sign-in page | User 3 | Sign in with the seeded customer through the foundation sign-in |
| L-05 Keep cart on sign-in (end-to-end check) | U3-01 sign-in page | User 3 | Unit tests cover the merge; check it end to end after U3-01 |
| L-06 My account: Profile and Passport tabs | U3-08, U2-09 | Users 3 and 2 | The tabs show the placeholder components |
| U2-03 Max flavors from settings | U1-06 settings screen | User 1 | Uses the seeded setting (3) |

Rule: if your story touches one of these links, **mention the other person in the PR** so they know.

---

## 7. GitHub setup

### 7.1 Labels

| Group | Labels |
|-------|--------|
| Who | `user:lead`, `user:1`, `user:2`, `user:3` |
| Epic | `epic:E1`, `epic:E2`, `epic:E3`, `epic:E4`, `epic:E5`, `epic:E6`, `epic:E7`, `foundation` |
| Type | `type:story`, `type:task`, `type:bug`, `type:docs` |
| Priority | `priority:must`, `priority:should`, `priority:could` |
| Size | `size:S`, `size:M`, `size:L` |
| Flags | `schema-change` (changes `supabase/`; the Lead must review), `blocked` (waiting on something; say what in a comment) |

### 7.2 Milestones

| Milestone | Contains |
|-----------|----------|
| **Foundation** | F1–F15, U1-00, U2-00, U3-00 |
| **Stories** | All L-, U1-, U2- and U3- stories |
| **Release v1.0** | Bug fixes and release tasks (section 10) |

### 7.3 Board and repo rules
- Project board: **Backlog → To do → In progress → In review → Done**
- `main` is protected: PR required, 1 approval, CI must pass, no force push. Admins can bypass only until F15.
- Squash merging only; head branches are deleted automatically after merging.
- `CODEOWNERS` follows section 3.
- Secrets live in **Settings → Secrets and variables**, never in files.

### 7.4 Issue format

```
Title:  [U2-03] US-301 Build a bag
Labels: user:2, epic:E3, type:story, priority:must, size:L
Milestone: Stories

Story: As a shopper, I want to pick a base chip and choose flavors so that I get the combination I want.

Acceptance criteria
- [ ] AC1 I choose exactly one base chip
- [ ] AC2 …

Files: components/bag_builder.py, components/price_summary.py
Depends on: #<U2-01 issue>, #<U2-02 issue>
Screens: S3 · NFRs: NFR-DI-02
```

---

## 8. Workflow for one story

```bash
# 1. Start from the latest main
git checkout main
git pull

# 2. One branch per story
git checkout -b feat/U2-03-build-a-bag

# 3. Build and test. Commit on the branch as often as you like.
streamlit run app/main.py
ruff check .
pytest
git add app/components/bag_builder.py tests/unit/test_bag_builder.py
git commit -m "wip: flavor limit"

# 4. Push and open a PR
git push -u origin feat/U2-03-build-a-bag
gh pr create --title "feat(cart): U2-03 US-301 build your bag panel" --body "Closes #23"
```

1. In the PR: `Closes #<issue>`, what changed, how to test it, and screenshots (desktop and mobile). Move the issue to **In review**.
2. The reviewer (set by CODEOWNERS, or any teammate) pulls the branch, runs it, and goes through the checklist in section 9.
3. Fix review comments with more commits on the same branch.
4. When it's approved and CI is green, the **author** clicks **Squash and merge** and checks that the commit title matches the format in section 2.
5. Everyone runs `git checkout main && git pull` before starting their next story.

If your branch falls behind `main`: `git merge origin/main`, fix any conflicts, run the tests, and push.

---

## 9. Quality gates

### Reviewer checklist
- [ ] I ran it, and every acceptance criterion works
- [ ] Tests were added, and CI is green
- [ ] No keys, passwords, `.env` or `secrets.toml`
- [ ] Pages only use `app/services`; there are no direct Supabase calls
- [ ] New tables have RLS; new pages have the right guard
- [ ] User text isn't shown as raw HTML
- [ ] It matches the wireframes and the tone of voice; empty, loading and error states are handled
- [ ] It's one story in one PR, and the title follows the commit format

### Definition of Done
- [ ] Acceptance criteria met
- [ ] Tests added or updated; CI passes
- [ ] Approved by 1 reviewer (and by the Lead if it's labelled `schema-change`)
- [ ] Squash-merged as **one commit** on `main`
- [ ] Works on staging after the deploy
- [ ] Docs updated if behavior changed

---

## 10. Phase 3: Bringing it all together and releasing

**Merging is continuous.** Every story is merged into `main` as soon as it's approved, so there's no big "merge everything" day. Staging is deployed from `main`, so the whole team always sees the current product. In the **middle of Phase 2**, hold a checkpoint demo of Flow A (doc 02) on staging to make sure the lanes fit together.

### Step 1: Feature freeze
- All Must stories are merged. Unfinished Should and Could stories move to a "Release 2" milestone.
- From now on, only `fix/` PRs are merged, still one commit each.

### Step 2: Release candidate
```bash
git checkout main && git pull
git tag -a v1.0.0-rc.1 -m "Release candidate 1"
git push origin v1.0.0-rc.1
```
Deploy this tag to staging, and reset the staging database with the migrations and seed data.

### Step 3: Test on staging
Each person tests a lane they **didn't** build, using the U2-00 and U3-00 test cases:

| Tester | Tests the work of |
|--------|-------------------|
| Lead | User 1: Discover |
| User 1 | User 2: Product & Cart |
| User 2 | User 3: Accounts & Admin |
| User 3 | Lead: Checkout & Orders |

Then everyone tests these together:
- **Flow A from start to finish:** home → search → product → build a bag → cart → sign in (the cart is kept) → checkout → confirmation → the `.eml` file → My orders → stock went down
- **Security:** a customer opens an admin link and sees "Not authorized"; staff can't change roles; customer A can't open customer B's order by changing `?order=`
- **Stock:** two browsers buy the last bag at the same time, and only one order succeeds
- **Phone and accessibility:** Flow A at phone width, and using only the keyboard
- **Content:** all content is age-appropriate, and the demo banner is visible

Each problem becomes an issue (`type:bug`, milestone Release v1.0). It's fixed with one `fix/` PR. Then tag `v1.0.0-rc.2` and test again.

### Step 4: Release
When there are no open Must bugs:
```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
gh release create v1.0.0 --generate-notes
```
- The generated release notes list every story, because there's one commit per story.
- Deploy `v1.0.0` to **production**, which has its own Supabase project and its own secrets. Apply the migrations, run the seed script, and change the demo passwords.
- **Smoke test (10 minutes):** open the home page, sign in, place one order, open the admin pages.
- **Rollback:** redeploy the previous tag; or `git revert <commit>` and release `v1.0.1`.

### Step 5: Demo and retro
- Each person demos their lane (5 minutes each), then Flow A is shown from start to finish.
- Retro: what to keep, what to change, and what goes into the Release 2 backlog.

### Release checklist (Lead)
- [ ] All Must stories are Done, and there are no open Must bugs
- [ ] CI is green on the commit being tagged
- [ ] Migrations run cleanly on an empty database
- [ ] No secrets in the repo
- [ ] RLS is on for every table (check in the Supabase dashboard)
- [ ] README and deployment docs are up to date; ADRs are recorded
- [ ] `v1.0.0` is tagged, the GitHub Release is published, and the production smoke test passed

---

## 11. Team routines and risks

| Routine | When | What |
|---------|------|------|
| Stand-up | Daily, 10 minutes | Done / doing / blocked (add the `blocked` label if needed) |
| Review check | Late morning and late afternoon | Clear the "In review" column. No PR waits more than half a day. |
| Design review | End of week 1 | User 1 presents the wireframes |
| Checkpoint demo | Middle of Phase 2 | Flow A on staging |
| Retro | End of each week | Keep / change / try |

| Risk | What we do |
|------|-----------|
| The foundation takes longer than a week | Users 1–3 keep working on docs tasks; lanes start once F14 is merged |
| A lane needs a missing service function | Add it in the story's PR; the Lead reviews it (CODEOWNERS) |
| Conflicts in the same file | File ownership (section 3) and one story at a time |
| A lane falls behind | Should and Could stories move to the end; whoever is free reviews or helps |
| A late bug breaks another lane | Revert that one story commit, fix it, merge again |
| Someone is away | Their branch and PR are on GitHub; their reviewer can continue the work |
