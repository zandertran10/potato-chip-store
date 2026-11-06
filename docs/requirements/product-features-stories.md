# Product Features and User Stories

Story format: **As a** [role], **I want** [action] **so that** [benefit].
Priority: **Must** = needed for Release 1, **Should** = Release 1 if time allows, **Could** = later.

Business rules (BR-xx) are defined in `requirements.md`, section 5.

---

## F-01 Add to Cart

The shopper builds a bag (base chip + flavors + quantity) and adds it to the cart.

### US-01.1 Build a bag (Must)
As a **shopper**, I want to pick a base chip and choose flavor add-ons so that I get the chip combination I want.

Acceptance criteria:
- [ ] I can choose exactly one base chip.
- [ ] I can choose 1 to 3 flavors (BR-01). Once I reach the maximum, the remaining flavors are disabled and a short message explains why.
- [ ] Out-of-stock bases and flavors are shown but can't be selected, and are labeled "Sold out" (BR-04).
- [ ] The bag price updates right away as I change my choices (BR-02).
- [ ] A summary shows my base, my flavors, and the total price before I add the bag.

### US-01.2 Add bag to cart (Must)
As a **shopper**, I want to add my bag to the cart with a quantity so that I can buy more than one.

Acceptance criteria:
- [ ] The quantity starts at 1. The most I can choose is whatever current stock allows (the lowest stock among the base and its flavors).
- [ ] After I add the bag, I see a confirmation (for example "Bag added!") and the cart count in the header goes up.
- [ ] If I add the same base + flavors again, the quantity of that cart line goes up instead of a new line being added.
- [ ] The "Add to cart" button is disabled until my choices are valid.

### US-01.3 View cart (Must)
As a **shopper**, I want to see everything in my cart so that I know what I'm buying.

Acceptance criteria:
- [ ] Each line shows: base chip, flavors, unit price, quantity, and line total.
- [ ] The cart shows a subtotal and the number of bags.
- [ ] An empty cart shows a friendly message and a link to the shop.

### US-01.4 Change or remove cart items (Must)
As a **shopper**, I want to change quantities or remove a bag so that my cart is right before I check out.

Acceptance criteria:
- [ ] I can raise or lower the quantity, never above available stock.
- [ ] Setting the quantity to 0, or pressing "Remove", takes the line out.
- [ ] Totals update right away.

### US-01.5 Keep my cart when I sign in (Must)
As a **guest**, I want my cart to stay when I sign in or register so that I don't have to rebuild my bags.

Acceptance criteria:
- [ ] A guest cart is kept for the browser session.
- [ ] When I sign in, guest cart lines are merged into my saved cart.
- [ ] A signed-in customer's cart is saved in the database, so it is still there next visit.

### US-01.6 Surprise me (Could)
As a **curious shopper**, I want a "Surprise me" button that picks a random in-stock combination so that I can discover new flavors.

---

## F-02 Checkout and Order Confirmation

No credit card. Placing an order deducts stock and saves a confirmation email file.

### US-02.1 Review order before placing it (Must)
As a **customer**, I want to review my order so that I can confirm it's right.

Acceptance criteria:
- [ ] I must be signed in. Guests are sent to sign in, then returned to checkout.
- [ ] The page shows all cart lines, the total, and my name and email.
- [ ] I enter a delivery name and address (stored for display only; nothing is shipped).
- [ ] A clear note says "Demo store: no payment needed."

### US-02.2 Place order (Must)
As a **customer**, I want to place my order with one button so that checkout is quick.

Acceptance criteria:
- [ ] Stock is checked again when I press "Place order" (BR-05).
- [ ] If something ran out, the order is not placed. I see which items changed, and my cart is updated.
- [ ] If everything is in stock, the order is saved, stock is deducted in one step (BR-06), and my cart is emptied.
- [ ] Pressing the button twice does not create two orders.
- [ ] Prices are saved on the order, so later price changes don't alter it.

### US-02.3 Order confirmation page (Must)
As a **customer**, I want a confirmation page so that I know my order went through.

