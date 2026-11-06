# Non-Functional Requirements

These describe **how well** the app must work, not what it does. This is a learning and demo app, so the targets are set to teach good habits without production-level cost.

Priority: **Must** / **Should** / **Could**.

---

## 1. Authentication (sign-in)

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-AUTH-01 | All sign-in uses **Supabase Auth** with email and password. The app never stores or handles passwords itself. | Must |
| NFR-AUTH-02 | Passwords: at least 8 characters, with at least one letter and one number. This is set in the Supabase Auth settings and shown on the form. | Must |
| NFR-AUTH-03 | Failed sign-in shows one general message ("Email or password is incorrect"), never which part was wrong. | Must |
| NFR-AUTH-04 | Sessions are kept in Streamlit session state only, never in URLs or logs. Sign-out clears the session and calls Supabase sign-out. | Must |
| NFR-AUTH-05 | Sessions expire after Supabase's token lifetime (default 1 hour, auto-refreshed while active). Expired sessions return the user to sign in, keeping their cart. | Should |
| NFR-AUTH-06 | Supabase's built-in sign-in rate limits stay switched on to slow down password guessing. | Must |
| NFR-AUTH-07 | Email confirmation at sign-up can be turned on or off (requirements Q3). For local demos, test emails are viewed in Supabase's local email inbox (Inbucket). | Should |
| NFR-AUTH-08 | Password reset uses Supabase's reset flow. | Should |

## 2. Authorization (roles and access)

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-AZ-01 | Roles are `customer`, `staff`, `owner`, stored in a `profiles` table linked to `auth.users`. New users are always `customer`. | Must |
| NFR-AZ-02 | **Row Level Security is enabled on every table** (project rule in `CLAUDE.md`). | Must |
| NFR-AZ-03 | Customers can read and change only their own profile, cart, and orders. | Must |
| NFR-AZ-04 | Anyone can read *active* products and flavors. Only staff and owner can add or change them. | Must |
| NFR-AZ-05 | Only the owner can change roles. A user cannot change their own role. This is enforced in the database, not only hidden in the UI. | Must |
| NFR-AZ-06 | Admin pages check the role on the server side every time they load. Hiding a link is not enough. | Must |
| NFR-AZ-07 | The app uses the Supabase **anon (public) key** plus the signed-in user's session. The **service role key** is never used in the Streamlit app; it is only used by the seed script run locally. | Must |

## 3. Data protection and secrets

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SEC-01 | No secrets in code or git. Keys go in environment variables or `.streamlit/secrets.toml` (gitignored); `secrets.toml.example` holds placeholders only. | Must |
| NFR-SEC-02 | No payment data is ever collected or stored. | Must |
| NFR-SEC-03 | Only the personal data needed is stored: name, email, delivery address. Demo users are told to use made-up data. | Must |
| NFR-SEC-04 | All user input is validated (type, length, range) before it is saved. The database also enforces rules with constraints (for example `price > 0`, `stock >= 0`). | Must |
| NFR-SEC-05 | Database access goes through the Supabase client or database functions with parameters, never SQL built by joining strings. | Must |
| NFR-SEC-06 | User-entered text (product names, descriptions) is displayed as plain text, not raw HTML (no `unsafe_allow_html` with user content). | Must |
| NFR-SEC-07 | Image uploads: only JPG, PNG, or WebP up to 2 MB. Only staff and owner can upload. The bucket can be read publicly but only staff can write to it. | Must |
| NFR-SEC-08 | All traffic uses HTTPS in any hosted environment. | Must |
| NFR-SEC-09 | Error messages shown to users never include stack traces, SQL, or keys. Details go to the server log. | Must |
| NFR-SEC-10 | Dependencies come from `requirements.txt` with version ranges and are checked occasionally with `pip-audit`. | Should |

