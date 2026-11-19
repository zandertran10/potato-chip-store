# Demo accounts and sample data

How to fill a Supabase project (dev or cloud demo) with the sample store and the three demo accounts.

**Passwords are never written in this repo.** The Tech Lead picks them when creating the users and shares them privately with the team (the same private channel as the Supabase anon key). Use different passwords for the dev and cloud demo projects.

## The three accounts

| Email | Role | Can do |
|---|---|---|
| `owner@demo.test` | owner | Everything, plus staff roles and store settings |
| `staff@demo.test` | staff | Manage chips, flavors, stock and orders |
| `customer@demo.test` | customer | Shop, check out, see own orders. Starts with 2 bags in the cart and 2 past orders |

`.test` is a reserved domain, so these addresses can never reach a real inbox.

## Steps (about 10 minutes)

Do these in order, in the Supabase dashboard for the project you're filling.

### 1. Database tables
Apply every file in `supabase/migrations/`, in number order (SQL Editor → New query → paste one file → Run).

### 2. Store catalog
SQL Editor → New query → paste all of `supabase/seed/01_catalog.sql` → Run.
This adds the settings row, 4 base chips, 10 flavors and 3 staff picks.

### 3. Create the three users
1. **Authentication → Users → Add user → Create new user.**
2. Email: `owner@demo.test`. Password: choose one (8+ characters, at least one letter and one number). Write it down somewhere private, **not** in the repo.
3. Tick **Auto Confirm User**, then **Create user**.
4. Repeat for `staff@demo.test` and `customer@demo.test`.

Each new user automatically gets a profile with the role `customer`.

### 4. Roles, cart and past orders
SQL Editor → New query → paste all of `supabase/seed/02_demo_accounts.sql` → Run.
This makes the owner and staff accounts, gives everyone a display name, fills the customer's cart (2 bags) and adds 2 past orders.

If it says *"Create owner@demo.test, staff@demo.test and customer@demo.test first"*, step 3 isn't finished.

### 5. Check it worked
```sql
select email, role, display_name from public.profiles order by role;
```
Expect 3 rows: owner, staff and customer.

### 6. Optional: prove the order function is safe
SQL Editor → paste all of `supabase/tests/place_order_test.sql` → Run.
Expect one row starting with **PASS**. The test undoes itself, so no data changes.

## Resetting the demo
Running steps 2 and 4 again is safe. Existing chips, flavors and orders are kept, and the customer's cart is reset to its 2 bags. Stock that was used up by test orders is **not** put back by the seed; change it in the admin Stock page, or in **Table Editor → base_chips / flavors**.

## Sharing with the team
- Send the 3 passwords privately (never in GitHub issues, pull requests, chat screenshots or prompts to Claude).
- After the class, change the passwords or delete the users in **Authentication → Users**.
