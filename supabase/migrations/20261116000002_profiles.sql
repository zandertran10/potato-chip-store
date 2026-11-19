-- 02. Profiles: one row per signed-up user, holding their display name and role.
-- Requirements: doc 00 section 6, NFR-SEC-01, NFR-SEC-05, NFR-PRIV-01, US-501 AC4.

create table public.profiles (
  -- Same id as the Supabase Auth user. Deleting the auth user deletes the profile.
  id              uuid primary key references auth.users (id) on delete cascade,
  display_name    text not null check (char_length(display_name) between 1 and 50),
  -- Copied from auth.users at sign-up. Staff need it for orders (US-704 AC2) and
  -- the owner finds users by email (US-705 AC1); auth.users is not readable from the app.
  email           text not null check (char_length(email) between 3 and 254),
  role            text not null default 'customer'
                    check (role in ('customer', 'staff', 'owner')),
  default_address text check (char_length(default_address) <= 300),
  created_at      timestamptz not null default now()
);

-- RLS on in the same migration that creates the table (NFR-SEC-02).
-- With no policies yet, nobody can read or write anything: the safe default.
alter table public.profiles enable row level security;

-- Lets the owner find a user by email quickly (US-705).
create index profiles_email_idx on public.profiles (lower(email));

-- Creates the profile automatically for every new user.
-- The role is ALWAYS 'customer': whatever the sign-up form sends is ignored (US-501 AC4).
-- security definer: it runs as the table owner, because the new user has no
-- insert rights on profiles.
create or replace function private.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id, display_name, email, role)
  values (
    new.id,
    -- Use the name from the register form; fall back to the start of the email.
    left(coalesce(nullif(trim(new.raw_user_meta_data ->> 'display_name'), ''),
                  split_part(new.email, '@', 1)), 50),
    new.email,
    'customer'
  );
  return new;
end;
$$;

revoke execute on function private.handle_new_user() from public, anon, authenticated;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function private.handle_new_user();
