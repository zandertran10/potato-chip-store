# Team Work Plan

How our team of 4 builds Release 1 on GitHub with as few dependencies as possible.

Based on: `docs/requirements/` (story IDs such as `US-01.1` come from `product-features-stories.md`).

---

## 1. The idea in one picture

```
PHASE 1: FOUNDATION (Lead only)            PHASE 2: STORIES (everyone)                 PHASE 3: FINISH
┌─────────────────────────────┐            ┌──────────────────────────────────┐        ┌──────────────────┐
│ Database, RLS, seed data    │            │ Pick 1 story → branch → commit   │        │ Full test run    │
│ Services (all data calls)   │  merge to  │ → pull request → review → merge  │  all   │ Bug fixes        │
│ Sign-in + role helpers      │ ─────────► │ → pick the next story            │ ─────► │ Tag v1.0.0       │
│ App skeleton + empty pages  │   main     │                                  │ merged │ Demo             │
│ Theme + shared components   │ (v0.1.0)   │ 4 people working in parallel     │        │                  │
│ GitHub setup + CI + issues  │            │                                  │        │                  │
└─────────────────────────────┘            └──────────────────────────────────┘        └──────────────────┘
```

**Why this removes dependencies:** the Lead builds everything that stories share **before** anyone starts a story. After that, each story only fills in its own page or adds to its own piece. It uses functions that already exist and work, so no one waits for anyone else.

---

## 2. Roles

| Person | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **Lead** (Member 1) | Builds the foundation | Picks stories like everyone else; reviews all database changes | Runs the release |
| **Members 2–4** | Prepare (see section 3.3); no app code yet | Pick stories one at a time | Testing and bug fixes |

---

## 3. Phase 1: Foundation (Lead)

The Lead works on one branch, `foundation`, and merges it to `main` with one pull request. Another member reviews it, which is a good way for them to learn the codebase.

### 3.1 Foundation checklist

**Database (`supabase/`)**
- [ ] Migrations for **all** tables: `profiles` (with role), `base_chips`, `flavors`, `carts`, `cart_items`, `cart_item_flavors`, `orders`, `order_items`, `order_item_flavors`, `stock_history`, `settings`, `staff_picks`
- [ ] **RLS enabled on every table**, with policies for guest / customer / staff / owner (NFR-AZ-01 to 05)
- [ ] Constraints: `price > 0`, `stock >= 0`, role values limited to the three roles
- [ ] `place_order` database function: checks stock, deducts it, creates the order, all in one step, safe against double clicks (NFR-DI-01 to 05)
- [ ] `cancel_order` database function that puts stock back
- [ ] Trigger that creates a `profiles` row with role `customer` for every new sign-up
- [ ] Seed data: 4 base chips, 10 flavors, 3 staff picks, 1 owner account, 1 staff account, 1 customer account (all fake, age-appropriate)
- [ ] Storage bucket for product images (public read, staff write)

**Services layer (`app/services/`)**: every database call the stories will need, working against real Supabase:
- [ ] `catalog.py`: `list_base_chips()`, `get_base_chip(id)`, `list_flavors()`, `search(query, filters, sort)`, `list_staff_picks(base_id)`
- [ ] `cart.py`: `get_cart()`, `add_bag(base_id, flavor_ids, qty)`, `update_qty(line_id, qty)`, `remove_line(line_id)`, `merge_guest_cart(guest_cart)`
- [ ] `orders.py`: `place_order(address, idempotency_key)`, `list_my_orders()`, `get_order(id)`, `list_all_orders(filters)`, `set_status(id, status)`, `cancel_order(id)`
- [ ] `admin.py`: `save_base_chip(data)`, `save_flavor(data)`, `set_stock(item, qty, reason)`, `upload_image(file)`, `set_role(user_id, role)`, `get_settings()`, `save_settings(data)`
- [ ] `auth.py`: `sign_up()`, `sign_in()`, `sign_out()`, `reset_password()`, `current_user()`, `current_role()`
- [ ] `supabase_client.py`: reads keys from `st.secrets` / environment variables only

