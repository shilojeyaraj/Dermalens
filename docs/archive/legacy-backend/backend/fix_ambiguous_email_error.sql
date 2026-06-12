-- =============================================================================
-- FIX: Ambiguous Column Reference "email" Error
-- =============================================================================
-- 
-- This script fixes the PostgreSQL error:
--   Error code: 42702
--   Message: column reference "email" is ambiguous
-- 
-- The issue occurs because both the 'users' and 'profiles' tables have an
-- 'email' column, and if column references are not properly qualified with
-- table aliases, PostgreSQL cannot determine which table's column to use.
-- 
-- This fix updates the authenticate_user_with_rls function to ensure all
-- column references are properly qualified with table aliases.
-- 
-- =============================================================================

-- Fix the authenticate_user_with_rls function with properly qualified column references
CREATE OR REPLACE FUNCTION authenticate_user_with_rls(
  user_email TEXT,
  user_password TEXT
)
RETURNS TABLE(
  user_id UUID,
  email TEXT,
  username TEXT,
  profile_picture TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
  user_record RECORD;
  profile_record RECORD;
  normalized_email TEXT;
BEGIN
  -- Normalize email (trim and lowercase)
  normalized_email := LOWER(TRIM(user_email));
  
  -- Validate inputs
  IF normalized_email = '' OR user_password = '' THEN
    RAISE EXCEPTION 'Email and password are required';
  END IF;
  
  -- Find user by email (properly qualified with table alias)
  SELECT u.id, u.email, u.password_hash, u.is_active
  INTO user_record
  FROM users u
  WHERE u.email = normalized_email AND u.is_active = true;
  
  -- Check if user exists and password is correct
  IF user_record.id IS NULL OR NOT verify_password(user_password, user_record.password_hash) THEN
    RAISE EXCEPTION 'Invalid email or password';
  END IF;
  
  -- Update last sign in
  UPDATE users 
  SET last_sign_in = NOW(), updated_at = NOW()
  WHERE id = user_record.id;
  
  -- Set user context for RLS
  PERFORM set_user_context(user_record.id);
  
  -- Get user profile (properly qualified with table alias)
  SELECT p.user_id, p.email, p.username, p.profile_picture, p.created_at, p.updated_at
  INTO profile_record
  FROM profiles p
  WHERE p.user_id = user_record.id;
  
  -- Return user data (using record fields, which are already qualified)
  RETURN QUERY SELECT
    user_record.id,
    user_record.email,
    COALESCE(profile_record.username, ''),
    COALESCE(profile_record.profile_picture, ''),
    COALESCE(profile_record.created_at, NOW()),
    COALESCE(profile_record.updated_at, NOW());
    
  -- Clear user context
  PERFORM clear_user_context();
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION authenticate_user_with_rls TO anon, authenticated;

-- Success message
DO $$
BEGIN
  RAISE NOTICE '✅ Fixed authenticate_user_with_rls function - all column references now properly qualified';
  RAISE NOTICE '🔧 This should resolve the "column reference email is ambiguous" error';
END $$;

