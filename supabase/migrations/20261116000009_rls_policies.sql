-- 09. Row Level Security policies: who can see and change what.
-- Requirements: NFR-SEC-03 to NFR-SEC-07.
--
-- Roles:
--   guest    = not signed in        -> Supabase role "anon"
--   customer = signed in            -> Supabase role "authenticated", profiles.role = 'customer'
--   staff    = store employee       -> "authenticated", profiles.role = 'staff'
--   owner    = store owner          -> "authenticated", profiles.role = 'owner'
--
-- Policies only ever ADD access. Anything not allowed below is blocked.
-- Writes to orders, order lines and stock_history happen only through the
-- database functions in Prompt C (NFR-SEC-07), so there are no insert policies for them.
-- auth.uid() is wrapped in (select ...) so Postgres works it out once per query,
-- not once per row.


-- ---------------------------------------------------------------------------
-- Role helpers
-- ---------------------------------------------------------------------------

-- security definer: reads profiles as the table owner, so the policies on
-- profiles don't have to check themselves (which would loop forever).
create or replace function private.is_staff()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.profiles
    where id = (select auth.uid()) and role in ('staff', 'owner')
  );
$$;

create or replace function private.is_owner()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.profiles
    where id = (select auth.uid()) and role = 'owner'
  );
$$;

-- Signed-in users need these to evaluate the policies. They only ever answer
-- about the caller, so there is nothing to leak.
revoke execute on function private.is_staff(), private.is_owner() from public, anon;
grant usage on schema private to authenticated;
grant execute on function private.is_staff(), private.is_owner() to authenticated;


-- ---------------------------------------------------------------------------
-- profiles
-- ---------------------------------------------------------------------------

create policy "Users can read their own profile"
  on public.profiles for select to authenticated
  -- Each user can see their own name, email, address and role.
  using (id = (select auth.uid()));

create policy "Staff can read all profiles"
  on public.profiles for select to authenticated
  -- Staff need customer names and emails on orders, and the owner finds users by email.
  using ((select private.is_staff()));

create policy "Users can update their own profile"
  on public.profiles for update to authenticated
  -- Users can edit their own profile only; the column grants below stop them changing their role.
  using (id = (select auth.uid()))
  with check (id = (select auth.uid()));

-- Nobody can change their own role (NFR-SEC-05): users may only update these two
-- columns. Roles change only through the owner-only set_role function (Prompt C).
revoke update on public.profiles from anon, authenticated;
grant update (display_name, default_address) on public.profiles to authenticated;


-- ---------------------------------------------------------------------------
-- base_chips and flavors
-- ---------------------------------------------------------------------------

create policy "Anyone can read active chips"
  on public.base_chips for select to anon, authenticated
  -- Guests and customers can browse the shop, but hidden chips stay hidden.
  using (is_active);

create policy "Staff can read all chips"
  on public.base_chips for select to authenticated
  -- Staff also see hidden chips so they can edit or show them again.
  using ((select private.is_staff()));

create policy "Staff can add chips"
  on public.base_chips for insert to authenticated
  -- Only staff and the owner manage the catalog.
  with check ((select private.is_staff()));

create policy "Staff can edit chips"
  on public.base_chips for update to authenticated
  -- Only staff and the owner edit chips; there is no delete policy because chips are hidden, never deleted (BR-10).
  using ((select private.is_staff()))
  with check ((select private.is_staff()));

-- Stock changes go through set_stock so every change is recorded (NFR-DI-07),
-- so staff may edit every column except stock.
revoke update on public.base_chips from anon, authenticated;
grant update (name, description, style, thickness, crunch_level, allergens, price,
              image_path, image_alt, is_featured, is_active)
  on public.base_chips to authenticated;


create policy "Anyone can read active flavors"
  on public.flavors for select to anon, authenticated
  -- Guests and customers see every flavor that is on sale.
  using (is_active);

create policy "Staff can read all flavors"
  on public.flavors for select to authenticated
  -- Staff also see hidden flavors so they can edit or show them again.
  using ((select private.is_staff()));

create policy "Staff can add flavors"
  on public.flavors for insert to authenticated
  -- Only staff and the owner manage the catalog.
  with check ((select private.is_staff()));

create policy "Staff can edit flavors"
  on public.flavors for update to authenticated
  -- Only staff and the owner edit flavors; there is no delete policy because flavors are hidden, never deleted (BR-10).
  using ((select private.is_staff()))
  with check ((select private.is_staff()));

revoke update on public.flavors from anon, authenticated;
grant update (name, description, family, salty, tangy, sweet, heat, allergens, price,
              icon, is_active)
  on public.flavors to authenticated;


