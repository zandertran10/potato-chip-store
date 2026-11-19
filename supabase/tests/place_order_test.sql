-- Test: place_order cannot over-sell, and cannot run twice for the same key.
--
-- How to run: Supabase dashboard -> SQL Editor -> paste this whole file -> Run.
-- Needs: all migrations and supabase/seed/01_catalog.sql applied first.
-- Safe: everything happens inside BEGIN ... ROLLBACK, so nothing is saved.
-- Result: one row saying all tests passed, or a red error starting with "FAIL".

begin;

-- Setup (as the database owner) ----------------------------------------------
-- A throwaway shopper. The sign-up trigger gives them a customer profile.
insert into auth.users (id, email)
values ('00000000-0000-4000-8000-0000000009a1', 'test.shopper@demo.test');

-- Sweet Potato gets exactly 3 in stock, whatever earlier demos did to it.
update public.base_chips set stock = 3 where id = '00000000-0000-4000-8000-000000000104';

-- The shopper's cart: 4 bags of Sweet Potato + Cinnamon Sugar. Only 3 exist.
insert into public.carts (id, user_id)
values ('00000000-0000-4000-8000-0000000009b1', '00000000-0000-4000-8000-0000000009a1');
insert into public.cart_items (id, cart_id, base_chip_id, quantity)
values ('00000000-0000-4000-8000-0000000009c1', '00000000-0000-4000-8000-0000000009b1',
        '00000000-0000-4000-8000-000000000104', 4);
insert into public.cart_item_flavors (cart_item_id, flavor_id)
values ('00000000-0000-4000-8000-0000000009c1', '00000000-0000-4000-8000-000000000209');

-- From here on, act as that signed-in shopper, exactly like the app would.
select set_config('request.jwt.claims',
                  '{"sub": "00000000-0000-4000-8000-0000000009a1", "role": "authenticated"}', true);
set local role authenticated;


-- Test 1: cannot over-sell -----------------------------------------------------
do $$
begin
  begin
    perform * from public.place_order('Test Shopper', '1 Test Street',
                                      '00000000-0000-4000-8000-0000000009d1');
    raise exception 'FAIL test 1: an order was placed for 4 bags with only 3 in stock';
  exception when others then
    if sqlerrm not like 'OUT_OF_STOCK%' then
      raise;  -- a different error than expected: show it
    end if;
  end;

  if (select stock from public.base_chips where id = '00000000-0000-4000-8000-000000000104') <> 3 then
    raise exception 'FAIL test 1: stock changed even though the order failed';
  end if;
  if exists (select 1 from public.orders) then
    raise exception 'FAIL test 1: an order row exists after a failed checkout';
  end if;
end $$;


-- Test 2: same key twice = one order ------------------------------------------
do $$
declare
  first_call  record;
  second_call record;
begin
  -- Ask for 1 bag instead, so the order can succeed.
  update public.cart_items set quantity = 1 where id = '00000000-0000-4000-8000-0000000009c1';

  select * into first_call
  from public.place_order('Test Shopper', '1 Test Street', '00000000-0000-4000-8000-0000000009d2');

  -- Put a bag back in the cart, so a second order WOULD be possible without the key check.
  insert into public.cart_items (id, cart_id, base_chip_id, quantity)
  values ('00000000-0000-4000-8000-0000000009c2', '00000000-0000-4000-8000-0000000009b1',
          '00000000-0000-4000-8000-000000000104', 1);
  insert into public.cart_item_flavors (cart_item_id, flavor_id)
  values ('00000000-0000-4000-8000-0000000009c2', '00000000-0000-4000-8000-000000000209');

  -- "Place order" pressed again with the same key.
  select * into second_call
  from public.place_order('Test Shopper', '1 Test Street', '00000000-0000-4000-8000-0000000009d2');

  if second_call.order_id <> first_call.order_id or not second_call.already_placed then
    raise exception 'FAIL test 2: the second call did not return the first order';
  end if;
  if (select count(*) from public.orders) <> 1 then
    raise exception 'FAIL test 2: expected 1 order, found %', (select count(*) from public.orders);
  end if;
  if (select stock from public.base_chips where id = '00000000-0000-4000-8000-000000000104') <> 2 then
    raise exception 'FAIL test 2: stock should be 2 (3 minus one bag), not taken twice';
  end if;
end $$;


-- Undo everything this test did. (If a test failed, the script already stopped
-- with a red "FAIL" error and nothing was saved either.)
rollback;

-- Last, so the SQL Editor shows it as the result.
select 'PASS: place_order cannot over-sell and cannot run twice for the same key' as result;
