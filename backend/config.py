"""
Configuration settings for Dermalens Backend
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = "https://ezlevlxkxanlceofykrh.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NzYxNTksImV4cCI6MjA3NTM1MjE1OX0.oPovEwcfN-jhHPxFOczj3RkmCX2QZICQYnfmo6hQwhg"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTc3NjE1OSwiZXhwIjoyMDc1MzUyMTU5fQ.SbhkLCmjqUDA1oBWLnXVzOeoiKYriiXe7AZ6L-9C2ag"

# Google Custom Search API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAtT3Jon9cWkbfnNLR91F9J810vvjzu8JY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "96653b7de4a3d49fe")
GOOGLE_SEARCH_ENABLED = os.getenv("GOOGLE_SEARCH_ENABLED", "True").lower() == "true"

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # gpt-4o has vision capabilities
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "False").lower() == "true"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/skin_classifier.pth")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

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

# Google Custom Search Configuration
GOOGLE_SEARCH_MAX_RESULTS = int(os.getenv("GOOGLE_SEARCH_MAX_RESULTS", "10"))
GOOGLE_SEARCH_SAFE_SEARCH = os.getenv("GOOGLE_SEARCH_SAFE_SEARCH", "active")  # off, active, high
GOOGLE_SEARCH_COUNTRY = os.getenv("GOOGLE_SEARCH_COUNTRY", "us")
GOOGLE_SEARCH_LANGUAGE = os.getenv("GOOGLE_SEARCH_LANGUAGE", "en")
