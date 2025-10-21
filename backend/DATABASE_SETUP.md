# Database Setup Guide

## Option 1: Manual Setup (Recommended)

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your project** (ezlevlxkxanlceofykrh)
3. **Go to SQL Editor**
4. **Copy and paste the contents of `setup_database.sql`**
5. **Click "Run"**

## Option 2: Python Script Setup

1. **Make sure you're in the backend directory**:
   ```bash
   cd backend
   ```

2. **Run the setup script**:
   ```bash
   python setup_database.py
   ```

## What This Setup Does

### 1. **Adds Missing Columns to `profiles` Table**
- `email` (TEXT) - User's email address
- `first_name` (TEXT) - User's first name
- `last_name` (TEXT) - User's last name

### 2. **Creates `user_skin_profiles` Table**
- Stores detailed skin profile information
- Includes all the fields from your skin profile form
- Links to users via `user_id`

### 3. **Creates `user_images` Table**
- Stores uploaded face scan images
- Links to users via `user_id`
- Includes analysis results

### 4. **Adds Security (RLS)**
- Row Level Security policies
- Users can only access their own data
- Protects against unauthorized access

### 5. **Adds Performance Features**
- Database indexes for faster queries
- Automatic timestamp updates
- Proper foreign key relationships

## After Setup

Once you've run the setup, your signup process should work correctly! The backend will be able to:

1. ✅ Create users in Supabase Auth
2. ✅ Insert user profiles with email addresses
3. ✅ Store skin profile data
4. ✅ Handle face scan images
5. ✅ Maintain data security

## Troubleshooting

If you encounter any issues:

1. **Check Supabase Auth Settings**:
   - Go to Authentication → Settings
   - Make sure "Enable email signup" is enabled
   - You can disable "Enable email confirmations" for testing

2. **Verify Table Structure**:
   - Go to Table Editor
   - Check that all tables exist with the correct columns

3. **Test the API**:
   - Try the signup endpoint again
   - Check the backend logs for detailed error messages

## Next Steps

After running the setup:
1. Restart your backend server
2. Test the signup process
3. Try the complete user flow (signup → profile → face scan)

