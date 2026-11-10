# 03: Non-Functional Requirements

These describe **how well** the app must work, not what it does.

This is a classroom demo, so the targets are small. The security practices are real, though, so learners see how it should be done in a production app.

- **Priority:** **Must** / **Should** / **Could**
- **IDs:** `NFR-<AREA>-<number>`

---

## 1. Authentication

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-AUTH-01 | All sign-in uses **Supabase Auth** with email and password. The app never stores or handles passwords itself. | Must |
| NFR-AUTH-02 | Passwords are at least 8 characters, with at least one letter and one number. This is set in Supabase Auth and shown on the form. | Must |
| NFR-AUTH-03 | A failed sign-in shows one general message ("Email or password is incorrect") and never says which part was wrong. | Must |
| NFR-AUTH-04 | The session is kept in Streamlit session state only, never in links or logs. Signing out clears it and calls Supabase sign-out. | Must |
| NFR-AUTH-05 | Sessions use Supabase's token lifetime (1 hour, renewed while active). When a session expires, the user is asked to sign in again and their cart is kept. | Should |
| NFR-AUTH-06 | Supabase's built-in sign-in rate limits stay on, to slow down password guessing. | Must |
| NFR-AUTH-07 | Email confirmation at sign-up is **off** for local and class demos and **on** in production. Locally, test emails can be read in Supabase's built-in mail viewer (Inbucket). | Should |
| NFR-AUTH-08 | The password reset uses Supabase's reset flow and shows the same message whether or not the email exists. | Should |

## 2. Security

### 2.1 Access control (Row Level Security)

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SEC-01 | Roles are `customer`, `staff` and `owner`, stored in a `profiles` table linked to `auth.users`. New users are always `customer`. | Must |
| NFR-SEC-02 | **Row Level Security (RLS) is enabled on every table**, in the same migration that creates the table. | Must |
| NFR-SEC-03 | Customers can only read and change their own profile, cart and orders. | Must |
| NFR-SEC-04 | Anyone can read *active* chips, flavors and staff picks. Only staff and owner can add or change them. | Must |
| NFR-SEC-05 | Only the owner can change roles, and nobody can change their own role. The database enforces this, not only the screen. | Must |
| NFR-SEC-06 | Every admin page checks the user's role on the server each time it loads. Hiding a link is not enough. | Must |
| NFR-SEC-07 | Stock and order changes only happen through database functions that check the caller's role. | Must |
| NFR-SEC-08 | Each RLS rule has a test: a customer can't see another customer's order, and a customer can't edit products. | Should |

### 2.2 Keys and secrets

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SEC-09 | **Keys are never committed.** They go in `.env` or `.streamlit/secrets.toml` (both gitignored). Only `.example` files with empty values are in the repo. | Must |
| NFR-SEC-10 | The app uses only the Supabase **anon (public) key** plus the signed-in user's session. The **service role key** is never used in the app; it is only used locally by the seed script. | Must |
| NFR-SEC-11 | Keys for CI and hosting are stored in GitHub Secrets or the host's secrets settings, never in workflow files. | Must |
| NFR-SEC-12 | Keys are never pasted into prompts, issues, pull requests, chat or screenshots. | Must |

### 2.3 Input and output

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SEC-13 | All user input is checked (type, length, range) before saving. The database also checks it with constraints such as `price > 0` and `stock >= 0`. | Must |
| NFR-SEC-14 | The database is only called through the Supabase client or database functions with parameters. SQL is never built by joining strings. | Must |
| NFR-SEC-15 | Text entered by users is shown as plain text, never as raw HTML (no `unsafe_allow_html` with user text). | Must |
| NFR-SEC-16 | Image uploads must be JPG, PNG or WebP and 2 MB or smaller, and only staff and owner can upload them. | Must |
| NFR-SEC-17 | Error messages shown to users never include technical details, SQL or keys. | Must |
| NFR-SEC-18 | All hosted environments use HTTPS. | Must |
| NFR-SEC-19 | Dependencies have version ranges in `requirements.txt` and are checked with `pip-audit` before each release. | Should |

