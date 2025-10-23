-- ============================================================
-- DERMALENS SUPABASE QUICK FIX
-- Run this in Supabase SQL Editor
-- ============================================================

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

DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;

CREATE POLICY "Users can view own profile" 
    ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" 
    ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" 
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

DROP POLICY IF EXISTS "Users can manage own images" ON user_images;

CREATE POLICY "Users can manage own images" 
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

DROP POLICY IF EXISTS "Users can manage own skin profile" ON user_skin_profiles;

CREATE POLICY "Users can manage own skin profile" 
    ON user_skin_profiles FOR ALL USING (auth.uid() = user_id);

-- Success message
SELECT 'Database setup complete! ✅ Now enable Email auth in Dashboard → Authentication → Providers' as message;

