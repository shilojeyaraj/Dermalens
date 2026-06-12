"""
Production Main Application for Dermalens
Handles missing dependencies gracefully and provides full functionality
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import uvicorn
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Dermalens AI Skin Analysis API",
    version="2.0.0",
    description="AI-powered skin analysis with advanced features",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Try to import services with fallbacks
try:
    from ai.vertex_ai_service import vertex_ai_service

    VERTEX_AI_AVAILABLE = True
    logger.info("✅ Vertex AI service loaded")
except Exception as e:
    logger.warning(f"⚠️ Vertex AI service not available: {e}")
    VERTEX_AI_AVAILABLE = False

try:
    from ai.enhanced_skin_analysis_service_simple import enhanced_skin_analysis_service

    SKIN_ANALYSIS_AVAILABLE = True
    logger.info("✅ Enhanced skin analysis service loaded")
except Exception as e:
    logger.warning(f"⚠️ Enhanced skin analysis service not available: {e}")
    SKIN_ANALYSIS_AVAILABLE = False

try:
    from ai.enhanced_product_recommendation_service import enhanced_product_recommendation_service

    PRODUCT_RECOMMENDATION_AVAILABLE = True
    logger.info("✅ Product recommendation service loaded")
except Exception as e:
    logger.warning(f"⚠️ Product recommendation service not available: {e}")
    PRODUCT_RECOMMENDATION_AVAILABLE = False

try:
    from database.connection import db_manager

    DATABASE_AVAILABLE = True
    logger.info("✅ Database service loaded")
except Exception as e:
    logger.warning(f"⚠️ Database service not available: {e}")
    DATABASE_AVAILABLE = False

try:
    from core.auth import auth_manager

    AUTH_AVAILABLE = True
    logger.info("✅ Authentication service loaded")
except Exception as e:
    logger.warning(f"⚠️ Authentication service not available: {e}")
    AUTH_AVAILABLE = False


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Dermalens AI API is running!",
        "version": "2.0.0",
        "status": "healthy",
        "services": {
            "vertex_ai": VERTEX_AI_AVAILABLE,
            "skin_analysis": SKIN_ANALYSIS_AVAILABLE,
            "product_recommendation": PRODUCT_RECOMMENDATION_AVAILABLE,
            "database": DATABASE_AVAILABLE,
            "authentication": AUTH_AVAILABLE,
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is running"}


# Skin analysis endpoint
@app.post("/analyze-skin")
async def analyze_skin(file: UploadFile = File(...)):
    """Analyze skin from uploaded image"""
    try:
        if not SKIN_ANALYSIS_AVAILABLE:
            return JSONResponse(
                status_code=503, content={"error": "Skin analysis service not available"}
            )

        # Read image data
        image_data = await file.read()

        # Perform analysis
        result = await enhanced_skin_analysis_service.analyze_skin_image(image_data)

        return {"success": True, "analysis": result, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        logger.error(f"Skin analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Multi-angle skin analysis
@app.post("/analyze-skin-multi-angle")
async def analyze_skin_multi_angle(
    center_image: UploadFile = File(...),
    left_image: UploadFile = File(...),
    right_image: UploadFile = File(...),
):
    """Analyze skin from multiple angles"""
    try:
        if not SKIN_ANALYSIS_AVAILABLE:
            return JSONResponse(
                status_code=503, content={"error": "Skin analysis service not available"}
            )

        # Read all images
        center_data = await center_image.read()
        left_data = await left_image.read()
        right_data = await right_image.read()

        # Perform multi-angle analysis
        result = await enhanced_skin_analysis_service.analyze_multi_angle_skin(
            center_data, left_data, right_data
        )

        return {"success": True, "analysis": result, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        logger.error(f"Multi-angle analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-angle analysis failed: {str(e)}")


# Product recommendations
@app.post("/recommend-products")
async def recommend_products(
    skin_conditions: List[str] = Form(...),
    skin_type: str = Form(...),
    budget: Optional[float] = Form(None),
):
    """Get product recommendations based on skin analysis"""
    try:
        if not PRODUCT_RECOMMENDATION_AVAILABLE:
            return JSONResponse(
                status_code=503, content={"error": "Product recommendation service not available"}
            )

        # Get recommendations
        recommendations = await enhanced_product_recommendation_service.get_recommendations(
            skin_conditions=skin_conditions, skin_type=skin_type, budget=budget
        )

        return {
            "success": True,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Product recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


# User authentication endpoints
@app.post("/auth/signup")
async def signup(request: dict):
    """User registration"""
    if not AUTH_AVAILABLE:
        return JSONResponse(
            status_code=503, content={"error": "Authentication service not available"}
        )

    try:
        result = await auth_manager.signup(request)
        return result
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@app.post("/auth/signin")
async def signin(request: dict):
    """User login"""
    if not AUTH_AVAILABLE:
        return JSONResponse(
            status_code=503, content={"error": "Authentication service not available"}
        )

    try:
        result = await auth_manager.signin(request)
        return result
    except Exception as e:
        logger.error(f"Signin error: {e}")
        raise HTTPException(status_code=500, detail=f"Signin failed: {str(e)}")


# User profile endpoints
@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    if not DATABASE_AVAILABLE:
        return JSONResponse(status_code=503, content={"error": "Database service not available"})

    try:
        profile = await db_manager.get_user_profile(user_id)
        return profile
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@app.post("/profile")
async def create_profile(profile_data: dict):
    """Create user profile"""
    if not DATABASE_AVAILABLE:
        return JSONResponse(status_code=503, content={"error": "Database service not available"})

    try:
        result = await db_manager.create_user_profile(profile_data)
        return result
    except Exception as e:
        logger.error(f"Create profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")


# Fallback endpoints for missing services
@app.get("/services/status")
async def services_status():
    """Get status of all services"""
    return {
        "vertex_ai": VERTEX_AI_AVAILABLE,
        "skin_analysis": SKIN_ANALYSIS_AVAILABLE,
        "product_recommendation": PRODUCT_RECOMMENDATION_AVAILABLE,
        "database": DATABASE_AVAILABLE,
        "authentication": AUTH_AVAILABLE,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
