# 01: Product Features and User Stories

- **Status:** Draft v0.2
- **Product:** An online store that sells bags of potato chips. A shopper picks a **base chip** and adds **flavor add-ons** to build their own bag.
- **Demo only:** No real payments, no real emails, no real customer data. Order confirmation emails are saved as files in an outbox folder, never sent.

---

## 1. Roles

| Role | Who | Can do |
|------|-----|--------|
| **Guest** | Not signed in | Browse, search, view products, build bags, use the cart |
| **Customer** | Registered shopper | Everything a guest can do, plus check out and see their own orders |
| **Staff** | Store employee | Manage chips, flavors, stock and orders |
| **Owner** | Store owner | Everything staff can do, plus manage staff roles and store settings |

## 2. How to read the stories

- **Format:** As a **[role]**, I want **[action]** so that **[benefit]**.
- **ID:** `US-<epic><number>`. For example, `US-301` is the first story in epic E3.
- **Priority:** **Must** = needed for Release 1 · **Should** = Release 1 if time allows · **Could** = later.
- **Acceptance criteria:** numbered `AC1`, `AC2`, and so on. Each one can be tested with a clear yes or no.

## 3. Epics

| Epic | Name | Stories | Screens (doc 02) |
|------|------|---------|------------------|
| E1 | Product search and catalog | US-101 to US-105 | S1, S2 |
| E2 | Product detail | US-201 to US-203 | S3 |
| E3 | Add to cart (Build Your Bag) | US-301 to US-305 | S3, S4 |
| E4 | Checkout and order confirmation | US-401 to US-404 | S5, S6 |
| E5 | Customer register / sign in | US-501 to US-505 | S7, S8, S9, S10 |
| E6 | Flavor discovery (playful extras) | US-601 to US-603 | S1, S3, S10 |
| E7 | Owner and staff product management | US-701 to US-707 | S11 to S15 |

---

## E1 Product search and catalog

### US-101 Home page invites discovery · Must
As a **shopper**, I want an inviting home page so that I'm curious to build a bag.
- AC1: The home page shows a headline, a "Build your bag" button and a "Browse flavors" button.
- AC2: A "How it works" section explains the 3 steps: pick your chip → add up to 3 flavors → crunch.
- AC3: 3 to 4 featured base chips are shown. Staff choose which ones in store settings.
- AC4: A row of flavor tiles links to the flavor library.

### US-102 Browse the shop · Must
As a **shopper**, I want a shop page that lists everything so that I can browse.
- AC1: All active base chips are shown in a grid with image, name, "from $X.XX" and stock status.
- AC2: All active flavors are shown in a separate "Flavor library" section.
- AC3: Inactive (hidden) items never appear.
- AC4: Each chip card has a "Build this bag" button that opens its product page.

### US-103 Search by keyword · Must
As a **shopper**, I want to type a word and find matching chips so that I can find what I want fast.
- AC1: Search looks at chip names, chip descriptions and flavor names.
- AC2: Upper and lower case don't matter, and partial words match ("bbq" finds "Smoky BBQ").
- AC3: The page shows how many results were found for the search word.
- AC4: When there are no results, a friendly message and some suggested items are shown.

### US-104 Filter results · Should
As a **shopper**, I want to filter results so that I can narrow down my choices.
- AC1: I can filter by chip style, flavor family, heat level (0–3), in stock only, and price range.
- AC2: Filters work together with the search word.
- AC3: A "Clear filters" link resets all filters.

### US-105 Sort results · Should
As a **shopper**, I want to sort results so that I see the most useful items first.
- AC1: Sort options are Featured (default), Price low → high, Price high → low, Name A → Z and Newest.
- AC2: The chosen sort stays the same when I change filters.

---

## E2 Product detail

### US-201 View chip details · Must
As a **shopper**, I want a detail page for each chip so that I can decide what to buy.
- AC1: The page shows a large image, name, description, base price and stock status.
- AC2: It shows chip facts: style, thickness and crunch level.
- AC3: It contains the Build Your Bag panel (US-301), so I can buy without leaving the page.
- AC4: A wrong or hidden product ID shows a friendly "not found" message.

### US-202 View flavor details · Must
As a **shopper**, I want to learn about each flavor so that I pick ones I'll enjoy.
- AC1: Each flavor shows its name, description, add-on price and allergens.
- AC2: Each flavor shows a profile: salty, tangy, sweet and heat, each from 0 to 3, as bars **and** numbers.
- AC3: I can open the flavor details from the builder without losing my choices.

