-- 11. Admin database functions: set_stock, cancel_order, set_role.
-- The RLS rules (migration 09) stop staff changing stock, cancelling orders or
-- changing roles directly, so these functions are the ONLY way to do it. Each
-- one checks the caller's role itself and runs as one transaction.
-- Requirements: NFR-SEC-05, NFR-SEC-07, NFR-DI-07, US-703, US-704, US-705.
--
-- Errors start with a code the app can check:
--   NOT_ALLOWED, NOT_FOUND, BAD_INPUT, ALREADY_CANCELLED, ALREADY_SHIPPED


-- set_stock: staff set the stock of a chip or flavor; the change is logged ------
create or replace function public.set_stock(
  p_item_type text,
  p_item_id   uuid,
  p_new_stock integer,
  p_reason    text
)
returns integer
language plpgsql
security definer
set search_path = ''
set lock_timeout = '5s'
as $$
declare
  v_old_stock integer;
begin
  if not (select private.is_staff()) then
    raise exception 'NOT_ALLOWED: Only store staff can change stock.';
  end if;
  if p_new_stock is null or p_new_stock < 0 then
    raise exception 'BAD_INPUT: Stock must be a whole number of 0 or more.';
  end if;
  if coalesce(trim(p_reason), '') = '' then
    raise exception 'BAD_INPUT: Please give a reason for the stock change.';
  end if;

  -- FOR UPDATE: if a checkout is using this row right now, wait for it.
  if p_item_type = 'base' then
    select stock into v_old_stock from public.base_chips where id = p_item_id for update;
  elsif p_item_type = 'flavor' then
    select stock into v_old_stock from public.flavors where id = p_item_id for update;
  else
    raise exception 'BAD_INPUT: item_type must be base or flavor.';
  end if;

  if v_old_stock is null then
    raise exception 'NOT_FOUND: That item does not exist.';
  end if;

  if p_new_stock = v_old_stock then
    return v_old_stock;  -- nothing changed, nothing to log
  end if;

  if p_item_type = 'base' then
    update public.base_chips set stock = p_new_stock where id = p_item_id;
  else
    update public.flavors set stock = p_new_stock where id = p_item_id;
  end if;

  insert into public.stock_history (item_type, item_id, change, reason, changed_by)
  values (p_item_type, p_item_id, p_new_stock - v_old_stock, trim(p_reason), (select auth.uid()));

  return p_new_stock;
end;
$$;

revoke execute on function public.set_stock(text, uuid, integer, text) from public, anon;
grant execute on function public.set_stock(text, uuid, integer, text) to authenticated;


-- cancel_order: staff cancel an order and every bag's stock goes back -----------
create or replace function public.cancel_order(p_order_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
set lock_timeout = '5s'
as $$
declare
  v_status       text;
  v_order_number text;
begin
  if not (select private.is_staff()) then
    raise exception 'NOT_ALLOWED: Only store staff can cancel orders.';
  end if;

  select o.status, o.order_number into v_status, v_order_number
  from public.orders o
  where o.id = p_order_id
  for update;

  if v_status is null then
    raise exception 'NOT_FOUND: That order does not exist.';
  elsif v_status = 'cancelled' then
    raise exception 'ALREADY_CANCELLED: This order is already cancelled.';
  elsif v_status = 'shipped' then
    raise exception 'ALREADY_SHIPPED: A shipped order can no longer be cancelled.';
  end if;

  -- Put the base chips back.
  with returned as (
    select oi.base_chip_id as item_id, sum(oi.quantity)::integer as amount
    from public.order_items oi
    where oi.order_id = p_order_id
    group by oi.base_chip_id
  ),
  updated as (
    update public.base_chips b
    set stock = b.stock + r.amount
    from returned r
    where b.id = r.item_id
    returning b.id, r.amount
  )
  insert into public.stock_history (item_type, item_id, change, reason, order_id, changed_by)
  select 'base', u.id, u.amount, 'Cancelled order ' || v_order_number, p_order_id, (select auth.uid())
  from updated u;

  -- Put the flavors back (one unit per bag).
  with returned as (
    select oif.flavor_id as item_id, sum(oi.quantity)::integer as amount
    from public.order_item_flavors oif
    join public.order_items oi on oi.id = oif.order_item_id
    where oi.order_id = p_order_id
    group by oif.flavor_id
  ),
  updated as (
    update public.flavors f
    set stock = f.stock + r.amount
    from returned r
    where f.id = r.item_id
    returning f.id, r.amount
  )
  insert into public.stock_history (item_type, item_id, change, reason, order_id, changed_by)
  select 'flavor', u.id, u.amount, 'Cancelled order ' || v_order_number, p_order_id, (select auth.uid())
  from updated u;

  update public.orders set status = 'cancelled' where id = p_order_id;
end;
$$;

revoke execute on function public.cancel_order(uuid) from public, anon;
grant execute on function public.cancel_order(uuid) to authenticated;


-- set_role: the owner makes a user customer or staff ----------------------------
create or replace function public.set_role(p_user_id uuid, p_role text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if not (select private.is_owner()) then
    raise exception 'NOT_ALLOWED: Only the store owner can change roles.';
  end if;
  -- Nobody changes their own role (NFR-SEC-05, US-705 AC3).
  if p_user_id = (select auth.uid()) then
    raise exception 'NOT_ALLOWED: You can''t change your own role.';
  end if;
  -- The owner hands out customer or staff only (US-705 AC1).
  if p_role not in ('customer', 'staff') then
    raise exception 'BAD_INPUT: The role must be customer or staff.';
  end if;

  update public.profiles set role = p_role where id = p_user_id;
  if not found then
    raise exception 'NOT_FOUND: That user does not exist.';
  end if;
end;
$$;

revoke execute on function public.set_role(uuid, text) from public, anon;
grant execute on function public.set_role(uuid, text) to authenticated;