## 3. Privacy and child safety

This project may be used in trainings that include minors.

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-PRIV-01 | Only the data that's needed is stored: display name, email and delivery address. No date of birth, phone number or payment data. | Must |
| NFR-PRIV-02 | All demo data is fictional. Learners use made-up names and test email addresses (for example `name@demo.test`). | Must |
| NFR-PRIV-03 | Every screen shows that this is a demo store (footer, plus a banner at checkout). | Must |
| NFR-PRIV-04 | All text, images, product names, seed data and AI-generated content are age-appropriate. | Must |
| NFR-PRIV-05 | No pressure tactics: no fake timers, no fake scarcity, no streaks (see doc 02, section 4). | Must |
| NFR-PRIV-06 | No tracking or analytics tools; Streamlit usage statistics are turned off. | Must |
| NFR-PRIV-07 | Allergen information is shown for every chip and flavor. | Must |
| NFR-PRIV-08 | An owner can delete a customer account. Their orders are kept, but with the name, email and address removed. | Could |

## 4. Data integrity

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-DI-01 | Placing an order is done by **one database function** (`place_order`) that, in a single transaction, locks the rows, checks stock, deducts stock, and creates the order and its lines. All or nothing. | Must |
| NFR-DI-02 | **No overselling:** stock can never go below 0, enforced by a database constraint and by the function's check. | Must |
| NFR-DI-03 | If two people buy the last bag at the same moment, one succeeds and the other gets a clear "just sold out" message. | Must |
| NFR-DI-04 | **No double orders:** each checkout attempt has a unique key. Sending it again returns the same order instead of creating a new one. | Must |
| NFR-DI-05 | Order lines keep the names and prices from the time of purchase. | Must |
| NFR-DI-06 | Chips and flavors that appear in orders are never deleted, only made inactive. | Must |
| NFR-DI-07 | Every stock change is recorded with who made it, when, the amount and the reason. | Should |
| NFR-DI-08 | The outbox email is written only **after** the order is saved. If writing it fails, the error is logged and the order still succeeds. | Must |

## 5. Performance

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-PERF-01 | Pages load within about 2 seconds with the seed data on a normal connection. | Should |
| NFR-PERF-02 | Search results appear within 1 second. | Should |
| NFR-PERF-03 | Catalog lists are cached for 60 seconds (`st.cache_data`), and the cache is cleared right after an admin edit. | Should |
| NFR-PERF-04 | Product images are 1200 px wide or smaller. | Could |
| NFR-PERF-05 | Database columns used for searching and joining have indexes. | Should |

## 6. Usability and accessibility

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UX-01 | Customer screens target **WCAG 2.1 level AA** (details in doc 02, section 8). | Should |
| NFR-UX-02 | Works on the latest Chrome, Edge, Firefox and Safari, on desktop and on phones from 360 px wide. | Must |
| NFR-UX-03 | Every action gives visible feedback within 1 second (a spinner, toast or change on screen). | Must |
| NFR-UX-04 | The whole site can be used with a keyboard. | Should |
| NFR-UX-05 | A new shopper can complete Flow A (doc 02, section 6) in under 3 minutes without help. | Should |

## 7. Reliability and error handling

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-REL-01 | If Supabase can't be reached, the app shows a friendly "taking a snack break" message instead of crashing. | Must |
| NFR-REL-02 | Every database call is wrapped in error handling. The user sees a plain message and a "Try again" option; the details are logged. | Must |
| NFR-REL-03 | Unexpected errors on a page don't break the rest of the app. Navigation keeps working. | Should |
| NFR-REL-04 | The database can be rebuilt from scratch with `supabase/migrations/` and `supabase/seed/`. | Must |