### US-203 See allergens before buying · Must
As a **shopper with allergies**, I want to see all allergens in my bag so that I can buy safely.
- AC1: The allergens of the base chip and every chosen flavor are combined, with no duplicates.
- AC2: The list is shown above the "Add to cart" button and updates when my choices change.

---

## E3 Add to cart (Build Your Bag)

### US-301 Build a bag · Must
As a **shopper**, I want to pick a base chip and choose flavors so that I get the combination I want.
- AC1: I choose exactly one base chip.
- AC2: I choose 1 to 3 flavors. The maximum comes from store settings.
- AC3: When I reach the maximum, the other flavors are disabled and a short message says why.
- AC4: Sold-out chips and flavors are shown but can't be selected, and are labeled "Sold out".
- AC5: The bag price (base + each flavor) updates right away.
- AC6: A pre-filled combination in the link (for example from a staff pick) is selected when the page opens.

### US-302 Add the bag to the cart · Must
As a **shopper**, I want to add my bag with a quantity so that I can buy more than one.
- AC1: The quantity starts at 1. The most I can choose is the lowest stock among the base chip and the chosen flavors.
- AC2: "Add to cart" stays disabled until my choices are valid.
- AC3: After adding, I see "Bag added!" and the cart count in the header goes up.
- AC4: Adding the same base and flavors again raises that line's quantity instead of adding a new line.

### US-303 View the cart · Must
As a **shopper**, I want to see everything in my cart so that I know what I'm buying.
- AC1: Each line shows the base chip, flavors, unit price, quantity and line total.
- AC2: The cart shows the number of bags and the subtotal.
- AC3: An empty cart shows a friendly message and a link to the shop.

### US-304 Change or remove cart items · Must
As a **shopper**, I want to change quantities or remove a bag so that my cart is right.
- AC1: I can raise or lower the quantity, but never above the available stock.
- AC2: Setting the quantity to 0, or pressing "Remove", takes the line out.
- AC3: Totals update right away.
- AC4: If stock dropped below a line's quantity, that line shows a warning.

### US-305 Keep my cart when I sign in · Must
As a **guest**, I want my cart kept when I sign in so that I don't rebuild my bags.
- AC1: A guest cart is kept for the browser session.
- AC2: When I sign in, guest lines are merged into my saved cart. The same bag adds up the quantities, never above stock.
- AC3: A signed-in customer's cart is saved in the database and is still there next visit.

---

## E4 Checkout and order confirmation

### US-401 Review the order · Must
As a **customer**, I want to review my order before placing it so that I know it's right.
- AC1: I must be signed in. A guest is sent to sign in and then returned to checkout.
- AC2: The page shows all cart lines, the total, and my name and email.
- AC3: I enter a delivery name and address. Both are required.
- AC4: A clear banner says "Demo store: no payment needed".

### US-402 Place the order · Must
As a **customer**, I want to place my order with one button so that checkout is quick.
- AC1: Stock is checked again when I press "Place order".
- AC2: If anything ran out, no order is created. I see what changed, and my cart is updated.
- AC3: If everything is in stock, the order is saved, stock is deducted for every item in one step, and my cart is emptied.
- AC4: Pressing the button twice creates only one order.
- AC5: The order keeps the names and prices from the time of purchase.
- AC6: Each order gets a number like `CHIP-20261109-0001`.

### US-403 See the order confirmation · Must
As a **customer**, I want a confirmation page so that I know my order went through.
- AC1: It shows the order number, items, total, and date and time.
- AC2: It says the confirmation email was sent to my email address. (It was saved to the outbox.)
- AC3: It has "View my orders" and "Keep shopping" buttons.
- AC4: I can only see my own orders, even if I change the order number in the link.

### US-404 Save the confirmation email to the outbox · Must
As the **store owner**, I want each confirmation saved as an email file so that the demo shows a real-looking email without sending anything.
- AC1: One file is created for each order: `outbox/order-<order-number>.eml`.
- AC2: The file includes To, From, Subject (`Your order <number> is confirmed!`), date, greeting, items, total, and a "no payment was taken (demo)" note.
- AC3: The file opens in a normal email program.
- AC4: If the file can't be written, the order still succeeds and the error is logged.

---

## E5 Customer register / sign in

