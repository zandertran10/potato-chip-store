# UI/UX Requirements

**Audience:** The designer creating wireframes and mockups. Developers use it to build the screens.

---

## 1. Analysis of the vision

> "Professional yet lighthearted. It should create curiosity to buy from the website. The UI design should facilitate."

| Vision phrase | What it means for design | What to avoid |
|---------------|--------------------------|---------------|
| **Professional** | Clean grid, plenty of space, one clear main action per screen, consistent components, sharp product photos, prices and stock always easy to see | Clutter, cramped layouts, inconsistent buttons, low-quality images |
| **Lighthearted** | Warm colors, rounded shapes, playful wording, small moments of delight (a "crunch" animation when a bag is added, friendly empty states) | Childish or cartoon-heavy styling, jokes that hide important information, too much animation |
| **Creates curiosity** | Make the flavor combination the star: show flavors as exciting choices, show flavor profiles, "Staff picks", "Surprise me", new-flavor badges, a hint of "only a few left" | Fake urgency (made-up countdowns), hiding prices, dark patterns |
| **UI should facilitate buying** | Short path from landing to checkout, the builder available on the product page, live price, visible cart count, stock and allergen info before adding | Extra steps, surprise errors at checkout, forcing sign-in before browsing |

**Design principle summary:** *Clear first, fun second. Every playful touch should also help the shopper decide or act.*

---

## 2. Brand direction

The store name is still open (see `requirements.md`, Q1). Use a placeholder wordmark.

### 2.1 Personality
Friendly expert. Like a snack-maker who is proud of their recipes and happy to share them.

### 2.2 Tone of voice (UX-BR-01)
| Situation | Example |
|-----------|---------|
| Main button | "Add to cart", "Place order" (plain and clear) |
| Success | "Bag added! Good choice." |
| Empty cart | "Your cart is snack-free. Let's fix that." |
| Max flavors reached | "3 flavors max. Your bag can only hold so much awesome." |
| Sold out | "Sold out. Back soon!" |
| Error | Plain words first, then a light touch: "Something went wrong saving your order. Please try again." |

Rules: short sentences, no slang that may age badly, never joke in error messages about money or security, and keep all content age-appropriate.

### 2.3 Colors (UX-BR-02)
These match `.streamlit/config.toml`. The designer may refine them, and the config file must then be updated.

| Token | Hex | Use |
|-------|-----|-----|
| Primary (Golden Chip) | `#E0A526` | Main buttons, highlights, active states |
| Background (Cream) | `#FFFDF7` | Page background |
| Surface (Butter) | `#FFF3D6` | Cards, sidebar, panels |
| Text (Toasted Brown) | `#3B2A1A` | Body text and headings |
| Suggested accent: Paprika | `#D9480F` | Heat levels, "New" badges (use sparingly) |
| Suggested accent: Herb Green | `#2F9E44` | In stock, success |
| Suggested: Error Red | `#C92A2A` | Errors and sold out |

Text must meet a 4.5:1 contrast ratio against its background. **Do not use primary gold for text on cream** (contrast is too low). Use it for fills, with brown text on top.

