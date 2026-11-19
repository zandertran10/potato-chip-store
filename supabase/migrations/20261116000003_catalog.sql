-- 03. Catalog: base chips and flavor add-ons.
-- Requirements: doc 00 section 6, BR-01 to BR-04, BR-10, US-701, US-702, NFR-SEC-13, NFR-PRIV-07.

create table public.base_chips (
  id           uuid primary key default gen_random_uuid(),
  name         text not null unique check (char_length(name) between 1 and 60),
  description  text not null default '' check (char_length(description) <= 500),
  style        text not null check (char_length(style) between 1 and 30),
  thickness    text not null default 'Regular' check (char_length(thickness) between 1 and 30),
  crunch_level smallint not null default 2 check (crunch_level between 0 and 3),
  -- Allergens of the chip itself, combined with the flavors' allergens in US-203.
  -- (Not in the doc 00 table, but NFR-PRIV-07 needs allergens for every chip.)
  allergens    text[] not null default '{}',
  price        numeric(6,2) not null check (price > 0),
  -- Stock can never go below 0, even if the app has a bug (NFR-DI-02).
  stock        integer not null default 0 check (stock >= 0),
  image_path   text,
  image_alt    text check (char_length(image_alt) <= 150),
  is_featured  boolean not null default false,
  -- Chips are hidden, never deleted, so old orders keep working (BR-10).
  is_active    boolean not null default true,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  -- Every image needs alt text for screen readers (doc 02 section 8).
  constraint base_chips_image_needs_alt
    check (image_path is null or char_length(coalesce(image_alt, '')) > 0)
);

alter table public.base_chips enable row level security;

create trigger base_chips_set_updated_at
  before update on public.base_chips
  for each row execute function private.set_updated_at();


create table public.flavors (
  id          uuid primary key default gen_random_uuid(),
  name        text not null unique check (char_length(name) between 1 and 60),
  description text not null default '' check (char_length(description) <= 500),
  -- The five families from doc 01 section 4.
  family      text not null check (family in ('Salty', 'Tangy', 'Spicy', 'Sweet', 'Herby')),
  -- The taste profile: four scores from 0 to 3 (US-202 AC2).
  salty       smallint not null default 0 check (salty between 0 and 3),
  tangy       smallint not null default 0 check (tangy between 0 and 3),
  sweet       smallint not null default 0 check (sweet between 0 and 3),
  heat        smallint not null default 0 check (heat between 0 and 3),
  allergens   text[] not null default '{}',
  price       numeric(6,2) not null check (price > 0),
  stock       integer not null default 0 check (stock >= 0),
  icon        text check (char_length(icon) <= 100),
  is_active   boolean not null default true,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

alter table public.flavors enable row level security;

create trigger flavors_set_updated_at
  before update on public.flavors
  for each row execute function private.set_updated_at();

-- The shop page filters by family (US-104).
create index flavors_family_idx on public.flavors (family);