### US-501 Register · Must
As a **guest**, I want to create an account so that I can check out and see my orders.
- AC1: The form asks for display name, email, password and password confirmation.
- AC2: The password rules are shown and ticked off as I type.
- AC3: An email address that's already registered shows a clear message.
- AC4: New accounts always get the **customer** role.

### US-502 Sign in and sign out · Must
As a **customer**, I want to sign in and out so that my account stays private.
- AC1: I sign in with email and password.
- AC2: A wrong email or password shows one general message that doesn't say which one was wrong.
- AC3: After signing in I go back to the page I came from.
- AC4: The header shows my name and a "Sign out" button. Signing out clears my session and goes to Home.

### US-503 Reset password · Should
As a **customer**, I want to reset a forgotten password so that I can get back in.
- AC1: A "Forgot password?" link asks for my email and starts the Supabase reset.
- AC2: The same message is shown whether or not the email exists.

### US-504 My orders · Must
As a **customer**, I want to see my past orders so that I can check what I bought.
- AC1: I see only my orders, newest first, with number, date, total and status.
- AC2: Opening an order shows its lines.
- AC3: With no orders yet, a friendly message and a link to the shop are shown.

### US-505 My profile · Could
As a **customer**, I want to update my display name and saved address so that checkout is faster.
- AC1: I can change my display name and default address.
- AC2: Checkout fills in the saved address automatically.

---

## E6 Flavor discovery (playful extras)

These features make the store feel fun and spark curiosity. They follow the ethics rule in doc 02, section 4: no fake timers, no fake scarcity, no pressure.

### US-601 Staff picks combos · Should
As a **curious shopper**, I want suggested flavor combinations so that I get ideas.
- AC1: A product page shows up to 3 "Staff pick" combinations for that chip.
- AC2: Choosing a combo fills in the builder with those flavors.
- AC3: Staff picks also appear on the home page.

### US-602 Surprise me · Could
As a **curious shopper**, I want a "Surprise me" button so that I can discover a random combination.
- AC1: The button picks a random in-stock base chip and 1 to 3 in-stock flavors.
- AC2: It opens the product page with that combination filled in. I can still change it.

### US-603 Flavor passport · Could
As a **customer**, I want to collect a stamp for each flavor I've tried so that exploring new flavors feels fun.
- AC1: My account shows every flavor as a stamp: filled in if I've ordered it, empty if not.
- AC2: It shows how many I've collected, for example "7 of 10 flavors tried".
- AC3: Badges are given at 3, 6 and all flavors ("Taster", "Explorer", "Flavor Master").
- AC4: There are no timers, no streaks, and no messages pushing me to buy.

---

## E7 Owner and staff product management

These pages are only for staff and owner. Anyone else sees "Not authorized".

### US-701 Manage base chips · Must
As **staff**, I want to add and edit base chips so that the catalog stays up to date.
- AC1: Fields are name, description, style, thickness, crunch level, price, stock, image, image alt text, featured, and active.
- AC2: Price must be above 0. Stock must be a whole number of 0 or more.
- AC3: Images must be JPG, PNG or WebP, 2 MB or smaller.
- AC4: Items are hidden (made inactive) instead of deleted, after a confirmation step.

### US-702 Manage flavors · Must
As **staff**, I want to add and edit flavors so that shoppers have exciting choices.
- AC1: Fields are name, description, family, profile values (salty, tangy, sweet, heat: 0–3), allergens, add-on price, stock, icon or image, and active.
- AC2: The same checks apply as in US-701.
- AC3: Staff can set up to 3 staff picks for each base chip.

### US-703 Manage stock · Must
As **staff**, I want a stock overview so that I know what to restock.
- AC1: One table lists all chips and flavors with their current stock.
- AC2: Items at or below the low-stock threshold are highlighted with an icon.
- AC3: I can change stock in the table. Each change needs a reason.
- AC4: Every stock change is recorded with who made it, when, the amount and the reason.

### US-704 Manage orders · Must
As **staff**, I want to see and update all orders so that I can fulfill them.
- AC1: Orders can be filtered by date and status.
- AC2: An order shows the customer's name, email, address and order lines.
- AC3: I can change the status: Placed → Packed → Shipped.
- AC4: Cancelling asks for confirmation and puts the stock back.

### US-705 Manage staff · Must
As the **owner**, I want to give or remove the staff role so that I control who manages the store.
- AC1: I can find a user by email and set their role to customer or staff.
- AC2: Staff can't change roles. The database blocks it, not only the screen.
- AC3: I can't remove my own owner role.