**Shared helpers (`app/utils/`)**
- [ ] `pricing.py`: bag price calculation and flavor limit check (BR-01, BR-02), with tests
- [ ] `guards.py`: `require_login()`, `require_role("staff")` for pages (NFR-AZ-06)
- [ ] `outbox.py`: `write_confirmation_email(order)` → `outbox/order-<number>.eml` (BR-09)
- [ ] `session.py`: guest cart and user session in `st.session_state`

**App skeleton (`app/`)**
- [ ] `app/main.py` with navigation listing **every page** in the site map (UI/UX doc, section 3)
- [ ] **One file per page** in `app/pages/`, each showing only its title and "Coming soon". Stories fill these in.
- [ ] Admin pages already protected by `require_role`
- [ ] Theme in `.streamlit/config.toml`; shared components in `app/components/` (product card, flavor tile, badges, quantity stepper, empty state, price summary) as simple first versions
- [ ] Friendly error page and "Supabase can't be reached" message (NFR-OPS-01)

**Tests and tooling**
- [ ] `pytest` set up with tests for `pricing.py` and `place_order` (including the "last bag" and double-click cases)
- [ ] `ruff` for code style
- [ ] `README.md`: how to run locally (install, `secrets.toml`, migrate, seed, `streamlit run app/main.py`)
- [ ] ADR for hosting (ADR 0001) and any other big choices

**GitHub setup**
- [ ] Branch protection on `main`: pull request + 1 approval + CI must pass, no force push
- [ ] GitHub Actions CI: install requirements, `ruff`, `pytest`
- [ ] Pull request template (with the Definition of Done checklist) and issue template
- [ ] Labels, milestones, and the Project board (section 5)
- [ ] **One issue per story** from section 4, with its acceptance criteria pasted in as a checklist

### 3.2 Foundation "done" test
Before merging, the Lead shows that:
1. A fresh clone runs by following the README
2. Every page opens (most just say "Coming soon")
3. The seed owner, staff, and customer accounts can sign in, and the admin pages block the customer
4. `place_order` works when called from a test
5. CI is green

Then the Lead merges and tags `v0.1.0-foundation`. **Phase 2 starts.**

### 3.3 What Members 2–4 do during Phase 1
They don't write app code yet. They:
- set up their computer (Python, Git, a local Supabase or access to the shared test project) and clone the repo
- read `docs/requirements/`
- do the design tasks (wireframes and mockups from the UI/UX doc, section 9). Each one is a **docs-only pull request** into `docs/design/wireframes/`, so it won't conflict with the Lead's work.
- write test cases from the acceptance criteria of the stories they plan to pick first
- review the Lead's foundation pull request when it's ready

---

## 4. Phase 2: Story list

Every story below depends **only on the foundation**, unless the "Note" column says otherwise. Size: **S** = about half a day, **M** = 1 day, **L** = 2 days.

