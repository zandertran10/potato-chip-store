-- 10. Storage bucket for chip and flavor images.
-- Requirements: doc 00 section 6 (storage), US-701 AC3, NFR-SEC-16.

-- Public bucket: anyone can view images by URL, which the shop needs.
-- The size limit (2 MB) and the allowed types are enforced by Supabase itself,
-- not just by the upload form.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('product-images', 'product-images', true, 2097152,
        array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do nothing;

create policy "Staff upload product images"
  on storage.objects for insert to authenticated
  -- Only staff and the owner can add images, and only to this bucket.
  with check (bucket_id = 'product-images' and (select private.is_staff()));

create policy "Staff replace product images"
  on storage.objects for update to authenticated
  -- Only staff and the owner can replace an image in this bucket.
  using (bucket_id = 'product-images' and (select private.is_staff()))
  with check (bucket_id = 'product-images' and (select private.is_staff()));

create policy "Staff remove product images"
  on storage.objects for delete to authenticated
  -- Only staff and the owner can remove an image from this bucket.
  using (bucket_id = 'product-images' and (select private.is_staff()));
