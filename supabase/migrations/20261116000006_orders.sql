-- 06. Orders. Rows are created only by the place_order function (Prompt C).
-- Names and prices are copied in at purchase time, so later price changes
-- never change an old order (NFR-DI-05).
-- Requirements: doc 00 section 6, BR-06 to BR-08, US-402 to US-404, NFR-DI-04.

create table public.orders (
  id               uuid primary key default gen_random_uuid(),
  -- Readable number like CHIP-20261116-0001 (BR-08).
  order_number     text not null unique check (order_number ~ '^CHIP-[0-9]{8}-[0-9]{4}$'),
  -- set null, not cascade: if a customer account is deleted, the order is kept (NFR-PRIV-08).
  user_id          uuid references public.profiles (id) on delete set null,
  status           text not null default 'placed'
                     check (status in ('placed', 'packed', 'shipped', 'cancelled')),
  delivery_name    text not null check (char_length(delivery_name) between 1 and 100),
  delivery_address text not null check (char_length(delivery_address) between 1 and 300),
  -- numeric(8,2) for totals: a big order can go past the 9,999.99 limit of numeric(6,2).
  total            numeric(8,2) not null check (total >= 0),
  -- One key per checkout attempt. Pressing "Place order" twice sends the same key,
  -- and the unique constraint stops a second order (NFR-DI-04).
  idempotency_key  uuid not null unique,
  created_at       timestamptz not null default now()
);

alter table public.orders enable row level security;

-- "My orders" lists a customer's orders newest first (US-504).
create index orders_user_id_created_at_idx on public.orders (user_id, created_at desc);
-- Staff filter orders by status and date (US-704).
create index orders_status_created_at_idx on public.orders (status, created_at desc);


create table public.order_items (
  id           uuid primary key default gen_random_uuid(),
  order_id     uuid not null references public.orders (id) on delete cascade,
  -- restrict: a chip in an order can never be deleted, only hidden (BR-10).
  base_chip_id uuid not null references public.base_chips (id) on delete restrict,
  base_name    text not null,
  base_price   numeric(6,2) not null check (base_price > 0),
  -- Price of one bag: base price plus each flavor's price (BR-02).
  unit_price   numeric(6,2) not null check (unit_price > 0),
  quantity     integer not null check (quantity between 1 and 99),
  line_total   numeric(8,2) not null check (line_total >= 0)
);

alter table public.order_items enable row level security;

create index order_items_order_id_idx on public.order_items (order_id);
create index order_items_base_chip_id_idx on public.order_items (base_chip_id);


create table public.order_item_flavors (
  order_item_id uuid not null references public.order_items (id) on delete cascade,
  flavor_id     uuid not null references public.flavors (id) on delete restrict,
  flavor_name   text not null,
  flavor_price  numeric(6,2) not null check (flavor_price > 0),
  primary key (order_item_id, flavor_id)
);

alter table public.order_item_flavors enable row level security;

-- Used by the flavor passport (US-603) and the "top flavors" chart (US-707).
create index order_item_flavors_flavor_id_idx on public.order_item_flavors (flavor_id);
