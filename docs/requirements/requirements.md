# Consolidated Requirements: Potato Chip Store

- **Status:** Draft v0.1
- **Purpose:** Learning and demo project. Not a real store. No real payments, no real emails, no real customer data.

## 1. Product summary

An online store that sells bags of potato chips. A shopper picks a **base chip** (for example Classic, Kettle, or Wavy) and then adds one or more **flavor add-ons** (for example Sea Salt and Vinegar, Smoky BBQ, Sour Cream and Onion) to make their own bag. The store owner and staff manage the base chips, the flavors, prices, and stock.

The site should look **professional yet lighthearted**, and make people **curious enough to try a flavor combination**.

## 2. Goals

| # | Goal | How we know it is met |
|---|------|-----------------------|
| G1 | A shopper can build a custom bag and place an order in a few minutes | The full flow (search → detail → build bag → cart → checkout → confirmation) works end to end |
| G2 | Stock stays correct | Placing an order reduces stock; an order can never take stock below zero |
| G3 | Staff can run the catalog without touching code | Owner and staff can add, edit, hide, and restock products and flavors in the app |
| G4 | The project is a clean teaching example | Code follows the rules in `CLAUDE.md`; security basics (sign-in, roles, RLS) are in place |

## 3. Users and roles

| Role | Who | What they can do |
|------|-----|------------------|
| **Guest** | Anyone not signed in | Browse, search, view products, build a bag, use the cart |
| **Customer** | Registered shopper | Everything a guest can do, plus check out and see their own orders |
| **Staff** | Store employee | Manage products, flavors, stock, and view all orders |
| **Owner** | Store owner | Everything staff can do, plus manage staff accounts and roles |

A guest must sign in or register before checkout. Their cart carries over when they sign in.

## 4. Features

| ID | Feature | Summary | Main roles |
|----|---------|---------|------------|
| F-01 | Add to cart | Build a bag (base chip + flavors + quantity) and put it in the cart; view, change, and remove cart items | Guest, Customer |
| F-02 | Checkout and order confirmation | Place the order with **no credit card**. Stock is deducted. A confirmation "email" is **saved as a file in a folder**, not sent | Customer |
| F-03 | Product search | Search by name, flavor, or keyword; filter and sort the results | Guest, Customer |
| F-04 | Product detail | Full page for a base chip with description, flavor options, live price, and stock | Guest, Customer |
| F-05 | Customer register and sign in | Create an account, sign in, sign out, reset password, see order history | Guest, Customer |
| F-06 | Owner and staff management pages | Manage products, flavors, stock, orders, and (owner only) staff accounts | Staff, Owner |

Detailed stories and acceptance criteria are in `product-features-stories.md`.

## 5. Key business rules

| ID | Rule |
|----|------|
| BR-01 | A bag has exactly **one base chip** and **1 to 3 flavor add-ons**. The maximum (3) is a setting that staff can change. |
| BR-02 | Bag price = base chip price + the price of each flavor add-on. |
| BR-03 | Stock is tracked separately for each base chip and each flavor add-on. One bag uses 1 unit of the base and 1 unit of each chosen flavor. |
| BR-04 | An item that is out of stock can be seen but not added to the cart. |
| BR-05 | Stock is checked again at checkout. If anything ran out, the customer is told what changed and the order is not placed. |
| BR-06 | Placing an order deducts all stock in one step. Either every item is deducted or none are (no partial orders). |
| BR-07 | No payment is collected. The order is recorded as "Placed (demo, no payment)". |
| BR-08 | Each order gets a readable number, for example `CHIP-20261102-0001`. |
| BR-09 | The confirmation email is written to the `outbox/` folder as one `.eml` file per order. Nothing is sent. |
| BR-10 | Products and flavors are never deleted once they appear in an order. They are hidden (marked inactive) instead, so old orders still display correctly. |

## 6. Scope

**In scope (Release 1)**
- Features F-01 to F-06
- Seed data: about 4 base chips and 10 flavors with images, so the demo looks full on day one
- One owner account created by the seed script

**Out of scope**
- Real payments, shipping costs, taxes, discount codes
- Sending real emails
- Product reviews and ratings
- Multiple bag sizes
- Mobile app

**Ideas for a later release**
- "Mystery flavor of the week"
- Popular combinations based on real orders
- Order status updates (Placed → Packed → Shipped) shown to customers

## 7. UI/UX summary

Professional yet lighthearted. Warm "golden chip" colors, friendly wording, clear layouts. The **Build Your Bag** experience is the heart of the site and should feel like a small, fun game while staying quick and clear. Full details are in `ui-ux-requirements.md`.

## 8. Non-functional summary

- Sign-in through Supabase Auth (email and password)
- Role-based access (customer / staff / owner) enforced in the database with Row Level Security on every table
- Secrets only in environment variables or `.streamlit/secrets.toml` (gitignored)
- Stock deduction is atomic, so orders can't oversell
- Accessible (WCAG 2.1 AA target), works on phone and desktop
- All content is age-appropriate, because this project may be used in training with minors

Full details are in `non-functional-requirements.md`.

## 9. Assumptions

| # | Assumption |
|---|-----------|
| A1 | Streamlit is the UI, so the design must work within Streamlit's layout options (see `ui-ux-requirements.md`, section 8). |
| A2 | Supabase hosts the database, sign-in, and product images. |
| A3 | Hosting is not decided yet (see ADR 0001). The `outbox/` folder works locally. On a cloud host its files may disappear on restart. That is acceptable for a demo. |
| A4 | All data is fake. People should use made-up names and test email addresses. |

## 10. Open questions

| # | Question | Owner |
|---|----------|-------|
| Q1 | What is the store's name? (Ideas: "Chip Lab", "Crunch Kitchen", "Flavor Drop") | Product owner |
| Q2 | Is 3 flavors per bag the right maximum? | Product owner |
| Q3 | Do we need an email confirmation step at registration, or turn it off for an easier demo? | Product owner |
| Q4 | Which hosting platform? (ADR 0001) | Tech lead |

## 11. Glossary

| Term | Meaning |
|------|---------|
| Base chip | The chip itself (cut, thickness, style). Example: Kettle Cooked. |
| Flavor add-on | A seasoning added to the bag. Example: Smoky BBQ. |
| Bag | One base chip plus its chosen flavors. This is what goes in the cart. |
| Outbox | The local folder where confirmation emails are saved as files. |
| RLS | Row Level Security, the Postgres feature that decides who can read or change each row. |
