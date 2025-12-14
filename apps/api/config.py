"""
Production-ready configuration for Dermalens Backend
This replaces the problematic settings import system
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ezlevlxkxanlceofykrh.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NzYxNTksImV4cCI6MjA3NTM1MjE1OX0.oPovEwcfN-jhHPxFOczj3RkmCX2QZICQYnfmo6hQwhg")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTc3NjE1OSwiZXhwIjoyMDc1MzUyMTU5fQ.SbhkLCmjqUDA1oBWLnXVzOeoiKYriiXe7AZ6L-9C2ag")

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "dermalens-production")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAtT3Jon9cWkbfnNLR91F9J810vvjzu8JY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "96653b7de4a3d49fe")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCI1YRrJprS3ADJIY1U_deeFiJUTa4T_hk")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dermalens-production-secret-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Elasticsearch Configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "https://126ac4035b474479a8228759b486116b.us-central1.gcp.cloud.es.io:443")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY", "")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "your_password_here")
ELASTICSEARCH_SSL_VERIFY = os.getenv("ELASTICSEARCH_SSL_VERIFY", "true").lower() == "true"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("PORT", 8080))  # Default to 8080 for Cloud Run
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://dermalens-frontend-941238576063.us-central1.run.app").split(",")

# Feature Flags
VERTEX_AI_ENABLED = os.getenv("VERTEX_AI_ENABLED", "True").lower() == "true"
VERTEX_AI_STREAMING_ENABLED = os.getenv("VERTEX_AI_STREAMING_ENABLED", "True").lower() == "true"
ENSEMBLE_ENABLED = os.getenv("ENSEMBLE_ENABLED", "True").lower() == "true"
PERFORMANCE_MONITORING_ENABLED = os.getenv("PERFORMANCE_MONITORING_ENABLED", "True").lower() == "true"
GOOGLE_SEARCH_ENABLED = os.getenv("GOOGLE_SEARCH_ENABLED", "True").lower() == "true"
GEMINI_ENABLED = os.getenv("GEMINI_ENABLED", "True").lower() == "true"

# Google Search Configuration
GOOGLE_SEARCH_MAX_RESULTS = int(os.getenv("GOOGLE_SEARCH_MAX_RESULTS", "10"))
GOOGLE_SEARCH_SAFE_SEARCH = os.getenv("GOOGLE_SEARCH_SAFE_SEARCH", "active")
GOOGLE_SEARCH_COUNTRY = os.getenv("GOOGLE_SEARCH_COUNTRY", "us")
GOOGLE_SEARCH_LANGUAGE = os.getenv("GOOGLE_SEARCH_LANGUAGE", "en")

# Database Table Names
PROFILES_TABLE = "profiles"
USER_IMAGES_TABLE = "user_images"
USER_SKIN_PROFILES_TABLE = "user_skin_profiles"

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/skin_classifier.pth")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["image/jpeg", "image/jpg", "image/png", "video/mp4"]

# Vertex AI Configuration
VERTEX_AI_ENDPOINT = os.getenv("VERTEX_AI_ENDPOINT", f"projects/{GOOGLE_CLOUD_PROJECT}/locations/{GOOGLE_CLOUD_REGION}/endpoints/skin-analysis")
VERTEX_AI_CACHE_ENABLED = os.getenv("VERTEX_AI_CACHE_ENABLED", "True").lower() == "true"
METRICS_ENDPOINT = os.getenv("METRICS_ENDPOINT", f"projects/{GOOGLE_CLOUD_PROJECT}/locations/{GOOGLE_CLOUD_REGION}/endpoints/metrics")

# Model Ensemble Weights
MODEL_ENSEMBLE_WEIGHTS = {
    "condition_classifier": float(os.getenv("CONDITION_CLASSIFIER_WEIGHT", "0.4")),
    "severity_analyzer": float(os.getenv("SEVERITY_ANALYZER_WEIGHT", "0.3")),
    "skin_type_detector": float(os.getenv("SKIN_TYPE_DETECTOR_WEIGHT", "0.3"))
}

# Gemini Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# OpenAI Configuration (fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "False").lower() == "true"


