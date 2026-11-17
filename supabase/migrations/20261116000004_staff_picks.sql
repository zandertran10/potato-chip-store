-- 04. Staff picks: suggested flavor combinations for a base chip.
-- Requirements: doc 00 section 6, US-601, US-702 AC3.

create table public.staff_picks (
  id           uuid primary key default gen_random_uuid(),
  base_chip_id uuid not null references public.base_chips (id) on delete cascade,
  title        text not null check (char_length(title) between 1 and 60),
  -- Up to 3 picks per chip: positions 1-3, and each position used once (below).
  position     smallint not null check (position between 1 and 3),
  constraint staff_picks_one_per_position unique (base_chip_id, position)
);

alter table public.staff_picks enable row level security;
-- No extra index on base_chip_id: the unique constraint above already starts with it.


create table public.staff_pick_flavors (
  staff_pick_id uuid not null references public.staff_picks (id) on delete cascade,
  -- restrict: a flavor used in a pick cannot be deleted (flavors are hidden instead).
  flavor_id     uuid not null references public.flavors (id) on delete restrict,
  primary key (staff_pick_id, flavor_id)
);

alter table public.staff_pick_flavors enable row level security;

-- Foreign keys are not indexed automatically in Postgres.
create index staff_pick_flavors_flavor_id_idx on public.staff_pick_flavors (flavor_id);