## 4. Data integrity (stock and orders)

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-DI-01 | Placing an order is done by **one Postgres function** (RPC) that checks stock, locks the rows, deducts stock, and creates the order and its lines in one transaction. All or nothing. | Must |
| NFR-DI-02 | Stock can never go below zero (database `CHECK (stock >= 0)` plus the check in the function). | Must |
| NFR-DI-03 | Two people buying the last bag at the same time: one succeeds and the other gets a clear "just sold out" message. | Must |
| NFR-DI-04 | Placing an order twice by accident (double click, retry) does not create a duplicate. Each attempt carries a unique key. | Must |
| NFR-DI-05 | Order lines store the price and name at the time of purchase. | Must |
| NFR-DI-06 | Products and flavors that appear in orders are never hard-deleted (they are made inactive instead). | Must |
| NFR-DI-07 | Every stock change (order, cancel, manual restock) is recorded with who, when, how much, and why. | Should |

## 5. Confirmation email files (outbox)

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-OUT-01 | Confirmation emails are written as `.eml` files to an `outbox/` folder (path set in config). No SMTP, nothing is sent. | Must |
| NFR-OUT-02 | `outbox/` is gitignored. | Must |
| NFR-OUT-03 | Writing the file happens **after** the order is saved. A failure to write is logged and does not undo the order. | Must |
| NFR-OUT-04 | File names use only the order number (no customer names or emails in file names). | Should |
| NFR-OUT-05 | On cloud hosts the folder may be wiped on restart. This is accepted for the demo and noted in the README. | Must |

## 6. Performance

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-PERF-01 | Pages load within about 2 seconds with seed data (about 50 products and flavors) on a normal connection. | Should |
| NFR-PERF-02 | Search results appear within 1 second. | Should |
| NFR-PERF-03 | Product and flavor lists are cached briefly (for example `st.cache_data` with a 60-second time limit) and refreshed right after an admin edit. | Should |
| NFR-PERF-04 | Product images are resized to 1200 px wide or less before upload or display. | Could |

## 7. Usability and accessibility

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UX-01 | Target **WCAG 2.1 level AA** for customer pages (details in `ui-ux-requirements.md`, section 7). | Should |
| NFR-UX-02 | Works on the latest Chrome, Edge, Firefox, and Safari, on desktop and on a phone (at least 360 px wide). | Must |
| NFR-UX-03 | Every action gives visible feedback within 1 second. | Must |
| NFR-UX-04 | The whole site can be used with a keyboard. | Should |

## 8. Content and audience

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-CNT-01 | All text, images, seed data, and flavor names are **age-appropriate**, because the project is used in trainings that may include minors. | Must |
| NFR-CNT-02 | The UI clearly says it is a demo store (footer and checkout banner). | Must |
| NFR-CNT-03 | Allergen information is shown for every product and flavor. | Must |

## 9. Reliability and operations

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-OPS-01 | When Supabase can't be reached, the app shows a friendly "store is taking a snack break" message, not a crash. | Should |
| NFR-OPS-02 | The app logs errors and key events (order placed, role changed, sign-in failed) with Python `logging`. Logs never contain passwords, tokens, or full addresses. | Should |
| NFR-OPS-03 | The database can be rebuilt from scratch with `supabase/migrations/` + `supabase/seed/`. | Must |
| NFR-OPS-04 | There are two environments, local and hosted, set up through config only (no code changes). | Should |

## 10. Maintainability and quality

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MNT-01 | Code follows the folder layout in `CLAUDE.md` (`app/pages`, `app/components`, `app/services`, `app/utils`). Database calls live only in `app/services`. | Must |
| NFR-MNT-02 | Every database change is a migration file in `supabase/migrations/`. | Must |
| NFR-MNT-03 | Automated tests (pytest) cover: price calculation, flavor limit, cart merge, and the order function (including the "last bag" case). | Should |
| NFR-MNT-04 | Major technical choices are recorded as ADRs in `docs/design/decisions/`. | Must |
| NFR-MNT-05 | The README explains how to run locally in a few steps (install, configure secrets, migrate, seed, run). | Must |

## 11. Out of scope for a demo

These would be needed for a real store but are intentionally left out: payment card security standards (PCI DSS), full privacy law compliance (GDPR/CCPA) processes, uptime guarantees, backups and disaster recovery, load testing, multi-factor authentication, and a security penetration test.
