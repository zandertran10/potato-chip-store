-- Seed 02: demo account roles, the demo customer's cart and 2 past orders.
-- Run AFTER 01_catalog.sql AND after creating the 3 demo users in the Supabase
-- dashboard (docs/deployment/demo-accounts.md). No passwords are stored here.
-- Safe to run more than once.

-- If the users were created BEFORE the migrations ran, the "new user ->
-- profile" trigger didn't exist yet and they have no profile. Make them now.
insert into public.profiles (id, display_name, email, role)
select u.id, split_part(lower(u.email), '@', 1), lower(u.email), 'customer'
from auth.users u
where lower(u.email) in ('owner@demo.test', 'staff@demo.test', 'customer@demo.test')
on conflict (id) do nothing;

do $$
declare
  v_owner_id    uuid := (select id from public.profiles where lower(email) = 'owner@demo.test');
  v_staff_id    uuid := (select id from public.profiles where lower(email) = 'staff@demo.test');
  v_customer_id uuid := (select id from public.profiles where lower(email) = 'customer@demo.test');
  v_cart_id     uuid;
  v_missing     text := concat_ws(', ',
                          case when v_owner_id is null then 'owner@demo.test' end,
                          case when v_staff_id is null then 'staff@demo.test' end,
                          case when v_customer_id is null then 'customer@demo.test' end);
begin
  if v_missing <> '' then
    raise exception 'These demo users don''t exist yet: %. Create them in Authentication > Users '
                    '(see docs/deployment/demo-accounts.md), then run this again.', v_missing;
  end if;

  -- Roles and friendly names. New sign-ups are always "customer", so the owner
  -- and staff roles are set here (this runs as the database owner in the SQL Editor).
  update public.profiles set role = 'owner', display_name = 'Olive Owner' where id = v_owner_id;
  update public.profiles set role = 'staff', display_name = 'Sam Staff' where id = v_staff_id;
  update public.profiles
  set role = 'customer', display_name = 'Casey Customer',
      default_address = '12 Demo Lane, Springfield'
  where id = v_customer_id;

  -- The demo customer's cart: 2 bags (doc 01 section 5).
  insert into public.carts (user_id) values (v_customer_id)
  on conflict (user_id) do nothing;
  select id into v_cart_id from public.carts where user_id = v_customer_id;

  -- Start from an empty cart so running this twice doesn't double the bags.
  delete from public.cart_items where cart_id = v_cart_id;

  insert into public.cart_items (id, cart_id, base_chip_id, quantity) values
    -- Kettle Cooked + Salt & Vinegar + Sea Salt, x2
    ('00000000-0000-4000-8000-000000000801', v_cart_id, '00000000-0000-4000-8000-000000000102', 2),
    -- Wavy Ridge + Smoky BBQ, x1
    ('00000000-0000-4000-8000-000000000802', v_cart_id, '00000000-0000-4000-8000-000000000103', 1);

  insert into public.cart_item_flavors (cart_item_id, flavor_id) values
    ('00000000-0000-4000-8000-000000000801', '00000000-0000-4000-8000-000000000202'),
    ('00000000-0000-4000-8000-000000000801', '00000000-0000-4000-8000-000000000201'),
    ('00000000-0000-4000-8000-000000000802', '00000000-0000-4000-8000-000000000204');

  -- 2 past orders, so "My orders" and the admin orders page have something to show.
  -- They are sample history only: they don't change today's stock, so the stock
  -- numbers stay exactly as listed in doc 01 section 5.
  insert into public.orders
    (id, order_number, user_id, status, delivery_name, delivery_address, total,
     idempotency_key, created_at)
  values
    ('00000000-0000-4000-8000-000000000501', 'CHIP-20261101-0001', v_customer_id, 'shipped',
     'Casey Customer', '12 Demo Lane, Springfield', 9.25,
     '00000000-0000-4000-8000-000000000701', '2026-11-01 15:30:00+00'),
    ('00000000-0000-4000-8000-000000000502', 'CHIP-20261110-0001', v_customer_id, 'placed',
     'Casey Customer', '12 Demo Lane, Springfield', 3.50,
     '00000000-0000-4000-8000-000000000702', '2026-11-10 18:05:00+00')
  on conflict (id) do nothing;

  -- Order lines, with names and prices copied as they were at purchase time.
  insert into public.order_items
    (id, order_id, base_chip_id, base_name, base_price, unit_price, quantity, line_total)
  values
    -- Order 1: Classic Thin + Sea Salt, x2 = 2 x (2.50 + 0.25) = 5.50
    ('00000000-0000-4000-8000-000000000601', '00000000-0000-4000-8000-000000000501',
     '00000000-0000-4000-8000-000000000101', 'Classic Thin', 2.50, 2.75, 2, 5.50),
    -- Order 1: Wavy Ridge + Zesty Lime + Chili Kick, x1 = 2.75 + 0.40 + 0.60 = 3.75
    ('00000000-0000-4000-8000-000000000602', '00000000-0000-4000-8000-000000000501',
     '00000000-0000-4000-8000-000000000103', 'Wavy Ridge', 2.75, 3.75, 1, 3.75),
    -- Order 2: Kettle Cooked + Sour Cream & Onion, x1 = 3.00 + 0.50 = 3.50
    ('00000000-0000-4000-8000-000000000603', '00000000-0000-4000-8000-000000000502',
     '00000000-0000-4000-8000-000000000102', 'Kettle Cooked', 3.00, 3.50, 1, 3.50)
  on conflict (id) do nothing;

  insert into public.order_item_flavors (order_item_id, flavor_id, flavor_name, flavor_price)
  values
    ('00000000-0000-4000-8000-000000000601', '00000000-0000-4000-8000-000000000201', 'Sea Salt', 0.25),
    ('00000000-0000-4000-8000-000000000602', '00000000-0000-4000-8000-000000000206', 'Zesty Lime', 0.40),
    ('00000000-0000-4000-8000-000000000602', '00000000-0000-4000-8000-000000000207', 'Chili Kick', 0.60),
    ('00000000-0000-4000-8000-000000000603', '00000000-0000-4000-8000-000000000203', 'Sour Cream & Onion', 0.50)
  on conflict do nothing;
end $$;