### US-706 Store settings · Should
As the **owner**, I want to change store settings without code so that I can adjust the store.
- AC1: Settings are: maximum flavors per bag (1–5), low-stock threshold, "from" email address, and featured chips.
- AC2: Changes take effect right away.

### US-707 Owner dashboard · Could
As the **owner**, I want a simple dashboard so that I can see how the store is doing.
- AC1: It shows orders today, bags sold this week and the number of low-stock items.
- AC2: It shows a chart of the top 5 flavors.

---

## 4. Key domain terms

| Term | Meaning |
|------|---------|
| Base chip | The chip itself: cut, thickness and style. Example: Kettle Cooked. |
| Flavor (add-on) | A seasoning added to a bag. Example: Smoky BBQ. Each has its own price and stock. |
| Bag | One base chip plus 1–3 flavors, with a quantity. This is what goes in the cart. |
| Flavor family | A group of similar flavors: Salty, Tangy, Spicy, Sweet, Herby. |
| Flavor profile | Four 0–3 scores: salty, tangy, sweet, heat. |
| Staff pick | A suggested combination of flavors for one base chip, chosen by staff. |
| Stock | How many units are left. One bag uses 1 unit of the base chip and 1 unit of each chosen flavor. |
| Order number | A readable ID, for example `CHIP-20261109-0001`. |
| Outbox | The folder where confirmation emails are saved as `.eml` files. Nothing is sent. |
| Flavor passport | The set of flavors a customer has tried, shown as stamps (US-603). |

## 5. Seed data for demos

The seed script loads this data so the store looks full from the first run. All of it is fictional and age-appropriate.

**Base chips (4)**

| Name | Style | Price | Stock |
|------|-------|-------|-------|
| Classic Thin | Classic | $2.50 | 100 |
| Kettle Cooked | Kettle | $3.00 | 80 |
| Wavy Ridge | Wavy | $2.75 | 60 |
| Sweet Potato | Sweet potato | $3.25 | 3 (to test "Few left") |

**Flavors (10)**

| Name | Family | Price | Stock |
|------|--------|-------|-------|
| Sea Salt | Salty | $0.25 | 200 |
| Salt & Vinegar | Tangy | $0.50 | 150 |
| Sour Cream & Onion | Herby | $0.50 | 150 |
| Smoky BBQ | Spicy | $0.50 | 120 |
| Cheddar Blast | Salty | $0.60 | 100 |
| Zesty Lime | Tangy | $0.40 | 90 |
| Chili Kick | Spicy | $0.60 | 70 |
| Honey Mustard | Sweet | $0.60 | 50 |
| Cinnamon Sugar | Sweet | $0.50 | 40 |
| Truffle Herb | Herby | $0.90 | 0 (to test "Sold out") |

**Other seed data**
- Staff picks: Kettle Cooked + Salt & Vinegar + Sea Salt; Wavy Ridge + Smoky BBQ + Cheddar Blast; Sweet Potato + Cinnamon Sugar.
- Accounts: `owner@demo.test`, `staff@demo.test`, `customer@demo.test`. Passwords are given in the README for local use only.
- The demo customer has **2 bags in their cart** and **2 past orders**, so the cart, checkout and order pages can be tested right away.
- Settings: maximum 3 flavors per bag, low-stock threshold 10.

## 6. Out of scope

- Real payments, taxes, shipping costs and discount codes
- Sending real emails
- Product reviews and ratings
- Several bag sizes
- Social sign-in (Google, etc.) and multi-factor sign-in
- A mobile app
- Leaderboards, streaks or any game feature that pushes people to buy

## 7. Story map (Release 1)

| Discover (E1) | Product (E2) | Build & Cart (E3) | Checkout (E4) | Account (E5) | Fun (E6) | Manage (E7) |
|---------------|--------------|-------------------|---------------|--------------|----------|-------------|
| US-101 | US-201 | US-301 | US-401 | US-501 | US-601 | US-701 |
| US-102 | US-202 | US-302 | US-402 | US-502 | | US-702 |
| US-103 | US-203 | US-303 | US-403 | US-504 | | US-703 |
| | | US-304 | US-404 | | | US-704 |
| | | US-305 | | | | US-705 |

**Should / Could:** US-104, US-105, US-503, US-505, US-602, US-603, US-706, US-707.
