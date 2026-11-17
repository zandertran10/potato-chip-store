-- 01. Shared helpers used by the later migrations.
--
-- The "private" schema holds helper functions. Supabase's Data API only
-- exposes the "public" schema, so nothing in here can be called from the app.

create schema if not exists private;

-- Keeps updated_at correct on every UPDATE, so the app never has to set it.
create or replace function private.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Functions are executable by everyone by default; this one is only for triggers.
revoke execute on function private.set_updated_at() from public, anon, authenticated;