## 8. Maintainability and code quality

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MNT-01 | Code follows the folder layout: `app/pages` (screens), `app/components` (UI pieces), `app/services` (all database calls), `app/models` (data classes), `app/utils` (helpers), `app/config` (settings and secrets loading). | Must |
| NFR-MNT-02 | Pages never call Supabase directly. They only use `app/services`. | Must |
| NFR-MNT-03 | Every database change is a migration file in `supabase/migrations/`. Nobody edits the hosted database by hand. | Must |
| NFR-MNT-04 | Code passes `ruff` (style and lint checks) and has type hints on public functions. | Must |
| NFR-MNT-05 | Tests: unit tests in `tests/unit` (pricing, flavor limit, cart merge, outbox) and integration tests in `tests/integration` (`place_order`, RLS rules). | Must |
| NFR-MNT-06 | CI (GitHub Actions) runs lint and tests on every pull request. `main` only accepts reviewed pull requests that pass CI. | Must |
| NFR-MNT-07 | Big technical choices are recorded as ADRs in `docs/architecture/decisions/`. | Must |
| NFR-MNT-08 | The README explains how to run the app locally in a few steps. | Must |

## 9. Logging

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-LOG-01 | The app uses Python's `logging` module with levels (INFO, WARNING, ERROR), not `print`. | Must |
| NFR-LOG-02 | Logged events: order placed or cancelled, stock changed, role changed, failed sign-in, errors. | Should |
| NFR-LOG-03 | Logs never contain passwords, tokens, keys or full addresses. Emails are partly hidden (`j***@demo.test`). | Must |
| NFR-LOG-04 | Each log line includes the time, level, area and the order number where there is one. | Should |

## 10. Deployment and environments

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-DEP-01 | There are three environments: **Local** (local Supabase with Docker, or a personal free project), **Staging** (a shared Supabase project; the app is deployed from `main`), and **Production** (a separate Supabase project; deployed from release tags). | Should |
| NFR-DEP-02 | The app is hosted on **Streamlit Community Cloud** (recommended in ADR 0001). The entry point is `app/main.py`. | Should |
| NFR-DEP-03 | Settings come only from environment variables or secrets, so the same code runs in every environment without changes. | Must |
| NFR-DEP-04 | Releases are tagged with versions (`v1.0.0`) and published as GitHub Releases. | Must |
| NFR-DEP-05 | Migrations are applied to staging before production. | Must |
| NFR-DEP-06 | Rollback: redeploy the previous tag, or revert the faulty commit and release a new patch version. | Should |
| NFR-DEP-07 | Streamlit Community Cloud may wipe local files when the app restarts, so the `outbox/` folder there is temporary. This is accepted for the demo. | Must |

## 11. Scalability limits

This demo is **not** designed to scale. The expected limits are:

| ID | Limit |
|----|-------|
| NFR-SCALE-01 | Up to about 30 people using it at once (a class). |
| NFR-SCALE-02 | Up to about 100 chips and flavors, and about 1,000 orders. |
| NFR-SCALE-03 | It must stay within the free tiers of Supabase and Streamlit Community Cloud. |
| NFR-SCALE-04 | There are no background jobs, queues or caching servers. The app and the database are enough. |

## 12. Constraints and assumptions

| ID | Constraint / assumption |
|----|-------------------------|
| NFR-CON-01 | Tech stack: Python 3.11+, Streamlit 1.57+, Supabase (Postgres, Auth, Storage). |
| NFR-CON-02 | Streamlit limits the layout and styling (see doc 02, section 10). |
| NFR-CON-03 | There are no real payments and no real emails. Confirmations are saved as `.eml` files. |
| NFR-CON-04 | Code is on GitHub. Work happens through issues, branches and pull requests. |
| NFR-CON-05 | The team is 4 people: a tech lead plus 3 developers (see `docs/planning/work-division-plan.md`). |
| NFR-CON-06 | Production rules that are left out for the demo: payment card security (PCI DSS), full privacy-law processes, uptime guarantees, backups, load testing, multi-factor sign-in and penetration testing. |
