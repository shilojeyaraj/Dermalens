"""
Simplified Dermalens API - Works with basic configuration
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Dict, Any
from datetime import datetime

# Import basic services (without advanced AI)
try:
    # Try to import from the new structure
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'config'))
    
    from database.connection import db_manager
    from core.auth import auth_manager
    from infrastructure.elasticsearch_service import elasticsearch_service
    from infrastructure.google_search_service import google_search_service
    print("✅ Basic services imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Fallback to basic functionality
    db_manager = None
    auth_manager = None
    elasticsearch_service = None
    google_search_service = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Dermalens Skin Analysis API",
    version="2.0.0-simplified",
    description="Simplified version with basic features"
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
        "version": "2.0.0-simplified",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-simplified",
        "services": {
            "database": "available" if db_manager else "unavailable",
            "elasticsearch": "available" if elasticsearch_service else "unavailable",
            "google_search": "available" if google_search_service else "unavailable"
        }
    }

@app.post("/analyze-skin")
async def analyze_skin_basic(
    file: UploadFile = File(...)
):
    """
    Basic skin analysis endpoint
    """
    try:
        # Read file content
        content = await file.read()
        
        # Basic analysis (mock for now)
        result = {
            "success": True,
            "analysis_results": [{
                "face_id": 0,
                "conditions": ["acne", "hyperpigmentation"],
                "skin_type": {"primary": "combination", "confidence": 0.8},
                "health_score": 75
            }],
            "detected_conditions": ["acne", "hyperpigmentation"],
            "faces_detected": 1,
            "overall_health_score": 75,
            "analysis_type": "basic",
            "timestamp": datetime.now().isoformat()
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
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Dermalens API (Simplified Version)")
    print("   - Basic features enabled")
    print("   - Advanced AI features disabled")
    print("   - Ready for development and testing")
    
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
