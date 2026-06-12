-- Clear test data from Dermalens database
-- Run this in Supabase SQL Editor if you want to start fresh

-- Delete from profiles table (this will cascade to other tables due to foreign keys)
DELETE FROM public.profiles WHERE email = 'shilojeyaraj@gmail.com' OR email = 'shilojeyarajj@gmail.com';

-- Delete from auth.users (this will also clean up the auth system)
-- Note: You might need to do this from the Supabase Auth dashboard instead
-- DELETE FROM auth.users WHERE email = 'shilojeyaraj@gmail.com' OR email = 'shilojeyarajj@gmail.com';

-- Check what's left in the profiles table
SELECT * FROM public.profiles;
