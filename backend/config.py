"""
Configuration settings for Dermalens Backend
"""
import os
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file with default encoding: {e}")
    # Try with different encodings
    try:
        load_dotenv(encoding='utf-16')
        print("Successfully loaded .env file with UTF-16 encoding")
    except Exception as e2:
        try:
            load_dotenv(encoding='latin-1')
            print("Successfully loaded .env file with Latin-1 encoding")
        except Exception as e3:
            print(f"Could not load .env file with any encoding. Using default configuration values...")
            print(f"UTF-16 error: {e2}")
            print(f"Latin-1 error: {e3}")

# Supabase Configuration
SUPABASE_URL = "https://ezlevlxkxanlceofykrh.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NzYxNTksImV4cCI6MjA3NTM1MjE1OX0.oPovEwcfN-jhHPxFOczj3RkmCX2QZICQYnfmo6hQwhg"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTc3NjE1OSwiZXhwIjoyMDc1MzUyMTU5fQ.SbhkLCmjqUDA1oBWLnXVzOeoiKYriiXe7AZ6L-9C2ag"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# CORS Configuration
# Allow all origins for development (change for production)
ALLOWED_ORIGINS = ["*"]

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/skin_classifier.pth")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# External API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_WEB_SEARCH_API_KEY = os.getenv("GOOGLE_WEB_SEARCH_API_KEY", "")

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
GEMINI_ENABLED = os.getenv("GEMINI_ENABLED", "True").lower() == "true"

# Elasticsearch Configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY", "")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
ELASTICSEARCH_SSL_VERIFY = os.getenv("ELASTICSEARCH_SSL_VERIFY", "false").lower() == "true"

# OpenAI Configuration (keeping for fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "False").lower() == "true"

# Google Custom Search API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
GOOGLE_SEARCH_ENABLED = os.getenv("GOOGLE_SEARCH_ENABLED", "True").lower() == "true"
GOOGLE_SEARCH_MAX_RESULTS = int(os.getenv("GOOGLE_SEARCH_MAX_RESULTS", "10"))
GOOGLE_SEARCH_SAFE_SEARCH = os.getenv("GOOGLE_SEARCH_SAFE_SEARCH", "active")
GOOGLE_SEARCH_COUNTRY = os.getenv("GOOGLE_SEARCH_COUNTRY", "us")
GOOGLE_SEARCH_LANGUAGE = os.getenv("GOOGLE_SEARCH_LANGUAGE", "en")

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["image/jpeg", "image/jpg", "image/png", "video/mp4"]

# Database Table Names
PROFILES_TABLE = "profiles"
USER_IMAGES_TABLE = "user_images"
USER_SKIN_PROFILES_TABLE = "user_skin_profiles"

# Skin condition types for validation
SKIN_TYPES = ["normal", "dry", "oily", "combination", "sensitive"]
SKIN_TONES = ["fair", "light", "medium", "tan", "dark", "deep"]
ACNE_SEVERITY = ["none", "mild", "moderate", "severe"]
PORE_SIZE = ["small", "medium", "large"]
SENSITIVITY_LEVEL = ["low", "moderate", "high"]
DIET_TYPE = ["omnivore", "vegetarian", "vegan", "pescatarian"]
WATER_INTAKE = ["low", "moderate", "high"]
SLEEP_HOURS = ["<6", "6-8", "8-10", ">10"]
SUN_EXPOSURE = ["minimal", "moderate", "high"]
ROUTINE_FREQUENCY = ["daily", "alternating_days", "weekly"]
ROUTINE_TYPE = ["minimal", "standard", "extensive"]
