-- 10. place_order: turns the signed-in customer's cart into an order, all or nothing.
-- Requirements: NFR-DI-01 to NFR-DI-05, NFR-DI-07, BR-01 to BR-08, US-402.
--
-- Everything below runs in ONE transaction. If any step fails, Postgres undoes
-- every earlier step: no half-made order, no stock taken without an order.
--
-- How the app calls it (from app/services/orders.py):
--   supabase.rpc("place_order", {"p_delivery_name": ..., "p_delivery_address": ...,
--                                "p_idempotency_key": <one uuid per checkout attempt>})
--
-- Errors start with a code the app can check, then a sentence it can show:
--   NOT_SIGNED_IN, MISSING_KEY, MISSING_DELIVERY, KEY_ALREADY_USED, CART_EMPTY,
--   INVALID_BAG, OUT_OF_STOCK, TOO_MANY_ORDERS_TODAY

create or replace function public.place_order(
  p_delivery_name    text,
  p_delivery_address text,
  p_idempotency_key  uuid
)
returns table (order_id uuid, order_number text, total numeric, already_placed boolean)
language plpgsql
-- security definer: runs as the table owner, because customers have no right to
-- write orders or change stock themselves (NFR-SEC-07). That's why every check
-- below uses the caller's own id from auth.uid().
security definer
set search_path = ''
-- Never wait more than 5 seconds for another checkout's locks (keeps transactions short).
set lock_timeout = '5s'
as $$
-- The output columns (order_id, order_number, total) share names with table
-- columns. This tells Postgres a bare name always means the table column.
#variable_conflict use_column
declare
  v_user_id      uuid := (select auth.uid());
  v_cart_id      uuid;
  v_existing     public.orders%rowtype;
  v_max_flavors  smallint;
  v_problems     text[];
  v_today        text := to_char(now() at time zone 'utc', 'YYYYMMDD');
  v_next_number  integer;
  v_order_id     uuid := gen_random_uuid();
  v_order_number text;
  v_total        numeric(8,2);
  v_line         record;
  v_flavor_total numeric(8,2);
  v_item_id      uuid;
