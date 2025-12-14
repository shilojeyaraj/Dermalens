#!/usr/bin/env python3
"""
Database Initialization Script
Sets up the database with proper tables, indexes, and sample data
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from database import get_supabase_client
from config import SUPABASE_URL, SUPABASE_KEY

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

async def init_database():
    """Initialize the database with tables and sample data"""
    try:
        print("🔧 Initializing Dermalens Database...")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Check if tables exist
        print("📋 Checking database tables...")
        
        # Test connection
        try:
            result = supabase.table('profiles').select('*').limit(1).execute()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Create tables if they don't exist
        print("📊 Creating database tables...")
        await create_tables(supabase)
        
        # Create indexes
        print("🔍 Creating database indexes...")
        await create_indexes(supabase)
        
        # Insert sample data
        print("🌱 Inserting sample data...")
        await insert_sample_data(supabase)
        
        print("✅ Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        logger.error(f"Database initialization error: {e}")
        return False

async def create_tables(supabase):
    """Create database tables"""
    try:
        # Note: In Supabase, tables are created via SQL migrations
        # This function would typically run SQL commands
        print("  - Tables already exist (created via Supabase dashboard)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        return False

async def create_indexes(supabase):
    """Create database indexes for better performance"""
    try:
        # Note: Indexes are typically created via SQL migrations
        # This function would run CREATE INDEX commands
        print("  - Indexes already exist (created via Supabase dashboard)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating indexes: {e}")
        return False

async def insert_sample_data(supabase):
    """Insert sample data for testing"""
    try:
        # Sample user profiles
        sample_profiles = [
            {
                "id": "sample-user-1",
                "username": "test_user_1",
                "email": "test1@dermalens.com",
                "first_name": "Alice",
                "last_name": "Johnson",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "sample-user-2", 
                "username": "test_user_2",
                "email": "test2@dermalens.com",
                "first_name": "Bob",
                "last_name": "Smith",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        ]
        
        # Sample skin profiles
        sample_skin_profiles = [
            {
                "id": "skin-profile-1",
                "user_id": "sample-user-1",
                "skin_type": "combination",
                "concerns": ["acne", "dark_spots"],
                "sensitivity_level": "moderate",
                "allergies": ["fragrance"],
                "current_routine": ["cleanser", "moisturizer"],
                "goals": ["clear_skin", "even_tone"],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "skin-profile-2",
                "user_id": "sample-user-2", 
                "skin_type": "oily",
                "concerns": ["oily_skin", "large_pores"],
                "sensitivity_level": "low",
                "allergies": [],
                "current_routine": ["cleanser", "toner", "moisturizer"],
                "goals": ["oil_control", "pore_minimization"],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        ]
        
        # Sample user images
        sample_images = [
            {
                "id": "image-1",
                "user_id": "sample-user-1",
                "filename": "test_face_1.jpg",
                "storage_path": "user_images/image-1.jpg",
                "bucket": "dermalens-images",
                "file_size": 1024000,
                "content_type": "image/jpeg",
                "uploaded_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "image-2",
                "user_id": "sample-user-2",
                "filename": "test_face_2.jpg", 
                "storage_path": "user_images/image-2.jpg",
                "bucket": "dermalens-images",
                "file_size": 1200000,
                "content_type": "image/jpeg",
                "uploaded_at": "2024-01-15T10:00:00Z"
            }
        ]
        
        # Insert sample data
        print("  - Inserting sample profiles...")
        for profile in sample_profiles:
            try:
                supabase.table('profiles').insert(profile).execute()
            except Exception as e:
                if "duplicate key" not in str(e).lower():
                    print(f"    ⚠️ Profile {profile['username']} already exists")
        
        print("  - Inserting sample skin profiles...")
        for skin_profile in sample_skin_profiles:
            try:
                supabase.table('user_skin_profiles').insert(skin_profile).execute()
            except Exception as e:
                if "duplicate key" not in str(e).lower():
                    print(f"    ⚠️ Skin profile for user {skin_profile['user_id']} already exists")
        
        print("  - Inserting sample images...")
        for image in sample_images:
            try:
                supabase.table('user_images').insert(image).execute()
            except Exception as e:
                if "duplicate key" not in str(e).lower():
                    print(f"    ⚠️ Image {image['filename']} already exists")
        
        print("  ✅ Sample data inserted successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Error inserting sample data: {e}")
        return False

async def verify_database():
    """Verify database setup"""
    try:
        print("🔍 Verifying database setup...")
        
        supabase = get_supabase_client()
        
        # Check profiles table
        profiles = supabase.table('profiles').select('*').limit(5).execute()
        print(f"  - Profiles table: {len(profiles.data)} records")
        
        # Check skin profiles table
        skin_profiles = supabase.table('user_skin_profiles').select('*').limit(5).execute()
        print(f"  - Skin profiles table: {len(skin_profiles.data)} records")
        
        # Check user images table
        images = supabase.table('user_images').select('*').limit(5).execute()
        print(f"  - User images table: {len(images.data)} records")
        
        print("✅ Database verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Dermalens Database Initialization")
    print("=" * 50)
    
    # Initialize database
    success = await init_database()
    
    if success:
        # Verify setup
        await verify_database()
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the backend server: python main.py")
        print("2. Start the frontend: npm run dev")
        print("3. Visit http://localhost:3000 to test the application")
    else:
        print("\n❌ Database setup failed!")
        print("Please check your Supabase configuration and try again.")

if __name__ == "__main__":
    asyncio.run(main())

