# Fix for Ambiguous Email Column Error

## Problem
When trying to log in, you're getting this PostgreSQL error:
```
Error code: 42702
Message: column reference "email" is ambiguous
Details: It could refer to either a PL/pgSQL variable or a table column.
```

## Root Cause
Both the `users` and `profiles` tables have an `email` column. In the `authenticate_user_with_rls` function, the SELECT statement that queries the `users` table didn't use table aliases, which caused PostgreSQL to be unable to determine which table's `email` column to use when evaluating the query.

## Solution
The fix ensures all column references in SQL queries are properly qualified with table aliases. This removes any ambiguity about which table's column is being referenced.

## How to Deploy the Fix

### Option 1: Quick Fix (Recommended for Production)
Run this SQL script directly in your Supabase SQL Editor:

```sql
-- File: backend/fix_ambiguous_email_error.sql
```

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `backend/fix_ambiguous_email_error.sql`
4. Run the script

### Option 2: Full Setup
If you want to update the complete auth setup (for future deployments):

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `backend/complete_auth_setup.sql`
4. Run the script (it will replace all functions with the fixed versions)

## What Changed

In the `authenticate_user_with_rls` function:
- **Before:** `SELECT id, email, password_hash, is_active FROM users WHERE email = ...`
- **After:** `SELECT u.id, u.email, u.password_hash, u.is_active FROM users u WHERE u.email = ...`

This change ensures PostgreSQL knows exactly which table's columns you're referencing.

## Verification

After running the fix, try logging in again. The error should be resolved.

If you still encounter issues, check:
1. That the function was updated successfully (you can verify in Supabase SQL Editor by viewing the function definition)
2. That you're using the correct function name (`authenticate_user_with_rls`)
3. That your frontend/backend code is calling the function correctly

## Files Changed
- `backend/complete_auth_setup.sql` - Updated with properly qualified column references
- `backend/fix_ambiguous_email_error.sql` - Standalone fix script for production deployment
- `backend/FIX_AMBIGUOUS_EMAIL_INSTRUCTIONS.md` - This file


