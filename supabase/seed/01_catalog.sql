-- Seed 01: store settings, base chips, flavors and staff picks (doc 01 section 5).
-- Run AFTER all migrations. Safe to run more than once: existing rows are kept.
-- All data is fictional. Fixed ids make the test file and demo links predictable.

-- Store settings: max 3 flavors per bag, low-stock warning at 10 (US-706).
insert into public.settings (id, max_flavors, low_stock_threshold, from_email)
values (1, 3, 10, 'orders@potatochipco.test')
on conflict (id) do nothing;


-- Base chips (4). Sweet Potato has only 3 left, to show the "Few left" badge.
-- Categories for chips are their style: Classic, Kettle, Wavy, Sweet potato.
insert into public.base_chips
  (id, name, description, style, thickness, crunch_level, allergens, price, stock, is_featured)
values
  ('00000000-0000-4000-8000-000000000101', 'Classic Thin',
   'Thin, golden slices of organic potato, cooked in small batches in our kitchen.',
   'Classic', 'Thin', 2, '{}', 2.50, 100, true),
  ('00000000-0000-4000-8000-000000000102', 'Kettle Cooked',
   'Thick-cut organic potatoes, kettle cooked by hand for an extra-loud crunch.',
   'Kettle', 'Thick', 3, '{}', 3.00, 80, true),
  ('00000000-0000-4000-8000-000000000103', 'Wavy Ridge',
   'Ridged slices that hold on to every bit of seasoning.',
   'Wavy', 'Regular', 2, '{}', 2.75, 60, true),
  ('00000000-0000-4000-8000-000000000104', 'Sweet Potato',
   'Organic sweet potato slices with a naturally sweet, earthy taste.',
   'Sweet potato', 'Regular', 1, '{}', 3.25, 3, false)
on conflict (id) do nothing;


-- Flavors (10). Categories are the five flavor families.
-- Truffle Herb has 0 left, to show the "Sold out" state.
-- Profile scores are 0-3: salty, tangy, sweet, heat (US-202).
insert into public.flavors
  (id, name, description, family, salty, tangy, sweet, heat, allergens, price, stock, icon)
values
  ('00000000-0000-4000-8000-000000000201', 'Sea Salt',
   'A simple pinch of flaky sea salt. The classic.',
   'Salty', 3, 0, 0, 0, '{}', 0.25, 200, '🧂'),
  ('00000000-0000-4000-8000-000000000202', 'Salt & Vinegar',
   'Sharp apple-cider vinegar with a salty finish.',
   'Tangy', 2, 3, 0, 0, '{}', 0.50, 150, '🍏'),
  ('00000000-0000-4000-8000-000000000203', 'Sour Cream & Onion',
   'Cool, creamy and full of green onion.',
   'Herby', 1, 1, 0, 0, '{milk}', 0.50, 150, '🧅'),
  ('00000000-0000-4000-8000-000000000204', 'Smoky BBQ',
   'Sweet and smoky, like a backyard barbecue.',
   'Spicy', 1, 1, 2, 1, '{soy}', 0.50, 120, '🔥'),
  ('00000000-0000-4000-8000-000000000205', 'Cheddar Blast',
   'Big, bold aged-cheddar flavor.',
   'Salty', 2, 0, 0, 0, '{milk}', 0.60, 100, '🧀'),
  ('00000000-0000-4000-8000-000000000206', 'Zesty Lime',
   'Bright, fresh lime zest.',
   'Tangy', 1, 3, 0, 0, '{}', 0.40, 90, '🍋'),
  ('00000000-0000-4000-8000-000000000207', 'Chili Kick',
   'A warm kick of red chili. Spicy, but friendly.',
   'Spicy', 1, 0, 0, 3, '{}', 0.60, 70, '🌶️'),
  ('00000000-0000-4000-8000-000000000208', 'Honey Mustard',
   'Golden honey with a little mustard tang.',
   'Sweet', 1, 1, 2, 1, '{mustard}', 0.60, 50, '🍯'),
  ('00000000-0000-4000-8000-000000000209', 'Cinnamon Sugar',
   'A sweet, cozy dusting of cinnamon and sugar.',
   'Sweet', 0, 0, 3, 0, '{}', 0.50, 40, '🍂'),
  ('00000000-0000-4000-8000-000000000210', 'Truffle Herb',
   'Earthy herbs with a hint of mushroom.',
   'Herby', 1, 0, 0, 0, '{milk}', 0.90, 0, '🌿')
on conflict (id) do nothing;


-- Staff picks (3): one suggested combo for three of the chips (US-601).
insert into public.staff_picks (id, base_chip_id, title, position)
values
  ('00000000-0000-4000-8000-000000000301', '00000000-0000-4000-8000-000000000102', 'Tangy Crunch', 1),
  ('00000000-0000-4000-8000-000000000302', '00000000-0000-4000-8000-000000000103', 'BBQ Cheddar Wave', 1),
  ('00000000-0000-4000-8000-000000000303', '00000000-0000-4000-8000-000000000104', 'Sweet Treat', 1)
on conflict (id) do nothing;

insert into public.staff_pick_flavors (staff_pick_id, flavor_id)
values
  -- Kettle Cooked + Salt & Vinegar + Sea Salt
  ('00000000-0000-4000-8000-000000000301', '00000000-0000-4000-8000-000000000202'),
  ('00000000-0000-4000-8000-000000000301', '00000000-0000-4000-8000-000000000201'),
  -- Wavy Ridge + Smoky BBQ + Cheddar Blast
  ('00000000-0000-4000-8000-000000000302', '00000000-0000-4000-8000-000000000204'),
  ('00000000-0000-4000-8000-000000000302', '00000000-0000-4000-8000-000000000205'),
  -- Sweet Potato + Cinnamon Sugar
  ('00000000-0000-4000-8000-000000000303', '00000000-0000-4000-8000-000000000209')
on conflict do nothing;
