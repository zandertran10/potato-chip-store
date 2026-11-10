# 02: UI / UX Requirements

- **Audience:** The UI/UX designer who will create wireframes and mockups. Developers use it to build the screens.
- **Vision:** "Professional, yet lighthearted. It should create curiosity to buy from the website. The UI design should help people buy."
- **Stories:** Each screen links to the user stories in `01-product-features-user-stories.md`.

---

## 1. What the vision means

| Word | What it means for the design | What it does NOT mean |
|------|------------------------------|-----------------------|
| **Professional** | Clean grid, plenty of space, one main action per screen, consistent components, sharp product photos, prices and stock always easy to see | Cold or corporate; cluttered pages full of offers |
| **Lighthearted** | Warm colors, rounded shapes, friendly wording, small moments of delight (adding to cart, order placed) | Childish or cartoon-heavy styling; jokes that hide important information; lots of animation |
| **Curiosity** | The flavor combination is the star: flavor tiles with taste profiles, staff picks, "Surprise me", the flavor passport, "New" badges | Fake urgency, made-up countdowns, hidden prices, tricks |
| **Help people buy** | A short path from home to checkout, the builder right on the product page, live price, visible cart count, stock and allergens shown before adding | Extra steps, surprise errors at checkout, forcing sign-in before browsing |

## 2. Design principles

1. **Clear first, fun second.** Every playful touch should also help the shopper decide or act.
2. **The bag is the hero.** The Build Your Bag panel (S3) gets the most design attention.
3. **Show, don't hide.** Price, stock and allergens are always visible before the shopper commits.
4. **One main action per screen.** Use one primary (gold) button per screen.
5. **Every state is designed.** Loading, empty, error and success states are part of every screen.
6. **Honest by design.** No dark patterns, no fake scarcity, no pressure (section 4).
7. **Built for Streamlit.** Designs fit what Streamlit can do (section 10).

## 3. Visual direction

### 3.1 Mood
A friendly snack shop with a craft feel: warm golden colors, crunchy close-up textures, clean layouts. Think "proud snack-maker sharing their recipes".

### 3.2 Color tokens
These match `.streamlit/config.toml`. If the designer changes them, the config file must be updated too.

| Token | Hex | Use |
|-------|-----|-----|
| `primary` (Golden Chip) | `#E0A526` | Main buttons, highlights, selected states |
| `background` (Cream) | `#FFFDF7` | Page background |
| `surface` (Butter) | `#FFF3D6` | Cards, sidebar, panels |
| `text` (Toasted Brown) | `#3B2A1A` | Body text and headings |
| `accent-heat` (Paprika) | `#D9480F` | Heat levels, "New" badges (use sparingly) |
| `success` (Herb Green) | `#2F9E44` | In stock, success messages |
| `danger` (Error Red) | `#C92A2A` | Errors, sold out |

Gold text on cream is too faint to read. Use gold as a fill with brown text on top.

