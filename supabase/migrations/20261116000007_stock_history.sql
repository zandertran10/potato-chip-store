-- 07. Stock history: who changed stock, when, by how much and why.
-- Written only by database functions (place_order, cancel_order, set_stock in Prompt C).
-- Requirements: doc 00 section 6, US-703 AC4, NFR-DI-07.

create table public.stock_history (
  id         uuid primary key default gen_random_uuid(),
  -- item_id points at base_chips or flavors depending on item_type, so it can't
  -- have a normal foreign key. The functions that write here check it instead.
  item_type  text not null check (item_type in ('base', 'flavor')),
  item_id    uuid not null,
  -- Positive = restock or cancelled order, negative = sold. Zero is never a change.
  change     integer not null check (change <> 0),
  reason     text not null check (char_length(reason) between 1 and 200),
  order_id   uuid references public.orders (id) on delete set null,
  changed_by uuid references public.profiles (id) on delete set null,
  created_at timestamptz not null default now()
);

alter table public.stock_history enable row level security;

-- The stock history tab shows one item's changes, newest first (S13).
create index stock_history_item_idx on public.stock_history (item_type, item_id, created_at desc);
create index stock_history_order_id_idx on public.stock_history (order_id);
create index stock_history_changed_by_idx on public.stock_history (changed_by);
