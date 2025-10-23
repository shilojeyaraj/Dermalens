# Supabase Authentication Debug Guide

## 🔴 Errors Found:

### Error 1: "Email logins are disabled"
**Location:** Line 390  
**Message:** `Email logins are disabled`

### Error 2: "Database error creating new user"
**Location:** Lines 393-396  
**Message:** `Database error creating new user`

---

## 🔧 Fix Steps

### Step 1: Enable Email Authentication in Supabase

1. **Go to:** https://supabase.com/dashboard
2. **Select your project:** ezlevlxkxanlceofykrh
3. **Navigate to:** Authentication → Providers
4. **Find "Email"** provider
5. **Enable it:**
   - Toggle "Enable Email provider" to ON
   - **Disable "Confirm email"** (so users don't need email verification)
   - Save changes

### Step 2: Set Up Database Tables

Your Supabase database needs these tables:

#### Table 1: `profiles`
```sql
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    profile_picture TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" 
    ON profiles FOR SELECT 
    USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" 
    ON profiles FOR UPDATE 
    USING (auth.uid() = id);

-- Policy: Users can insert their own profile
CREATE POLICY "Users can insert own profile" 
    ON profiles FOR INSERT 
    WITH CHECK (auth.uid() = id);
```

#### Table 2: `user_images`
```sql
CREATE TABLE IF NOT EXISTS user_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    image_data TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_type TEXT DEFAULT 'face_scan',
    UNIQUE(user_id, image_type)
);

-- Enable Row Level Security
ALTER TABLE user_images ENABLE ROW LEVEL SECURITY;

-- Policy: Users can manage their own images
CREATE POLICY "Users can manage own images" 
    ON user_images FOR ALL 
    USING (auth.uid() = user_id);
```

#### Table 3: `user_skin_profiles`
```sql
CREATE TABLE IF NOT EXISTS user_skin_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    skin_type TEXT,
    skin_concerns TEXT[],
    sensitivities TEXT[],
    current_products TEXT[],
    skin_goals TEXT[],
    age_range TEXT,
    lifestyle_factors TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE user_skin_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can manage their own profile
CREATE POLICY "Users can manage own skin profile" 
    ON user_skin_profiles FOR ALL 
    USING (auth.uid() = user_id);
```

---

## 🚀 Quick Fix Script

Run this in **Supabase SQL Editor:**

```sql
-- 1. Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    profile_picture TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Users can view own profile" 
    ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY IF NOT EXISTS "Users can update own profile" 
    ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY IF NOT EXISTS "Users can insert own profile" 
    ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- 2. Create user_images table
CREATE TABLE IF NOT EXISTS user_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    image_data TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_type TEXT DEFAULT 'face_scan',
    UNIQUE(user_id, image_type)
);

ALTER TABLE user_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Users can manage own images" 
    ON user_images FOR ALL USING (auth.uid() = user_id);

-- 3. Create user_skin_profiles table
CREATE TABLE IF NOT EXISTS user_skin_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    skin_type TEXT,
    skin_concerns TEXT[],
    sensitivities TEXT[],
    current_products TEXT[],
    skin_goals TEXT[],
    age_range TEXT,
    lifestyle_factors TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE user_skin_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Users can manage own skin profile" 
    ON user_skin_profiles FOR ALL USING (auth.uid() = user_id);

-- Success message
SELECT 'Database setup complete! ✅' as message;
```

---

## ✅ Verification Steps

### After Setting Up:

1. **Check Authentication:**
   - Go to: Supabase Dashboard → Authentication → Providers
   - Confirm "Email" is enabled
   - Confirm "Confirm email" is disabled

2. **Check Tables:**
   - Go to: Supabase Dashboard → Table Editor
   - Verify tables exist:
     - ✅ profiles
     - ✅ user_images
     - ✅ user_skin_profiles

3. **Test Sign Up:**
   - Try signing up again from your app
   - Should work now! ✅

---

## 🐛 Additional Debugging

If it still fails, check backend logs for:

```python
# Add this to apps/api/core/auth.py in sign_up method:
import traceback

try:
    # ... existing code ...
except Exception as e:
    print(f"[DEBUG] Full error: {traceback.format_exc()}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
```

---

## 📋 Summary

**Issue:** Supabase not configured for authentication
**Root Causes:**
1. Email auth disabled
2. Database tables missing

**Solution:**
1. Enable email auth in Supabase dashboard
2. Run SQL script to create tables
3. Test sign up again

**Expected Result:** User creation succeeds! ✅

