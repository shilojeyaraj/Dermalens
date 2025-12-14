-- Fix user_skin_profiles table schema
-- This script ensures the table has all the required columns with proper types

-- Drop and recreate the table with the correct schema
DROP TABLE IF EXISTS user_skin_profiles CASCADE;

-- Create the user_skin_profiles table with all required columns
CREATE TABLE user_skin_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_user_skin_profiles_user_id ON user_skin_profiles(user_id);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_skin_profiles_updated_at 
    BEFORE UPDATE ON user_skin_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE user_skin_profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
DROP POLICY IF EXISTS "Users can view their own skin profile" ON user_skin_profiles;
DROP POLICY IF EXISTS "Users can insert their own skin profile" ON user_skin_profiles;
DROP POLICY IF EXISTS "Users can update their own skin profile" ON user_skin_profiles;

CREATE POLICY "Users can view their own skin profile" ON user_skin_profiles
    FOR SELECT USING (user_id = (SELECT id FROM users WHERE email = current_setting('app.current_user_id', true)));

CREATE POLICY "Users can insert their own skin profile" ON user_skin_profiles
    FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE email = current_setting('app.current_user_id', true)));

CREATE POLICY "Users can update their own skin profile" ON user_skin_profiles
    FOR UPDATE USING (user_id = (SELECT id FROM users WHERE email = current_setting('app.current_user_id', true)));

-- Grant permissions
GRANT ALL ON user_skin_profiles TO anon;
GRANT ALL ON user_skin_profiles TO authenticated;

-- Test the table with sample data
INSERT INTO user_skin_profiles (
    user_id, 
    skin_type, 
    primary_concerns, 
    skin_goals
) VALUES (
    (SELECT id FROM users LIMIT 1),
    'combination',
    ARRAY['acne', 'hyperpigmentation'],
    ARRAY['clear_skin', 'even_tone']
);

-- Verify the table works
SELECT 'user_skin_profiles table created successfully' as status;
