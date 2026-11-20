# Product and technical decisions

This file records the answers to the open questions in [doc 00 §8](../requirements/00-consolidated-requirements.md#8-open-questions) (work plan item F7), and other choices made while building. If a decision changes, add a new dated entry instead of editing the old one, so the history stays readable. Bigger technical choices also get an ADR in [decisions/](decisions/).

## Open questions from doc 00 §8

| # | Question | Decision | Notes |
|---|---|---|---|
| Q1 | Store name? | **Potato Chip Co.** (not the default "Chip Lab") | Fictional; home-made organic chips. Material "bakery_dining" icon, no designed logo. |
| Q2 | Max flavors per bag? | **3**, a store setting the owner can change (1-5) | US-706; `settings.max_flavors` |
| Q3 | Email confirmation at sign-up? | **Off** for the dev project and class demos | The app also handles it being on (register then asks to confirm). |
| Q4 | Hosting? | **Streamlit Community Cloud**, main file `app/streamlit_app.py` | ADR 0001 (accepted). Vercel can't run a Streamlit app's long-lived connection. |
| Q5 | Guest checkout? | **No.** Guests browse and use the cart; checkout needs sign-in, and the cart is kept on sign-in | US-305, US-401 |
| Q6 | Currency? | **USD**, 2 decimals, stored as `numeric` (never floating point) | Bag prices are about $2.50 to $5 |
| Q7 | Product images? | Free-to-use photos or simple illustrations in the `product-images` bucket (JPG/PNG/WebP, 2 MB) | Seed chips start with no photo and show a placeholder |
| Q8 | Team size? | Planned as 4 (Tech Lead + 3). **In practice: the Tech Lead with Claude Code** | The plan's 3 story lists are kept as the build order |

## Other decisions

### D1. Forgot password: "Ask your trainer", no email (2026-11-19)
**Decision.** The "Forgot password?" page tells the user to ask their trainer, who resets the account in the Supabase dashboard; the user then registers again. No reset email is sent and the page asks for no email address.
**Why.** Doc 00 §7 lists "sending real emails" as out of scope, learners use made-up `@demo.test` addresses, and many are minors. The overseer's reference app made the same choice.
**Changed.** US-503 and NFR-AUTH-08 were updated to match; `auth.reset_password` was removed.
**Update 2026-11-19.** The page now speaks like a real store: *"Contact our customer support team and we'll reset your account for you."* In class, the support team is the trainer. Same behaviour: no email box, nothing is sent.

### D2. Admin pages exist only for staff and the owner (2026-11-18)
**Decision.** Guests and customers don't get the Store Admin pages at all: not in the menu, and an admin address opens Home. Staff get Base chips, Flavors, Stock and Orders; the owner also gets Staff, Settings and Dashboard.
**Why.** The store's internal structure stays out of customers' sight. Security still comes from each page's role check and the database's RLS rules, not from hiding.

### D3. Sign-in lasts for the browser tab (2026-11-18)
**Decision.** The sign-in is kept in Streamlit's session only (NFR-AUTH-04), so refreshing the browser tab signs you out. Accepted for the demo; moving around with the menu keeps you signed in.

### D4. Supabase key: the publishable key only (2026-11-19)
**Decision.** The app uses only the publishable key (`sb_publishable_...`, formerly "anon"). It refuses a secret key (`sb_secret_...`, formerly "service role"). The setting is called `SUPABASE_PUBLISHABLE_KEY`; the older name `SUPABASE_ANON_KEY` still works.

### D5. No passwords in the repo (2026-11-16)
**Decision.** Demo account passwords are chosen in the Supabase dashboard and shared privately. Doc 01 §5 said they would be in the README; that line is replaced. See [docs/deployment/demo-accounts.md](../deployment/demo-accounts.md).

### D6. Page files stay in `app/pages/` (2026-11-19)
**Decision.** Keep `app/pages/`, as in the work plan, `CLAUDE.md` and the playbook template. The overseer's reference app uses `app/views/` (Streamlit's advice, to avoid its older page auto-discovery); here `st.navigation` already overrides that, and moving 20 files would change nothing users see.