Acceptance criteria:
- [ ] It shows the order number (BR-08), the items, the total, and the date and time.
- [ ] It says a confirmation email has been "sent" (saved to the outbox).
- [ ] It links to "View my orders" and "Keep shopping".

### US-02.4 Confirmation email saved to a folder (Must)
As the **store owner**, I want each order confirmation written as an email file so that the demo shows a real-looking email without sending anything.

Acceptance criteria:
- [ ] One file per order: `outbox/order-<order-number>.eml` (BR-09).
- [ ] It contains: To (customer email), From (store address), Subject ("Your order <number> is confirmed!"), date, greeting, item list, total, and a "no payment was taken (demo)" note.
- [ ] The file opens in a normal email program (standard `.eml` format).
- [ ] If writing the file fails, the order still goes through and the error is logged.
- [ ] The `outbox/` folder is gitignored.

---

## F-03 Product Search

### US-03.1 Search by keyword (Must)
As a **shopper**, I want to type a word and find matching chips so that I can find what I want fast.

Acceptance criteria:
- [ ] Search looks at base chip names, descriptions, and flavor names.
- [ ] Matching ignores upper and lower case and finds partial words ("bbq" finds "Smoky BBQ").
- [ ] Results show image, name, starting price, and stock status.
- [ ] No results shows a friendly message and suggested popular items.

### US-03.2 Filter results (Should)
As a **shopper**, I want to filter results so that I can narrow down my choices.

Filters:
- [ ] Chip style (Classic, Kettle, Wavy, …)
- [ ] Flavor family (Salty, Tangy, Spicy, Sweet, Herby)
- [ ] Heat level (0–3)
- [ ] In stock only
- [ ] Price range

### US-03.3 Sort results (Should)
As a **shopper**, I want to sort results so that I see the most useful items first.

- [ ] Sort options: Featured (default), Price low → high, Price high → low, Name A → Z, Newest.

### US-03.4 Browse without searching (Must)
As a **shopper**, I want a Shop page that lists all products so that I can browse.

- [ ] It shows all active base chips in a grid, and all active flavors in a separate "Flavor library" section.
- [ ] Inactive (hidden) items never appear.

---

## F-04 Product Detail

### US-04.1 View base chip details (Must)
As a **shopper**, I want a detail page for each chip so that I can decide what to buy.

Acceptance criteria:
- [ ] It shows a large image, name, description, base price, and stock status.
- [ ] It shows chip facts: style, thickness, crunch level.
- [ ] It includes the Build Your Bag panel (US-01.1) so I can customize and add to the cart without leaving the page.

### US-04.2 View flavor details (Must)
As a **shopper**, I want to learn about each flavor so that I can pick ones I'll enjoy.

Acceptance criteria:
- [ ] Each flavor shows its name, a short description, price, a flavor profile (salty / tangy / sweet / heat, 0–3 each), and its allergens.
- [ ] Flavor info can be opened from the builder without losing my choices.

### US-04.3 Suggested combos (Should)
As a **shopper**, I want to see suggested flavor combinations so that I get ideas.

- [ ] Staff can mark up to 3 "Staff picks" combos for each base chip.
- [ ] Pressing a combo fills in the builder with those choices.

### US-04.4 Allergen and ingredient info (Must)
As a **shopper with allergies**, I want to see ingredients and allergens so that I can buy safely.

- [ ] The allergens of the base and of every chosen flavor are combined and shown before "Add to cart".

---

## F-05 Customer Register and Sign In

### US-05.1 Register (Must)
As a **guest**, I want to create an account so that I can check out and see my orders.

Acceptance criteria:
- [ ] Fields: display name, email, password, confirm password.
- [ ] Password rules are shown on the form (see NFR-AUTH-02).
- [ ] An email that is already registered shows a clear message.
- [ ] New accounts always get the **customer** role.
- [ ] After registering, I'm signed in (or asked to confirm my email, depending on Q3).