### 3.3 Typography
- Headings: a rounded, friendly sans serif (Nunito or Poppins)
- Body: a clean sans serif (Streamlit's default sans or Inter), at least 16 px
- Prices and numbers: tabular (fixed-width) digits so columns line up

### 3.4 Icons and images
- Product photos: bright close-ups on a plain warm background, all with the same lighting and angle
- Flavors: a simple icon or ingredient photo each (lime, chili, onion…), plus a color tag for the flavor family
- Icons: one set with a rounded line style (for example Material Symbols Rounded, which Streamlit supports)
- Optional: a simple chip mascot for empty states and the 404 page

## 4. How playful features appear in the UI (ethically)

The store uses light game-like touches (epic E6) to spark curiosity. They must be honest.

| Feature | Where | How it looks |
|---------|-------|--------------|
| Flavor profile bars | S2, S3 | Four small 0–3 bars (salty, tangy, sweet, heat), with numbers |
| Staff picks (US-601) | S1, S3 | Cards with a "Staff pick" badge; one click fills in the builder |
| Surprise me (US-602) | S1 | A secondary button with a dice icon |
| Flavor passport (US-603) | S10 | A grid of flavor stamps (filled = tried), a counter, and 3 badges |
| Bag added | S3 | A short toast "Bag added!" and the cart count grows |
| Order placed | S6 | One short celebration (balloons or an illustration) |

**Ethics rules (must follow):**
- No countdown timers and no "offer ends soon".
- "Few left" only appears when real stock is low (at or below the threshold in settings).
- No streaks, leaderboards, or messages like "Don't lose your progress!".
- Badges are only rewards for exploring. They never unlock discounts or block anything.
- All motion can be turned off with the device's "reduce motion" setting.

## 5. Sitemap and navigation

```
Header: Logo | Search | Shop | Account or Sign in | Cart (count)
│
├── S1  Home
├── S2  Shop / Search results
│       └── S3  Product detail + Build Your Bag
├── S4  Cart
├── S5  Checkout ──► S6 Order confirmation
├── S7  Sign in ── S9 Reset password
├── S8  Register
├── S10 My account (orders, profile, flavor passport)
└── Store Admin (staff and owner only)
        ├── S11 Base chips
        ├── S12 Flavors and staff picks
        ├── S13 Stock
        ├── S14 Orders
        └── S15 Staff, settings, dashboard (owner only)
S16 System states: loading, empty, error, not found, not authorized, offline
```

Navigation rules:
- The cart count and search are visible on every customer screen.
- Admin pages are hidden from navigation for guests and customers, and they're also blocked if someone opens the link directly.
- Admin pages use the same brand but a calmer, denser layout, with a clear "Store Admin" label.

## 6. Key user flows

**Flow A: First-time shopper buys a bag (the main flow)**
S1 Home → "Build your bag" → S3 Product (choose base, pick 2 flavors, see price and allergens) → Add to cart → toast → S4 Cart → Checkout → S7 Sign in / S8 Register → back to S5 Checkout (cart kept) → Place order → S6 Confirmation

**Flow B: Shopper searches for a flavor**
Any screen → search "lime" → S2 results → filter "Tangy" → S3 product → build and add

**Flow C: Curious shopper uses staff picks or Surprise me**
S1 → choose a Staff pick (or Surprise me) → S3 with the builder filled in → change one flavor → add to cart

**Flow D: Returning customer checks an order**
Sign in → S10 My account → My orders → open an order → see the flavor passport stamps

**Flow E: Staff restock and fulfil**
Sign in as staff → S13 Stock (low items highlighted) → restock with a reason → S14 Orders → open an order → status Packed → Shipped

**Flow F: Owner adds a staff member**
Sign in as owner → S15 Staff → find a user by email → make them staff → confirm

## 7. Screen-by-screen requirements

For every screen, the designer provides **default, loading, empty and error** states at **desktop (1280 px)** and **mobile (390 px)** widths.

### S1 Home · US-101, US-601, US-602
- Hero: a short headline about building your own bag, a "Build your bag" main button and a "Browse flavors" second button
- "How it works" in 3 steps
- Featured chips (3–4 product cards)
- Staff pick cards, and a "Surprise me" button
- A row of flavor tiles (the flavor library teaser)

### S2 Shop / Search results · US-102, US-103, US-104, US-105
- Search box with the current search word shown ("12 results for 'bbq'")
- Filters in the sidebar on desktop, in an expandable section on mobile; a sort dropdown
- Product card: image, name, "from $X.XX", stock badge, "New" or "Few left" badge, "Build this bag" button
- Flavor library section with flavor tiles
- No results: a friendly message, "Clear filters", and suggested items

### S3 Product detail + Build Your Bag · US-201, US-202, US-203, US-301, US-302, US-601 (key screen)
- Left on desktop, top on mobile: large image, name, description, chip facts (style, thickness, crunch meter)
- Right on desktop, below on mobile: **Build Your Bag**
  1. Base chip (selected already, can be switched)
  2. Flavor tiles grouped by family: icon, name, add-on price, profile bars. Selected tiles have a check mark (not only a color change). Sold-out tiles are greyed out and labeled.
  3. Counter: "2 of 3 flavors chosen"
  4. Combined allergens
  5. Quantity stepper
  6. Live summary: base + flavors = **total**
  7. "Add to cart" main button
- Staff pick cards for this chip
- After adding: a toast with a "View cart" link

### S4 Cart · US-303, US-304
- Lines: small image, base name, flavor tags, unit price, quantity stepper, line total, remove link
- Summary card: bag count, subtotal, "Checkout" main button, "Keep shopping" link
- A warning on any line where stock dropped below the quantity
- Empty state with an illustration and a "Build your bag" button

### S5 Checkout · US-401, US-402
- Steps at the top: Cart → Details → Done
- Delivery name and address form
- Order summary (read only, with a link back to the cart)
- "Demo store: no payment needed" banner
- "Place order" main button with a loading state. It is disabled while the order is being placed.
- An out-of-stock message that lists what changed

### S6 Order confirmation · US-403, US-404
- A short celebration
- Order number shown large, the items, total and date
- "We've emailed your confirmation to name@example.com"
- "View my orders" and "Keep shopping" buttons

### S7 Sign in · US-502
- A centered card with email, password, "Sign in", a "Forgot password?" link and a link to Register
- A short reason to register: "Save your bags and track your orders"

### S8 Register · US-501
- Display name, email, password and confirmation fields
- A password-rules checklist that ticks off as the shopper types
- Errors shown next to the field they belong to

### S9 Reset password · US-503
- Email field and a "Send reset link" button
- The same success message whether or not the email exists

### S10 My account · US-504, US-505, US-603
- Tabs: Orders, Profile, Flavor passport
- Orders: list (number, date, total, status badge) → order detail
- Profile: display name and default address form
- Flavor passport: a grid of stamps, the "7 of 10 tried" counter, and badges

### S11 Admin: Base chips · US-701
- A searchable table: image, name, price, stock, active, featured, edit
- An "Add new" button; the add/edit form includes image upload with a preview and an alt-text field
- Hiding an item asks for confirmation

### S12 Admin: Flavors and staff picks · US-702
- The same pattern as S11, plus family, profile sliders (0–3), allergens (multi-select) and add-on price
- A "Staff picks" tab: choose a chip, then set up to 3 combos

### S13 Admin: Stock · US-703
- One editable table of all chips and flavors
- Low-stock rows highlighted with an icon as well as a color
- A reason is required when saving
- A stock history tab

### S14 Admin: Orders · US-704
- Filters by date and status; a list of orders → order detail with a status dropdown
- Cancel asks for confirmation and explains that stock will be returned

### S15 Admin: Staff, settings, dashboard (owner only) · US-705, US-706, US-707
- Staff: find a user by email and change their role; the owner's own row is locked
- Settings: max flavors, low-stock threshold, "from" email address, featured chips
- Dashboard: 3 stat tiles and a "top flavors" bar chart

### S16 System states · all stories
- Loading: a spinner or skeleton, with a short friendly message
- Empty: an illustration, a message and a next-step button
- Error: what happened in plain words, and a "Try again" button
- 404 / Not found: friendly wording and a link home
- Not authorized: "This page is for store staff", with a sign-in link
- Offline / database unreachable: "The store is taking a snack break. Please try again in a minute."
- A "Demo store, no payment needed" footer on every screen

## 8. Accessibility and mobile

- Target **WCAG 2.1 AA** (see NFR-UX-01 in doc 03).
- Text contrast is at least 4.5:1; large text and interface parts at least 3:1.
- Color is never the only signal: selected, sold out, low stock and errors also use an icon or text.
- Every form field has a visible label; errors are shown next to the field.
- Every product image has alt text, which staff enter in the admin pages.
- Buttons and touch targets are at least 44 × 44 px.
- Everything works with a keyboard, in the same order as it appears on screen.
- Mobile first: works at 360 px width; columns stack on small screens; the main button is always easy to reach.

## 9. Content and tone

Friendly expert: short, warm, plain sentences. Light humor is fine, but never in errors about orders or security. All text must be age-appropriate.

| Situation | Example |
|-----------|---------|
| Main buttons | "Build your bag", "Add to cart", "Place order" |
| Success | "Bag added! Good choice." |
| Empty cart | "Your cart is snack-free. Let's fix that." |
| Max flavors reached | "3 flavors max. Your bag can only hold so much awesome." |
| Sold out | "Sold out. Back soon!" |
| Error | "We couldn't place your order. Nothing was charged. Please try again." |
| Not authorized | "This page is for store staff." |

## 10. What is and isn't possible in Streamlit

| Easy in Streamlit | Hard (needs custom CSS or components) |
|-------------------|---------------------------------------|
| Columns, containers, tabs, expanders, sidebar, popovers, dialogs | Pixel-perfect custom layouts |
| Theme colors and one font family (in `config.toml`) | A different font for each element, complex hover effects |
| Buttons, toggles, selects, sliders, number inputs, forms | Fully custom tiles with rich hover states |
| Tables and editable tables (good for admin) | Drag and drop |
| Toasts, balloons, spinners, progress bars | Custom animations (possible with small CSS; keep simple) |
| Multipage navigation with `st.navigation` | A fully custom top navigation bar |
| Built-in charts | Complex interactive charts (use Altair or Plotly) |

**Guidance:** design flavor tiles and product cards as cards inside a column grid, with one button or checkbox each. This maps well to Streamlit. Mark anything that needs custom CSS in the wireframe notes.

## 11. Deliverables the designer hands over

1. Mood board and final color and type palette (then `.streamlit/config.toml` is updated to match)
2. Low-fidelity wireframes for S1–S16, desktop and mobile, saved in `docs/design/wireframes/`
3. High-fidelity mockups for S1, S3, S4, S5 and S6
4. A component sheet with all states: product card, flavor tile, profile bars, badges, quantity stepper, price summary, toast, empty state, admin table, form fields
5. Clickable prototype of Flow A (optional)
6. Microcopy list (section 9, extended)
7. Notes on anything that needs custom CSS beyond Streamlit's defaults