-- ---------------------------------------------------------------------------
-- staff_picks and staff_pick_flavors
-- ---------------------------------------------------------------------------

create policy "Anyone can read staff picks for active chips"
  on public.staff_picks for select to anon, authenticated
  -- Shoppers see suggestions only for chips that are on sale.
  using (exists (
    select 1 from public.base_chips c
    where c.id = staff_picks.base_chip_id and c.is_active
  ));

create policy "Staff can manage staff picks"
  on public.staff_picks for all to authenticated
  -- Staff create, edit and remove picks (picks are suggestions, so deleting is fine).
  using ((select private.is_staff()))
  with check ((select private.is_staff()));

create policy "Anyone can read staff pick flavors"
  on public.staff_pick_flavors for select to anon, authenticated
  -- The flavors in a pick are public; the pick itself is already filtered above.
  using (true);

create policy "Staff can manage staff pick flavors"
  on public.staff_pick_flavors for all to authenticated
  -- Staff choose which flavors belong to a pick.
  using ((select private.is_staff()))
  with check ((select private.is_staff()));


-- ---------------------------------------------------------------------------
-- carts, cart_items, cart_item_flavors (customers only see their own)
-- ---------------------------------------------------------------------------

create policy "Customers manage their own cart"
  on public.carts for all to authenticated
  -- A customer can only create, read, change or empty their own cart (NFR-SEC-03).
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

create policy "Customers manage lines in their own cart"
  on public.cart_items for all to authenticated
  -- Cart lines belong to whoever owns the cart, so access follows the cart.
  using (exists (
    select 1 from public.carts c
    where c.id = cart_items.cart_id and c.user_id = (select auth.uid())
  ))
  with check (exists (
    select 1 from public.carts c
    where c.id = cart_items.cart_id and c.user_id = (select auth.uid())
  ));

create policy "Customers manage flavors in their own cart lines"
  on public.cart_item_flavors for all to authenticated
  -- The flavors in a cart line belong to whoever owns the cart.
  using (exists (
    select 1 from public.cart_items i
    join public.carts c on c.id = i.cart_id
    where i.id = cart_item_flavors.cart_item_id and c.user_id = (select auth.uid())
  ))
  with check (exists (
    select 1 from public.cart_items i
    join public.carts c on c.id = i.cart_id
    where i.id = cart_item_flavors.cart_item_id and c.user_id = (select auth.uid())
  ));


-- ---------------------------------------------------------------------------
-- orders, order_items, order_item_flavors
-- ---------------------------------------------------------------------------

create policy "Customers read their own orders"
  on public.orders for select to authenticated
  -- A customer sees only their own orders, even if they change the order number in the link (US-403 AC4).
  using (user_id = (select auth.uid()));

create policy "Staff read all orders"
  on public.orders for select to authenticated
  -- Staff see every order so they can pack and ship it (US-704).
  using ((select private.is_staff()));

create policy "Staff move orders to packed or shipped"
  on public.orders for update to authenticated
  -- Staff update the status, but cannot set "cancelled" here: cancelling must go through cancel_order so stock is put back (US-704 AC4).
  using ((select private.is_staff()))
  with check ((select private.is_staff()) and status in ('placed', 'packed', 'shipped'));

-- Staff may change the status only, never the total, address or owner of an order.
revoke update on public.orders from anon, authenticated;
grant update (status) on public.orders to authenticated;

create policy "Order lines follow their order"
  on public.order_items for select to authenticated
  -- Anyone who can see the order (its customer or staff) can see its lines.
  using (exists (
    select 1 from public.orders o
    where o.id = order_items.order_id
      and (o.user_id = (select auth.uid()) or (select private.is_staff()))
  ));

create policy "Order line flavors follow their order"
  on public.order_item_flavors for select to authenticated
  -- Anyone who can see the order can see the flavors in it (also feeds the flavor passport).
  using (exists (
    select 1 from public.order_items i
    join public.orders o on o.id = i.order_id
    where i.id = order_item_flavors.order_item_id
      and (o.user_id = (select auth.uid()) or (select private.is_staff()))
  ));


-- ---------------------------------------------------------------------------
-- stock_history and settings
-- ---------------------------------------------------------------------------

create policy "Staff read stock history"
  on public.stock_history for select to authenticated
  -- Only staff and the owner see who changed stock; rows are written by functions only.
  using ((select private.is_staff()));

create policy "Anyone can read store settings"
  on public.settings for select to anon, authenticated
  -- The bag builder needs max_flavors for every shopper, and nothing here is secret.
  using (true);

create policy "Owner can change store settings"
  on public.settings for update to authenticated
  -- Only the owner changes store settings (US-706).
  using ((select private.is_owner()))
  with check ((select private.is_owner()));
