-- 05. Saved carts for signed-in customers. Guest carts live in the Streamlit session.
-- Requirements: doc 00 section 6, US-301 to US-305.

create table public.carts (
  id         uuid primary key default gen_random_uuid(),
  -- unique: one saved cart per customer. The unique constraint also indexes user_id.
  user_id    uuid not null unique references public.profiles (id) on delete cascade,
  updated_at timestamptz not null default now()
);

alter table public.carts enable row level security;

create trigger carts_set_updated_at
  before update on public.carts
  for each row execute function private.set_updated_at();


-- One line = one bag design (a base chip plus its flavors) with a quantity.
create table public.cart_items (
  id           uuid primary key default gen_random_uuid(),
  cart_id      uuid not null references public.carts (id) on delete cascade,
  base_chip_id uuid not null references public.base_chips (id) on delete restrict,
  quantity     integer not null check (quantity between 1 and 99),
  created_at   timestamptz not null default now()
);

alter table public.cart_items enable row level security;

create index cart_items_cart_id_idx on public.cart_items (cart_id);
create index cart_items_base_chip_id_idx on public.cart_items (base_chip_id);


-- The flavors in a cart line. "1 to 3 flavors" (BR-01) depends on the max_flavors
-- setting, so it is checked in place_order and the app, not with a constraint here.
create table public.cart_item_flavors (
  cart_item_id uuid not null references public.cart_items (id) on delete cascade,
  flavor_id    uuid not null references public.flavors (id) on delete restrict,
  primary key (cart_item_id, flavor_id)
);

alter table public.cart_item_flavors enable row level security;

create index cart_item_flavors_flavor_id_idx on public.cart_item_flavors (flavor_id);