| Issue | Story | Main file(s) touched | Size | Note |
|-------|-------|----------------------|------|------|
| US-03.4 | Shop page (browse all) | `pages/shop.py` | M | |
| US-03.1 | Search by keyword | `pages/shop.py` | S | Pick after US-03.4 (same file) |
| US-03.2 | Filters | `pages/shop.py` | M | Pick after US-03.1 |
| US-03.3 | Sort | `pages/shop.py` | S | Pick after US-03.1 |
| UX-PG-01 | Home page | `pages/home.py` | M | |
| US-04.1 | Product detail page | `pages/product.py` | M | |
| US-04.2 | Flavor details | `components/flavor_tile.py` | S | |
| US-04.4 | Allergen info | `pages/product.py` | S | Pick after US-04.1 |
| US-01.1 | Build Your Bag panel | `components/bag_builder.py` | L | |
| US-01.2 | Add bag to cart | `components/bag_builder.py` | S | Pick after US-01.1 |
| US-04.3 | Staff picks combos | `pages/product.py` | S | Pick after US-01.1 |
| US-01.6 | Surprise me | `components/bag_builder.py` | S | Could |
| US-01.3 | View cart | `pages/cart.py` | M | Test with a seeded cart |
| US-01.4 | Change / remove cart items | `pages/cart.py` | S | Pick after US-01.3 |
| US-01.5 | Keep cart on sign-in | `utils/session.py` | S | |
| US-02.1 | Checkout review page | `pages/checkout.py` | M | |
| US-02.2 | Place order | `pages/checkout.py` | M | Pick after US-02.1 |
| US-02.3 | Confirmation page | `pages/confirmation.py` | S | |
| US-02.4 | Outbox email content and format | `utils/outbox.py` | S | |
| US-05.1 | Register page | `pages/register.py` | M | |
| US-05.2 | Sign in / sign out | `pages/sign_in.py`, header | M | |
| US-05.3 | Reset password | `pages/sign_in.py` | S | Should; pick after US-05.2 |
| US-05.4 | My orders | `pages/my_orders.py` | M | Test with seeded orders |
| US-05.5 | My profile | `pages/account.py` | S | Could |
| US-06.1 | Admin: manage base chips | `pages/admin_products.py` | L | |
| US-06.2 | Admin: manage flavors | `pages/admin_flavors.py` | L | |
| US-06.3 | Admin: stock | `pages/admin_stock.py` | M | |
| US-06.4 | Admin: orders | `pages/admin_orders.py` | M | |
| US-06.5 | Admin: manage staff | `pages/admin_staff.py` | M | |
| US-06.6 | Admin: settings | `pages/admin_settings.py` | S | Should |
| US-06.7 | Owner dashboard | `pages/admin_dashboard.py` | M | Could |

**Pick "Must" stories first.** Only start a "Should" or "Could" story when no "Must" story is left in "To do".

The "Pick after" notes are there only because two stories edit the **same file**. Doing them in order avoids merge conflicts; it is not a waiting dependency, because there is always another story available.

### 4.1 Suggested first picks (so everyone starts on a different file)

| Person | 1st story | 2nd story |
|--------|-----------|-----------|
| Lead | US-02.1 Checkout review | US-02.2 Place order |
| Member 2 | US-03.4 Shop page | UX-PG-01 Home |
| Member 3 | US-01.1 Build Your Bag | US-04.1 Product detail |
| Member 4 | US-05.2 Sign in / out | US-06.1 Admin: base chips |

After that, anyone picks the next "Must" story at the top of the "To do" column.

---

## 5. Phase 2: How one story goes from start to merge

### 5.1 Rules
- **One story at a time per person.** Finish it (merged) before picking another.
- **One story = one branch = one pull request.**
- Pull requests should be small: one story, ideally under about 300 changed lines.
- Don't change foundation files (`app/services/`, `supabase/`, `app/utils/`, `app/main.py`) inside a story unless the story needs it. If it does, keep the change small and say so in the pull request. The Lead reviews it.

### 5.2 Steps

**1. Pick the story**
On the Project board, take the top issue in **To do**, assign it to yourself, and move it to **In progress**.

**2. Start a branch from the latest `main`**
```bash
git checkout main
git pull
git checkout -b feature/US-03.4-shop-page
```

**3. Build and commit in small steps**
```bash
git add app/pages/shop.py tests/test_shop.py
git commit -m "US-03.4: show active base chips in a grid"
```
Start every commit message with the story ID. Run the app and `pytest` locally before pushing.

**4. Push and open a pull request**
```bash
git push -u origin feature/US-03.4-shop-page
```
On GitHub, open a pull request into `main`:
- Title: `US-03.4 Shop page`
- Description: `Closes #<issue number>`, what changed, how to test, and a screenshot of the page
- Tick the Definition of Done checklist (section 5.4)

Move the issue to **In review**.

