-- 08. Store settings: a single row the owner can change without code.
-- Requirements: doc 00 section 6, US-706, BR-01.

create table public.settings (
  -- Always 1: the check makes a second settings row impossible.
  id                  smallint primary key default 1 check (id = 1),
  max_flavors         smallint not null default 3 check (max_flavors between 1 and 5),
  low_stock_threshold integer not null default 10 check (low_stock_threshold >= 0),
  -- .test is a reserved domain, so this address can never reach a real inbox.
  from_email          text not null default 'orders@potatochipco.test'
                        check (from_email ~ '^[^@\s]+@[^@\s]+$'),
  updated_at          timestamptz not null default now()
);

alter table public.settings enable row level security;

create trigger settings_set_updated_at
  before update on public.settings
  for each row execute function private.set_updated_at();

-- The single settings row (id 1) is added with the sample data in supabase/seed/.
