-- Dermalens Database Setup Script
-- Run this in your Supabase SQL Editor

-- Add missing columns to the profiles table
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS email TEXT,
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS last_name TEXT;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);

-- Create the user_skin_profiles table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.user_skin_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    skin_type TEXT,
    skin_tone TEXT,
    acne_severity TEXT,
    pore_size TEXT,
    sensitivity_level TEXT,
    primary_concerns TEXT[] DEFAULT '{}',
    pre_existing_conditions TEXT[] DEFAULT '{}',
    allergies TEXT[] DEFAULT '{}',
    preferred_brands TEXT[] DEFAULT '{}',
    medical_conditions TEXT[] DEFAULT '{}',
    diet_type TEXT,
    water_intake TEXT,
    sleep_hours TEXT,
    sun_exposure TEXT,
    routine_frequency TEXT,
    routine_type TEXT,
    skin_goals TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create the user_images table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.user_images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    bucket TEXT DEFAULT 'user-images',
    analysis_results JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for the new tables
CREATE INDEX IF NOT EXISTS idx_user_skin_profiles_user_id ON public.user_skin_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_images_user_id ON public.user_images(user_id);

-- Enable Row Level Security (RLS) on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_skin_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_images ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for profiles table
CREATE POLICY IF NOT EXISTS "Users can view own profile" 
    ON public.profiles FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY IF NOT EXISTS "Users can update own profile" 
    ON public.profiles FOR UPDATE 
    USING (auth.uid() = id);

CREATE POLICY IF NOT EXISTS "Users can insert own profile" 
    ON public.profiles FOR INSERT 
    WITH CHECK (auth.uid() = id);

-- Create RLS policies for user_skin_profiles table
CREATE POLICY IF NOT EXISTS "Users can view own skin profile" 
    ON public.user_skin_profiles FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can update own skin profile" 
    ON public.user_skin_profiles FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert own skin profile" 
    ON public.user_skin_profiles FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for user_images table
CREATE POLICY IF NOT EXISTS "Users can view own images" 
    ON public.user_images FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert own images" 
    ON public.user_images FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can delete own images" 
    ON public.user_images FOR DELETE 
    USING (auth.uid() = user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON public.profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_skin_profiles_updated_at 
    BEFORE UPDATE ON public.user_skin_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON public.profiles TO anon, authenticated;
GRANT ALL ON public.user_skin_profiles TO anon, authenticated;
GRANT ALL ON public.user_images TO anon, authenticated;

-- Insert a test profile to verify the setup (optional)
-- INSERT INTO public.profiles (id, email, username, first_name, last_name) 
-- VALUES (gen_random_uuid(), 'test@example.com', 'testuser', 'Test', 'User')
-- ON CONFLICT (id) DO NOTHING;

COMMIT;