### 2.4 Type (UX-BR-03)
- Headings: a rounded, friendly sans serif (suggestions: Nunito, Poppins, Fredoka for the logo only)
- Body: a clean sans serif (Streamlit's default sans or Inter)
- At least 16 px for body text

### 2.5 Imagery and icons (UX-BR-04)
- Product photos: bright, close-up chip textures on a plain warm background, all with the same lighting and angle.
- Flavors: each flavor gets a simple icon or ingredient photo (lime, chili, onion, …) and a color tag for its family.
- Icons: one icon set with rounded line style.
- Illustrations for empty states and the 404 page: a simple chip mascot is allowed but optional.

---

## 3. Information architecture

```
Header: Logo | Search | Shop | (Account / Sign in) | Cart (count)
│
├── Home
├── Shop (browse + search results)
│     └── Product Detail (with Build Your Bag)
├── Cart
├── Checkout ──► Order Confirmation
├── Sign in / Register / Reset password
├── My Account
│     └── My Orders ──► Order Detail
└── Store Admin (staff/owner only)
      ├── Products (base chips)
      ├── Flavors
      ├── Stock
      ├── Orders
      ├── Staff (owner only)
      └── Settings (owner only)
```

Navigation rules:
- UX-NAV-01: The cart count and search are visible on every customer page.
- UX-NAV-02: Admin pages are not shown in navigation for customers and guests.
- UX-NAV-03: Admin pages use the same brand but a calmer, denser layout (tables and forms), with a visible "Store Admin" label so staff always know where they are.

---

## 4. Page requirements

For each page, the designer should produce wireframes for: **default**, **loading**, **empty**, and **error** states, at **desktop (1280 px)** and **mobile (390 px)** widths.

### UX-PG-01 Home
Goal: spark curiosity and get the shopper into the builder fast.
- Hero: a short headline about building your own bag, a main button "Build your bag", and a second button "Browse flavors".
- "How it works" in 3 steps: Pick your chip → Add up to 3 flavors → Crunch.
- Featured base chips (3–4 cards).
- "Staff picks" combos (cards that open the product page with the builder pre-filled).
- Flavor library teaser: a row of flavor icons. Selecting one shows its profile.
- Optional "Surprise me" button.

### UX-PG-02 Shop / Search results
- Search box at the top, with the current search shown ("12 results for 'bbq'").
- Filters (chip style, flavor family, heat, in stock, price) in the sidebar on desktop and in an expandable section on mobile.
- Sort dropdown.
- Product card: image, name, "from $X.XX", stock badge, "New" or "Few left" badge when relevant, and a "Build this bag" button.
- Empty results: a friendly message, a "clear filters" link, and suggested items.

### UX-PG-03 Product Detail + Build Your Bag (key screen)
This is the most important screen. Spend the most design time here.
- Left (desktop) / top (mobile): large image, name, description, chip facts (style, thickness, crunch meter).
- Right / below: **Build Your Bag** panel:
  1. Base chip (already selected; can switch).
  2. Flavor picker: flavor "tiles" grouped by family, each with an icon, name, add-on price, and mini profile bars (salty / tangy / sweet / heat). Selected tiles have a clear selected state (not color only: add a check mark). Sold-out tiles are greyed out with a "Sold out" label.
  3. A counter: "2 of 3 flavors chosen".
  4. Combined allergens.
  5. Quantity stepper.
  6. Live summary: base + flavors = **total**.
  7. "Add to cart" main button.
- "Staff picks" combos for this chip.
- After adding: a short confirmation (toast) with a "View cart" link; the cart count animates.

### UX-PG-04 Cart
- Line items: small image, base name, flavor tags, unit price, quantity stepper, line total, remove link.
- Summary card: bag count, subtotal, "Checkout" main button, "Keep shopping" link.
- A warning shown on a line if stock fell below its quantity.
- Empty state with an illustration and a "Build your bag" button.

### UX-PG-05 Checkout
- Steps shown at the top: Cart → Details → Done.
- If not signed in: a sign-in / register prompt, and the shopper returns here afterwards.
- Delivery name and address form.
- Order summary (can't be edited here; there is a link back to the cart).
- A visible banner: "Demo store: no payment needed."
- "Place order" main button with a loading state. It is disabled while the order is being placed.

### UX-PG-06 Order Confirmation
- A celebration moment (a small animation or illustration, kept short).
- Order number shown large, the items, the total, and the date.
- "We've emailed your confirmation to name@example.com" (saved to the outbox).
- Buttons: "View my orders", "Keep shopping".

### UX-PG-07 Sign in / Register / Reset password
- A simple centered card. Tabs or links to switch between sign in and register.
- Password rules shown as a checklist that updates as the shopper types.
- Errors shown next to the field they belong to.
- A short reason to register: "Save your bags and track your orders."

### UX-PG-08 My Account / My Orders
- Profile summary (name, email).
- Orders table/cards: number, date, total, status badge.
- Order detail with line items.

### UX-PG-09 Admin: Products and Flavors
- A searchable table with columns: image, name, price, stock, active, featured, and an edit action.
- "Add new" button. Add/edit form in a side panel or separate page, with image upload and preview.
- Active/inactive toggle. Hiding an item asks for confirmation.

### UX-PG-10 Admin: Stock
- A table of all bases and flavors with stock numbers that can be edited inline.
- Low-stock rows are highlighted (with an icon as well as color).
- A stock history table below or in a tab.

### UX-PG-11 Admin: Orders
- Filters by date and status. A list of orders. Opening one shows its detail with a status dropdown.
- Cancelling asks for confirmation and explains that stock will be returned.

### UX-PG-12 Admin: Staff (owner only) and Settings
- Find a user by email and set their role. The owner's own row is locked.
- Settings form: maximum flavors, low-stock threshold, "from" email, featured items.

### UX-PG-13 System pages
- 404 / "Not authorized" pages with friendly wording and a link home.

---

## 5. Components to design

| ID | Component | Notes |
|----|-----------|-------|
| UX-C-01 | Header / navigation | Logo, search, links, account menu, cart count |
| UX-C-02 | Product card | Used on Home and Shop |
| UX-C-03 | Flavor tile | Selected / not selected / sold out / disabled (max reached) |
| UX-C-04 | Flavor profile bars | Four 0–3 meters; must also show the number (not only the bar) |
| UX-C-05 | Badges | New, Few left, Sold out, Staff pick, order status |
| UX-C-06 | Quantity stepper | − / number / +, with limits |
| UX-C-07 | Price summary | Live bag total |
| UX-C-08 | Toast / alert | Success, warning, error |
| UX-C-09 | Empty state | Illustration + message + button |
| UX-C-10 | Admin data table | Search, sort, inline edit |
| UX-C-11 | Forms | Labels above fields, help text, errors |

---

## 6. Interaction and motion

- UX-INT-01: Every action gives feedback within about 1 second (spinner, toast, or state change).
- UX-INT-02: Animations are short (under 400 ms) and turn off when the user has "reduce motion" switched on.
- UX-INT-03: Delight moments are limited to: adding to cart, the order confirmation, and "Surprise me". Nowhere else.
- UX-INT-04: Messages that block the shopper (pop-ups that must be closed) are only used for destructive admin actions.

## 7. Accessibility (design side)

- Color is never the only signal (selected, sold out, low stock, and errors also use an icon or text).
- Contrast: 4.5:1 for text, 3:1 for large text and interface parts.
- Buttons and touch targets at least 44 × 44 px.
- Every form field has a visible label.
- Every product image needs alt text (staff enter it in admin).
- Reading and keyboard order follows the visual order.

## 8. Streamlit constraints the designer must know

The app is built with Streamlit, so wireframes must fit what it can do without heavy custom code:

| Streamlit can do easily | Harder, or needs custom CSS / components |
|-------------------------|------------------------------------------|
| Columns, containers, tabs, expanders, sidebar | Pixel-perfect custom layouts |
| Built-in theme colors and font family | Different font per element, complex hover effects |
| Buttons, toggles, selects, sliders, number inputs, forms | Fully custom-styled tiles with rich hover states |
| Tables and data editors (good for admin) | Drag-and-drop |
| Toasts, balloons, spinners, progress bars | Custom animations (possible with small CSS, keep simple) |
| Multipage app navigation | Fully custom top navigation bar (sidebar or `st.navigation` is easier) |

**Guidance:** Design flavor tiles and product cards as cards inside a column grid with one button or checkbox each. This maps well to Streamlit. Mark anything that needs custom CSS in the wireframe notes.

## 9. Deliverables expected from the designer

1. A mood board and a confirmed color/type palette (update `.streamlit/config.toml` afterwards).
2. Low-fidelity wireframes for UX-PG-01 to UX-PG-13 (desktop and mobile), saved in `docs/design/wireframes/`.
3. High-fidelity mockups for Home, Product Detail + Build Your Bag, Cart, Checkout, and Confirmation.
4. A component sheet (section 5) with all states.
5. Microcopy list (section 2.2 extended).
6. Notes on anything that needs custom CSS beyond Streamlit's defaults.
