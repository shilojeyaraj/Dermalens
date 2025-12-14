"""
Debug version of main.py to find the issue
"""
print("🔍 Step 1: Starting imports...")

try:
    print("   - Importing FastAPI...")
    from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.gzip import GZipMiddleware
    import uvicorn
    import asyncio
    import time
    import logging
    from typing import List, Dict, Any, Optional
    from datetime import datetime
    import json
    print("   ✅ Basic imports successful")
    
    print("   - Importing configuration...")
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'config'))
    from config import (
        ALLOWED_ORIGINS, API_HOST, API_PORT, DEBUG, 
        VERTEX_AI_ENABLED, VERTEX_AI_STREAMING_ENABLED, ENSEMBLE_ENABLED,
        PERFORMANCE_MONITORING_ENABLED
    )
    print("   ✅ Configuration imported")
    
    print("   - Importing AI services...")
    from ai.vertex_ai_service import vertex_ai_service
    print("   ✅ Vertex AI service imported")
    
    from ai.enhanced_comprehensive_analysis_service import enhanced_comprehensive_analysis_service
    print("   ✅ Enhanced analysis service imported")
    
    from infrastructure.caching import intelligent_caching_service
    print("   ✅ Caching service imported")
    
    from ai.ai_recommendation_engine import ai_recommendation_engine
    print("   ✅ Recommendation engine imported")
    
    from monitoring.performance import performance_monitoring_service
    print("   ✅ Performance monitoring imported")
    
    print("   - Importing database services...")
    from database.connection import db_manager, UserProfileCreate, UserProfileUpdate, SkinProfileCreate, SkinProfileUpdate, UserImageCreate
    print("   ✅ Database service imported")
    
    print("   - Importing auth services...")
    from core.auth import auth_manager, get_current_user, get_current_user_id, SignUpRequest, SignInRequest, PasswordResetRequest, TokenResponse
    print("   ✅ Auth service imported")
    
    print("   - Importing infrastructure services...")
    from infrastructure.elasticsearch_service import elasticsearch_service
    from infrastructure.google_search_service import google_search_service
    print("   ✅ Infrastructure services imported")
    
    print("\n🎉 All imports successful!")
    print("\n🔍 Step 2: Creating FastAPI app...")
    
    app = FastAPI(
        title="Dermalens Enhanced Skin Analysis API",
        version="2.0.0-debug",
        description="Debug version"
    )
    print("   ✅ FastAPI app created")
    
    print("\n🔍 Step 3: Adding middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    print("   ✅ Middleware added")
    
    print("\n🔍 Step 4: Creating basic routes...")
    
    @app.get("/")
    async def root():
        return {"message": "Dermalens API is running!", "version": "2.0.0-debug"}
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-debug"
        }
    
    print("   ✅ Routes created")
    
    print("\n✅ All setup complete!")
    print("🚀 Starting server...")
    
    if __name__ == "__main__":
        uvicorn.run(
            "debug_main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