**5. Review**
- Any one teammate reviews it, using the checklist in section 5.3. Pull requests that change `supabase/` must be reviewed by the Lead.
- The reviewer checks out the branch, runs it, and either **approves** or **requests changes**.
- Aim to review within a few hours, because a waiting pull request blocks its author.
- The author fixes the comments with new commits on the same branch.

**6. Merge**
- When the pull request is approved and CI is green, the **author** clicks **Squash and merge**, then deletes the branch.
- The issue closes automatically and moves to **Done**.

**7. Everyone stays up to date**
Before starting the next story, run `git checkout main` and `git pull`. If your open branch falls behind `main`, run `git merge main` on your branch and fix any conflicts.

**8. Pick the next story** (back to step 1).

### 5.3 Reviewer checklist
- [ ] The story's acceptance criteria all work when I run it
- [ ] Tests added, and CI is green
- [ ] No keys, passwords, or `.env` / `secrets.toml` in the changes
- [ ] Data is read and written only through `app/services/`
- [ ] Any new table has RLS turned on
- [ ] User text isn't shown as raw HTML
- [ ] The page matches the UI/UX doc (colors, wording, empty and error states)
- [ ] The code is easy to read

### 5.4 Definition of Done (one story)
- [ ] All acceptance criteria met
- [ ] Tests added or updated, and CI passes
- [ ] Reviewed and approved by one teammate
- [ ] Merged to `main` with squash
- [ ] Docs updated if behavior changed

---

## 6. Phase 3: Finish

When every "Must" story is merged:
1. **Freeze:** only bug-fix pull requests are merged (branch name `fix/<issue>-<short-name>`).
2. **Full test run:** each person tests a flow they did *not* build:
   - shopper: search → product → build bag → cart → sign in → checkout → confirmation → check the `.eml` file in `outbox/` → My orders
   - staff: add a product, restock, view and update the order
   - owner: make a user staff, change settings
   - security: a customer opens an admin page and sees "Not authorized"; two users buy the last bag at the same time
3. Log bugs as issues labelled `type:bug`, fix them with the same story flow (section 5).
4. The Lead tags `v1.0.0` on `main` and creates a **GitHub Release** with notes.
5. Demo.

---

## 7. GitHub setup reference

| Item | Setting |
|------|---------|
| Labels | `feature:F-01`…`F-06`, `foundation`, `design`, `type:story`, `type:bug`, `type:docs`, `priority:must`, `priority:should`, `priority:could`, `size:S/M/L` |
| Milestones | `Phase 1: Foundation`, `Phase 2: Stories`, `Phase 3: Release` |
| Project board | Backlog → To do → In progress → In review → Done |
| Branch names | `foundation`, `feature/<story-id>-<short-name>`, `fix/<issue>-<short-name>`, `docs/<short-name>` |
| Merge method | Squash and merge only |
| Tags | `v0.1.0-foundation`, `v1.0.0` |
| Secrets | Never in the repo. Each person has their own local `.streamlit/secrets.toml`; CI and hosting keys go in GitHub → Settings → Secrets |

## 8. Team routines

| Routine | When | What |
|---------|------|------|
| Stand-up | Daily, 10 min (or a written comment on a pinned issue) | Done / doing / blocked |
| Review check | Twice a day | Look at the "In review" column and review anything waiting |
| Weekly demo | End of each week | Show merged stories |

## 9. Risks

| Risk | What we do |
|------|-----------|
| Phase 1 takes longer than planned | Members 2–4 use the time for design and test cases; the Lead can merge the foundation in 2 pull requests (database + services first, then skeleton + GitHub setup) |
| Two people change the same file | One story at a time per person, "Pick after" notes, pull `main` often |
| A story needs a service function that's missing | Add it in that story's pull request, keep it small, Lead reviews |
| Pull requests wait too long for review | Review check twice a day; any teammate can review |
| Someone leaves mid-story | Their branch and pull request are on GitHub; anyone can continue it |