### US-05.2 Sign in and sign out (Must)
As a **customer**, I want to sign in and out so that my account stays private.

Acceptance criteria:
- [ ] I sign in with email and password.
- [ ] A wrong email or password shows one general message (it doesn't say which was wrong).
- [ ] The header shows my name and a "Sign out" button.
- [ ] Signing out clears my session and returns me to Home.

### US-05.3 Reset password (Should)
As a **customer**, I want to reset a forgotten password so that I can get back into my account.

- [ ] Uses Supabase Auth password reset. For the demo, the reset link may come from the local Supabase email inbox (Inbucket) or the Supabase dashboard.

### US-05.4 My orders (Must)
As a **customer**, I want to see my past orders so that I can check what I bought.

- [ ] It lists my orders only (newest first) with number, date, total, and status.
- [ ] Opening an order shows its lines.

### US-05.5 My profile (Could)
As a **customer**, I want to update my display name and saved address so that checkout is faster.

---

## F-06 Owner and Staff Management Pages

These pages are only visible to staff and owner. Customers and guests who try to open them see "Not authorized".

### US-06.1 Manage base chips (Must)
As **staff**, I want to add and edit base chips so that the catalog stays up to date.

Acceptance criteria:
- [ ] Fields: name, description, style, price, stock, image, featured (yes/no), active (yes/no).
- [ ] I can upload a product image (stored in Supabase Storage; JPG/PNG/WebP, 2 MB max).
- [ ] Price must be above 0. Stock must be a whole number of 0 or more.
- [ ] I can hide an item (set it inactive) instead of deleting it (BR-10).

### US-06.2 Manage flavors (Must)
As **staff**, I want to add and edit flavors so that shoppers have exciting choices.

- [ ] Fields: name, description, family, flavor profile values, allergens, add-on price, stock, image or icon, active.
- [ ] Same checks as US-06.1.

### US-06.3 Restock and view stock (Must)
As **staff**, I want a stock overview so that I know what to restock.

- [ ] A table lists all bases and flavors with current stock.
- [ ] Items at or below a low-stock threshold (default 10) are highlighted.
- [ ] I can change stock directly from the table.
- [ ] Each stock change records who made it and when (stock history).

### US-06.4 View orders (Must)
As **staff**, I want to see all orders so that I can fulfill them.

- [ ] A list of orders with filters by date and status.
- [ ] Opening an order shows the customer name, email, address, and lines.
- [ ] I can change the order status: Placed → Packed → Shipped, or Cancelled.
- [ ] Cancelling an order puts its stock back.

### US-06.5 Manage staff (Must, owner only)
As the **owner**, I want to give or remove the staff role so that I control who manages the store.

- [ ] The owner can search users by email and set their role to customer or staff.
- [ ] Staff cannot change roles.
- [ ] The owner cannot remove their own owner role.

### US-06.6 Store settings (Should, owner only)
As the **owner**, I want to change store settings so that I can adjust the store without code.

- [ ] Settings: maximum flavors per bag, low-stock threshold, store email "from" address, featured items on Home.

### US-06.7 Dashboard (Could)
As the **owner**, I want a simple dashboard (orders today, top flavors, low stock) so that I can see how the store is doing.

---

## Story map (Release 1)

| Discover | Browse | View Product | Build and Add to Cart | Checkout | Account / Orders | Manage Store |
|----------|--------|--------------|-----------------------|----------|------------------|--------------|
| US-03.1 | US-03.4 | US-04.1 | US-01.1 | US-02.1 | US-05.1 | US-06.1 |
| US-03.2 | US-03.3 | US-04.2 | US-01.2 | US-02.2 | US-05.2 | US-06.2 |
| | | US-04.4 | US-01.3 | US-02.3 | US-05.4 | US-06.3 |
| | | US-04.3 | US-01.4 | US-02.4 | US-05.3 | US-06.4 |
| | | | US-01.5 | | | US-06.5 |

Later: US-01.6, US-05.5, US-06.6, US-06.7.
