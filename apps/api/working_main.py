"""
Working Main Application for Dermalens
Gracefully handles import failures and provides fallback functionality
"""

import json
import logging
import os

# Import configuration
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config"))

# Try to import config
try:
    from config import (
        ALLOWED_ORIGINS,
        API_HOST,
        API_PORT,
        DEBUG,
        ENSEMBLE_ENABLED,
        PERFORMANCE_MONITORING_ENABLED,
        VERTEX_AI_ENABLED,
        VERTEX_AI_STREAMING_ENABLED,
    )
except:
    # Fallback configuration
    ALLOWED_ORIGINS = ["*"]
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    DEBUG = True
    VERTEX_AI_ENABLED = False
    VERTEX_AI_STREAMING_ENABLED = False
    ENSEMBLE_ENABLED = False
    PERFORMANCE_MONITORING_ENABLED = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import enhanced services (may fail due to numpy issues)
AI_SERVICES_AVAILABLE = False
DATABASE_AVAILABLE = False
AUTH_AVAILABLE = False
SEARCH_AVAILABLE = False

try:
    logger.info("Attempting to import AI services...")
    from ai.ai_recommendation_engine import ai_recommendation_engine
    from ai.enhanced_comprehensive_analysis_service import enhanced_comprehensive_analysis_service
    from ai.vertex_ai_service import vertex_ai_service
    from infrastructure.caching import intelligent_caching_service
    from monitoring.performance import performance_monitoring_service

    AI_SERVICES_AVAILABLE = True
    logger.info("✅ AI services imported successfully")
except Exception as e:
    logger.warning(f"⚠️  AI services not available: {e}")
    logger.warning("   Running in basic mode without AI features")

try:
    logger.info("Attempting to import database services...")
    from database.connection import (
        SkinProfileCreate,
        SkinProfileUpdate,
        UserImageCreate,
        UserProfileCreate,
        UserProfileUpdate,
        db_manager,
    )

    DATABASE_AVAILABLE = True
    logger.info("✅ Database services imported successfully")
except Exception as e:
    logger.warning(f"⚠️  Database services not available: {e}")

try:
    logger.info("Attempting to import auth services...")
    from core.auth import (
        PasswordResetRequest,
        SignInRequest,
        SignUpRequest,
        TokenResponse,
        auth_manager,
        get_current_user,
        get_current_user_id,
    )

    AUTH_AVAILABLE = True
    logger.info("✅ Auth services imported successfully")
except Exception as e:
    logger.warning(f"⚠️  Auth services not available: {e}")

try:
    logger.info("Attempting to import search services...")
    from infrastructure.elasticsearch_service import elasticsearch_service
    from infrastructure.google_search_service import google_search_service

    SEARCH_AVAILABLE = True
    logger.info("✅ Search services imported successfully")
except Exception as e:
    logger.warning(f"⚠️  Search services not available: {e}")

# Create FastAPI application
app = FastAPI(
    title="Dermalens Skin Analysis API",
    version="2.0.0-adaptive",
    description="Adaptive API that works with or without AI services",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Add explicit OPTIONS handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "OK"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dermalens API is running!",
        "version": "2.0.0-adaptive",
        "timestamp": datetime.now().isoformat(),
        "status": "ready",
    }


@app.get("/health")
async def health_check():
    """Health check with service availability status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-adaptive",
        "services": {
            "api": "available",
            "ai_services": "available" if AI_SERVICES_AVAILABLE else "unavailable",
            "database": "available" if DATABASE_AVAILABLE else "unavailable",
            "auth": "available" if AUTH_AVAILABLE else "unavailable",
            "search": "available" if SEARCH_AVAILABLE else "unavailable",
        },
        "features": {
            "vertex_ai": VERTEX_AI_ENABLED and AI_SERVICES_AVAILABLE,
            "streaming": VERTEX_AI_STREAMING_ENABLED and AI_SERVICES_AVAILABLE,
            "ensemble": ENSEMBLE_ENABLED and AI_SERVICES_AVAILABLE,
            "monitoring": PERFORMANCE_MONITORING_ENABLED and AI_SERVICES_AVAILABLE,
        },
    }


@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "ai_available": AI_SERVICES_AVAILABLE,
        "database_available": DATABASE_AVAILABLE,
    }


@app.post("/analyze-skin")
async def analyze_skin(file: UploadFile = File(...)):
    """
    Skin analysis endpoint - uses AI if available, otherwise returns mock data
    """
    try:
        # Read file content
        content = await file.read()

        if AI_SERVICES_AVAILABLE:
            # Use real AI analysis
            logger.info("Using AI services for analysis")
            # TODO: Call actual AI service
            result = {
                "success": True,
                "analysis_type": "ai_powered",
                "note": "AI services are available but not fully configured",
            }
        else:
            # Return mock data
            logger.info("AI services not available, returning mock data")
            result = {
                "success": True,
                "analysis_results": [
                    {
                        "face_id": 0,
                        "conditions": ["acne", "hyperpigmentation"],
                        "skin_type": {"primary": "combination", "confidence": 0.8},
                        "health_score": 75,
                        "recommendations": [
                            "Use gentle cleanser",
                            "Apply sunscreen daily",
                            "Consider vitamin C serum",
                        ],
                    }
                ],
                "detected_conditions": ["acne", "hyperpigmentation"],
                "faces_detected": 1,
                "overall_health_score": 75,
                "analysis_type": "mock",
                "timestamp": datetime.now().isoformat(),
                "note": "This is mock data. AI services are not available.",
            }

        return result

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Dermalens API (Adaptive Mode)")
    print(f"   AI Services: {'✅ Available' if AI_SERVICES_AVAILABLE else '⚠️  Not Available'}")
    print(f"   Database: {'✅ Available' if DATABASE_AVAILABLE else '⚠️  Not Available'}")
    print(f"   Auth: {'✅ Available' if AUTH_AVAILABLE else '⚠️  Not Available'}")
    print(f"   Search: {'✅ Available' if SEARCH_AVAILABLE else '⚠️  Not Available'}")
    print("   🌐 API will be available at: http://localhost:8000")
    print("   📖 API docs at: http://localhost:8000/docs")

    uvicorn.run("working_main:app", host=API_HOST, port=API_PORT, reload=True, log_level="info")
