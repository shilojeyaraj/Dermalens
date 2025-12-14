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
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Google Custom Search API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
GOOGLE_SEARCH_ENABLED = os.getenv("GOOGLE_SEARCH_ENABLED", "True").lower() == "true"

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")  # gemini-1.5-pro has vision capabilities
GEMINI_ENABLED = os.getenv("GEMINI_ENABLED", "True").lower() == "true"

# Vertex AI Configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
VERTEX_AI_ENABLED = os.getenv("VERTEX_AI_ENABLED", "True").lower() == "true"
VERTEX_AI_ENDPOINT = os.getenv("VERTEX_AI_ENDPOINT", f"projects/{GOOGLE_CLOUD_PROJECT}/locations/{GOOGLE_CLOUD_REGION}/endpoints/skin-analysis")
VERTEX_AI_CACHE_ENABLED = os.getenv("VERTEX_AI_CACHE_ENABLED", "True").lower() == "true"
VERTEX_AI_STREAMING_ENABLED = os.getenv("VERTEX_AI_STREAMING_ENABLED", "True").lower() == "true"

# Multi-Model Configuration
ENSEMBLE_ENABLED = os.getenv("ENSEMBLE_ENABLED", "True").lower() == "true"
MODEL_ENSEMBLE_WEIGHTS = {
    "condition_classifier": float(os.getenv("CONDITION_CLASSIFIER_WEIGHT", "0.4")),
    "severity_analyzer": float(os.getenv("SEVERITY_ANALYZER_WEIGHT", "0.3")),
    "skin_type_detector": float(os.getenv("SKIN_TYPE_DETECTOR_WEIGHT", "0.3"))
}

# Performance Monitoring
PERFORMANCE_MONITORING_ENABLED = os.getenv("PERFORMANCE_MONITORING_ENABLED", "True").lower() == "true"
METRICS_ENDPOINT = os.getenv("METRICS_ENDPOINT", f"projects/{GOOGLE_CLOUD_PROJECT}/locations/{GOOGLE_CLOUD_REGION}/endpoints/metrics")
# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://dermalens-frontend-941238576063.us-central1.run.app").split(",")

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/skin_classifier.pth")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# External API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_WEB_SEARCH_API_KEY = os.getenv("GOOGLE_WEB_SEARCH_API_KEY", "")

# Elasticsearch Configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY", "")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
ELASTICSEARCH_SSL_VERIFY = os.getenv("ELASTICSEARCH_SSL_VERIFY", "false").lower() == "true"

# OpenAI Configuration (keeping for fallback)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "False").lower() == "true"

# Google Custom Search API Configuration
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
