-- 13. Audit log: who changed what in the store, and when.
-- Requirements: NFR-LOG-02 (order placed or cancelled, role changed, catalog
-- and settings changes), NFR-LOG-03 (no emails, addresses or passwords).
--
-- Rows are written ONLY by database triggers, so every change is recorded
-- whether it comes from the app, a database function or the Supabase
-- dashboard. Nobody can add, edit or delete rows from the app. Only the
-- owner can read them (Store Admin > Dashboard > Activity).
-- Stock changes are already recorded in stock_history, so they're left out here.

create table public.audit_log (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  -- Who did it. Null when the change was made directly in the Supabase dashboard.
  actor_id    uuid references public.profiles (id) on delete set null,
  actor_name  text,
  actor_role  text,
  action      text not null check (action in ('insert', 'update', 'delete')),
  table_name  text not null,
  record_id   text,
  -- One readable line, e.g.  Hid flavor "Truffle Herb"
  summary     text not null check (char_length(summary) between 1 and 300),
  -- What changed: {"column": {"from": ..., "to": ...}}. Personal columns are left out.
  changes     jsonb not null default '{}'
);

alter table public.audit_log enable row level security;

create index audit_log_created_at_idx on public.audit_log (created_at desc);
create index audit_log_actor_id_idx on public.audit_log (actor_id);

create policy "Owner reads the audit log"
  on public.audit_log for select to authenticated
  -- Only the store owner sees who changed what.
  using ((select private.is_owner()));

-- No insert/update/delete for anyone using the app: only the trigger writes.
revoke insert, update, delete on public.audit_log from anon, authenticated;


-- The trigger function ------------------------------------------------------
-- security definer: it writes to audit_log, which nobody else may write to.
create or replace function private.write_audit()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_old       jsonb := case when tg_op in ('UPDATE', 'DELETE') then to_jsonb(old) end;
  v_new       jsonb := case when tg_op in ('INSERT', 'UPDATE') then to_jsonb(new) end;
  v_row       jsonb := coalesce(v_new, v_old);
  v_actor     uuid := (select auth.uid());
  v_name      text;
  v_role      text;
  v_changes   jsonb := '{}';
  v_label     text;
  v_thing     text;
  v_summary   text;
begin
  -- What changed, column by column. Bookkeeping, stock (in stock_history) and
  -- personal details (NFR-LOG-03) are never copied into the log.
  if tg_op = 'UPDATE' then
    select coalesce(jsonb_object_agg(n.key, jsonb_build_object('from', v_old -> n.key, 'to', n.value)), '{}')
      into v_changes
    from jsonb_each(v_new) n
    where n.value is distinct from v_old -> n.key
      and n.key not in ('updated_at', 'stock', 'email', 'default_address',
                        'delivery_name', 'delivery_address', 'display_name');
    if v_changes = '{}' then
      return null;  -- nothing worth recording (e.g. only stock changed during an order)
    end if;
  end if;

  select p.display_name, p.role into v_name, v_role
  from public.profiles p where p.id = v_actor;

  v_thing := case tg_table_name
    when 'base_chips' then 'chip' when 'flavors' then 'flavor' when 'staff_picks' then 'staff pick'
    else tg_table_name end;
  v_label := coalesce(v_row ->> 'name', v_row ->> 'order_number', v_row ->> 'title', '');

  -- One readable line per change.
  v_summary := case
    when tg_table_name = 'orders' and tg_op = 'INSERT' then
      format('Order %s placed', v_label)
    when tg_table_name = 'orders' then
      format('Order %s: %s → %s', v_label, v_old ->> 'status', v_new ->> 'status')
    when tg_table_name = 'profiles' then
      format('Role of %s: %s → %s', coalesce(v_new ->> 'display_name', 'a user'), v_old ->> 'role', v_new ->> 'role')
    when tg_table_name = 'settings' then
      'Changed store settings'
    when tg_op = 'UPDATE' and v_changes ? 'is_active' then
      format('%s %s "%s"', case when (v_new ->> 'is_active')::boolean then 'Showed' else 'Hid' end, v_thing, v_label)
    when tg_op = 'INSERT' then format('Added %s "%s"', v_thing, v_label)
    when tg_op = 'DELETE' then format('Removed %s "%s"', v_thing, v_label)
    else format('Changed %s "%s"', v_thing, v_label)
  end;

  insert into public.audit_log (actor_id, actor_name, actor_role, action, table_name, record_id, summary, changes)
  values (v_actor, coalesce(v_name, 'Supabase dashboard'), v_role, lower(tg_op), tg_table_name,
          coalesce(v_row ->> 'id', ''), left(v_summary, 300), v_changes);
  return null;  -- AFTER trigger: the return value is ignored
end;
$$;

revoke execute on function private.write_audit() from public, anon, authenticated;


-- Which changes are recorded ---------------------------------------------------
create trigger audit_base_chips
  after insert or update or delete on public.base_chips
  for each row execute function private.write_audit();

create trigger audit_flavors
  after insert or update or delete on public.flavors
  for each row execute function private.write_audit();

create trigger audit_staff_picks
  after insert or update or delete on public.staff_picks
  for each row execute function private.write_audit();

create trigger audit_settings
  after update on public.settings
  for each row execute function private.write_audit();

-- Orders: placed, and every status change (packed, shipped, cancelled).
create trigger audit_orders_placed
  after insert on public.orders
  for each row execute function private.write_audit();

create trigger audit_orders_status
  after update of status on public.orders
  for each row execute function private.write_audit();

-- Roles only: a customer editing their own name or address isn't recorded.
create trigger audit_profile_roles
  after update of role on public.profiles
  for each row execute function private.write_audit();
