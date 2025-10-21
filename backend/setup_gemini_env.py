#!/usr/bin/env python3
"""
Setup script to configure Gemini API for Dermalens
Run this script to set up your environment variables
"""
import os
import sys

def setup_gemini_environment():
    """Set up Gemini environment variables"""
    print("🚀 Setting up Google Gemini for Dermalens...")
    
    # Get Gemini API key from user
    gemini_key = input("Enter your Gemini API key: ").strip()
    
    if not gemini_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    # Create .env file with Gemini configuration
    env_content = f"""# Google Gemini Configuration
GEMINI_API_KEY={gemini_key}
GEMINI_MODEL=gemini-1.5-pro
GEMINI_ENABLED=true

# OpenAI Configuration (fallback - disabled)
OPENAI_API_KEY=
OPENAI_ENABLED=false

# Other existing environment variables
DATABASE_URL=your-database-url
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
GOOGLE_API_KEY=your-google-search-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment configured successfully!")
    print("📝 Created .env file with Gemini configuration")
    print("🔧 You can now run: python main.py")
    
    return True

def test_gemini_connection():
    """Test Gemini API connection"""
    print("\n🧪 Testing Gemini connection...")
    
    try:
        from gemini_analysis_service import get_gemini_service
        
        # Test with a simple prompt
        gemini_service = get_gemini_service(os.getenv("GEMINI_API_KEY"))
        
        # Test text generation
        test_result = gemini_service.generate_personalized_report(
            user_profile={"skin_type": "oily", "concerns": ["acne"]},
            analysis_results=[],
            detected_conditions=["acne"]
        )
        
        if test_result["success"]:
            print("✅ Gemini connection successful!")
            print("🎯 Ready to analyze skin images")
            return True
        else:
            print(f"❌ Gemini test failed: {test_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔬 Dermalens Gemini Setup")
    print("=" * 50)
    
    # Setup environment
    if setup_gemini_environment():
        # Test connection
        test_gemini_connection()
    
    print("\n🎉 Setup complete!")
    print("📚 Next steps:")
    print("1. Run: python main.py")
    print("2. Test skin analysis endpoint")
    print("3. Check /api/services-status")
