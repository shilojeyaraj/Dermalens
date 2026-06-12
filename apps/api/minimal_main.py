"""
Minimal Dermalens API - No external dependencies
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Dermalens Skin Analysis API",
    version="2.0.0-minimal",
    description="Minimal version with no external dependencies",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dermalens API is running!",
        "version": "2.0.0-minimal",
        "timestamp": datetime.now().isoformat(),
        "status": "ready",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-minimal",
        "services": {
            "api": "available",
            "database": "not_configured",
            "ai_services": "not_configured",
        },
    }


@app.post("/analyze-skin")
async def analyze_skin_mock(file: UploadFile = File(...)):
    """
    Mock skin analysis endpoint - returns sample data
    """
    try:
        # Read file content
        content = await file.read()

        # Mock analysis results
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
            "note": "This is a mock analysis. Configure AI services for real analysis.",
        }

        return result

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "basic_analysis": "available",
            "advanced_ai": "not_configured",
            "database": "not_configured",
        },
    }


@app.get("/config")
async def get_config():
    """Get current configuration status"""
    return {
        "vertex_ai": "not_configured",
        "database": "not_configured",
        "elasticsearch": "not_configured",
        "redis": "not_configured",
        "features": {
            "basic_analysis": True,
            "advanced_ai": False,
            "caching": False,
            "monitoring": False,
        },
    }


if __name__ == "__main__":
    print("🚀 Starting Dermalens API (Minimal Version)")
    print("   ✅ Basic endpoints available")
    print("   ⚠️  AI services not configured")
    print("   ⚠️  Database not configured")
    print("   📝 Ready for development and testing")
    print("   🌐 API will be available at: http://localhost:8000")
    print("   📖 API docs at: http://localhost:8000/docs")

    uvicorn.run("minimal_main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