begin
  -- 1. Basic checks -----------------------------------------------------------
  if v_user_id is null then
    raise exception 'NOT_SIGNED_IN: Please sign in to place an order.';
  end if;

  if p_idempotency_key is null then
    raise exception 'MISSING_KEY: Every checkout needs an idempotency key.';
  end if;

  if coalesce(trim(p_delivery_name), '') = '' or coalesce(trim(p_delivery_address), '') = '' then
    raise exception 'MISSING_DELIVERY: Please enter a delivery name and address.';
  end if;

  -- 2. Same key = same order (NFR-DI-04) --------------------------------------
  -- If "Place order" is pressed twice, both calls send the same key. This lock
  -- makes the second call wait until the first has finished, then it finds the
  -- order the first call made and returns it instead of making a new one.
  perform pg_advisory_xact_lock(hashtext('place_order:' || p_idempotency_key::text));

  select * into v_existing
  from public.orders o
  where o.idempotency_key = p_idempotency_key;

  if found then
    if v_existing.user_id is distinct from v_user_id then
      raise exception 'KEY_ALREADY_USED: This checkout key belongs to another order.';
    end if;
    return query select v_existing.id, v_existing.order_number, v_existing.total, true;
    return;
  end if;

  -- 3. The cart must have at least one valid bag ------------------------------
  select c.id into v_cart_id from public.carts c where c.user_id = v_user_id;

  if v_cart_id is null
     or not exists (select 1 from public.cart_items i where i.cart_id = v_cart_id) then
    raise exception 'CART_EMPTY: Your cart is empty.';
  end if;

  select s.max_flavors into v_max_flavors from public.settings s where s.id = 1;
  v_max_flavors := coalesce(v_max_flavors, 3);

  -- Every bag has 1 to max_flavors flavors (BR-01).
  if exists (
    select 1
    from public.cart_items i
    left join public.cart_item_flavors f on f.cart_item_id = i.id
    where i.cart_id = v_cart_id
    group by i.id
    having count(f.flavor_id) < 1 or count(f.flavor_id) > v_max_flavors
  ) then
    raise exception 'INVALID_BAG: Every bag needs 1 to % flavors.', v_max_flavors;
  end if;

  -- 4. Lock the chips and flavors in this cart (NFR-DI-03) --------------------
  -- FOR UPDATE makes any other checkout that wants the same rows wait until we
  -- finish. Locking in id order, chips before flavors, means two checkouts always
  -- queue in the same order and can never deadlock.
  perform 1
  from public.base_chips b
  where b.id in (select i.base_chip_id from public.cart_items i where i.cart_id = v_cart_id)
  order by b.id
  for update;

  perform 1
  from public.flavors fl
  where fl.id in (
    select f.flavor_id
    from public.cart_item_flavors f
    join public.cart_items i on i.id = f.cart_item_id
    where i.cart_id = v_cart_id
  )
  order by fl.id
  for update;

  -- 5. Check stock again, now that nobody else can change it (BR-03, BR-05) ----
  -- One bag uses 1 unit of its base chip and 1 unit of each of its flavors.
  with needed as (
    select 'base'::text as item_type, i.base_chip_id as item_id, sum(i.quantity)::integer as amount
    from public.cart_items i
    where i.cart_id = v_cart_id
    group by i.base_chip_id
    union all
    select 'flavor', f.flavor_id, sum(i.quantity)::integer
    from public.cart_item_flavors f
    join public.cart_items i on i.id = f.cart_item_id
    where i.cart_id = v_cart_id
    group by f.flavor_id
  ),
  available as (
    select 'base'::text as item_type, b.id, b.name, b.stock, b.is_active from public.base_chips b
    union all
    select 'flavor', fl.id, fl.name, fl.stock, fl.is_active from public.flavors fl
  )
  select array_agg(
           case when not a.is_active then format('%s (no longer sold)', a.name)
                else format('%s (%s left, %s needed)', a.name, a.stock, n.amount) end
           order by a.name)
    into v_problems
  from needed n
  join available a on a.item_type = n.item_type and a.id = n.item_id
  where not a.is_active or a.stock < n.amount;

  if v_problems is not null then
    -- Raising here undoes everything: no order is created (US-402 AC2).
    raise exception 'OUT_OF_STOCK: Not enough stock for: %', array_to_string(v_problems, ', ');
  end if;

  -- 6. Order number CHIP-YYYYMMDD-#### (BR-08) --------------------------------
  -- The lock stops two orders taking the same number at the same moment.
  perform pg_advisory_xact_lock(hashtext('place_order:order_number'));

  select coalesce(max(substring(o.order_number from 15)::integer), 0) + 1
    into v_next_number
  from public.orders o
  where o.order_number like 'CHIP-' || v_today || '-%';

  if v_next_number > 9999 then
    raise exception 'TOO_MANY_ORDERS_TODAY: The store has reached its daily order limit.';
  end if;

  v_order_number := format('CHIP-%s-%s', v_today, lpad(v_next_number::text, 4, '0'));

  -- 7. Create the order and copy names and prices into it (NFR-DI-05) ---------
  -- The total starts at 0 and is filled in once all the lines exist.
  insert into public.orders
    (id, order_number, user_id, delivery_name, delivery_address, total, idempotency_key)
  values
    (v_order_id, v_order_number, v_user_id, trim(p_delivery_name), trim(p_delivery_address),
     0, p_idempotency_key);

  for v_line in
    select i.id as cart_item_id, i.quantity, b.id as base_chip_id, b.name as base_name,
           b.price as base_price
    from public.cart_items i
    join public.base_chips b on b.id = i.base_chip_id
    where i.cart_id = v_cart_id
    order by i.created_at
  loop
    -- Bag price = base chip price + each flavor's price (BR-02).
    select coalesce(sum(fl.price), 0) into v_flavor_total
    from public.cart_item_flavors f
    join public.flavors fl on fl.id = f.flavor_id
    where f.cart_item_id = v_line.cart_item_id;

    v_item_id := gen_random_uuid();

    insert into public.order_items
      (id, order_id, base_chip_id, base_name, base_price, unit_price, quantity, line_total)
    values
      (v_item_id, v_order_id, v_line.base_chip_id, v_line.base_name, v_line.base_price,
       v_line.base_price + v_flavor_total, v_line.quantity,
       (v_line.base_price + v_flavor_total) * v_line.quantity);

    insert into public.order_item_flavors (order_item_id, flavor_id, flavor_name, flavor_price)
    select v_item_id, fl.id, fl.name, fl.price
    from public.cart_item_flavors f
    join public.flavors fl on fl.id = f.flavor_id
    where f.cart_item_id = v_line.cart_item_id;
  end loop;

  update public.orders o
  set total = (select sum(oi.line_total) from public.order_items oi where oi.order_id = v_order_id)
  where o.id = v_order_id
  returning o.total into v_total;

  -- 8. Take the stock and record why (NFR-DI-07) ------------------------------
  -- The CHECK (stock >= 0) on the tables is a second safety net (NFR-DI-02).
  with needed as (
    select i.base_chip_id as item_id, sum(i.quantity)::integer as amount
    from public.cart_items i
    where i.cart_id = v_cart_id
    group by i.base_chip_id
  ),
  taken as (
    update public.base_chips b
    set stock = b.stock - n.amount
    from needed n
    where b.id = n.item_id
    returning b.id, n.amount
  )
  insert into public.stock_history (item_type, item_id, change, reason, order_id, changed_by)
  select 'base', t.id, -t.amount, 'Order ' || v_order_number, v_order_id, v_user_id
  from taken t;

  with needed as (
    select f.flavor_id as item_id, sum(i.quantity)::integer as amount
    from public.cart_item_flavors f
    join public.cart_items i on i.id = f.cart_item_id
    where i.cart_id = v_cart_id
    group by f.flavor_id
  ),
  taken as (
    update public.flavors fl
    set stock = fl.stock - n.amount
    from needed n
    where fl.id = n.item_id
    returning fl.id, n.amount
  )
  insert into public.stock_history (item_type, item_id, change, reason, order_id, changed_by)
  select 'flavor', t.id, -t.amount, 'Order ' || v_order_number, v_order_id, v_user_id
  from taken t;

  -- 9. Empty the cart (US-402 AC3). Deleting the lines also deletes their flavors.
  delete from public.cart_items i where i.cart_id = v_cart_id;

  return query select v_order_id, v_order_number, v_total, false;
end;
$$;

-- Only signed-in users may call it; guests must sign in first (Q5).
revoke execute on function public.place_order(text, text, uuid) from public, anon;
grant execute on function public.place_order(text, text, uuid) to authenticated;
