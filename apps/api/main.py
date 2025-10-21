"""
Enhanced Main Application for Dermalens
Integrates all advanced AI services including Vertex AI, streaming, ensemble models, and monitoring
"""
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

# Import enhanced services
from vertex_ai_service import vertex_ai_service
from enhanced_comprehensive_analysis_service import enhanced_comprehensive_analysis_service
from intelligent_caching_service import intelligent_caching_service
from ai_recommendation_engine import ai_recommendation_engine
from performance_monitoring_service import performance_monitoring_service

# Import existing services
from database import db_manager, UserProfileCreate, UserProfileUpdate, SkinProfileCreate, SkinProfileUpdate, UserImageCreate
from auth import auth_manager, get_current_user, get_current_user_id, SignUpRequest, SignInRequest, PasswordResetRequest, TokenResponse
from elasticsearch_service import elasticsearch_service
from google_search_service import google_search_service

# Import configuration
from config import (
    ALLOWED_ORIGINS, API_HOST, API_PORT, DEBUG, 
    VERTEX_AI_ENABLED, VERTEX_AI_STREAMING_ENABLED, ENSEMBLE_ENABLED,
    PERFORMANCE_MONITORING_ENABLED
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create enhanced FastAPI application
app = FastAPI(
    title="Dermalens Enhanced Skin Analysis API",
    version="2.0.0",
    description="Advanced AI-powered skin analysis with Vertex AI, streaming, and ensemble models",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add explicit OPTIONS handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "OK"}

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    try:
        # Get service health status
        service_health = await performance_monitoring_service.get_service_health_status()
        
        # Check if all critical services are healthy
        critical_services = ["vertex_ai", "elasticsearch", "caching"]
        healthy_services = [service for service, health in service_health.items() if health.status == "healthy"]
        
        overall_status = "healthy" if all(service in healthy_services for service in critical_services) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-enhanced",
            "services": {
                service: {
                    "status": health.status,
                    "response_time": health.response_time,
                    "last_check": health.last_check.isoformat()
                }
                for service, health in service_health.items()
            },
            "features": {
                "vertex_ai": VERTEX_AI_ENABLED,
                "streaming": VERTEX_AI_STREAMING_ENABLED,
                "ensemble": ENSEMBLE_ENABLED,
                "monitoring": PERFORMANCE_MONITORING_ENABLED
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Enhanced skin analysis endpoint
@app.post("/analyze-skin")
async def analyze_skin_enhanced(
    file: UploadFile = File(...),
    analysis_type: str = "comprehensive",
    current_user_id: str = Depends(get_current_user_id),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Enhanced skin analysis with multiple AI capabilities
    
    Args:
        file: Image or video file to analyze
        analysis_type: Type of analysis (comprehensive, quick, streaming, ensemble)
        current_user_id: Authenticated user ID
        background_tasks: Background tasks for performance tracking
    """
    start_time = time.time()
    analysis_id = f"analysis_{current_user_id}_{int(start_time)}"
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Track performance start
        if PERFORMANCE_MONITORING_ENABLED:
            background_tasks.add_task(
                performance_monitoring_service.track_analysis_performance,
                analysis_id=analysis_id,
                service="enhanced_analysis",
                analysis_type=analysis_type,
                start_time=start_time,
                end_time=time.time(),
                success=True,
                user_id=current_user_id
            )
        
        # Perform enhanced analysis
        if analysis_type == "streaming" and VERTEX_AI_STREAMING_ENABLED:
            # Real-time streaming analysis
            return StreamingResponse(
                _stream_analysis_results(content, current_user_id, analysis_id),
                media_type="application/json"
            )
        else:
            # Standard enhanced analysis
            result = await enhanced_comprehensive_analysis_service.analyze_user_comprehensive(
                user_id=current_user_id,
                analysis_type=analysis_type
            )
            
            # Track performance end
            if PERFORMANCE_MONITORING_ENABLED:
                background_tasks.add_task(
                    performance_monitoring_service.track_analysis_performance,
                    analysis_id=analysis_id,
                    service="enhanced_analysis",
                    analysis_type=analysis_type,
                    start_time=start_time,
                    end_time=time.time(),
                    success=result.get("success", False),
                    user_id=current_user_id
                )
            
            return result
            
    except Exception as e:
        logger.error(f"❌ Enhanced skin analysis failed: {e}")
        
        # Track error
        if PERFORMANCE_MONITORING_ENABLED:
            background_tasks.add_task(
                performance_monitoring_service.track_analysis_performance,
                analysis_id=analysis_id,
                service="enhanced_analysis",
                analysis_type=analysis_type,
                start_time=start_time,
                end_time=time.time(),
                success=False,
                user_id=current_user_id
            )
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def _stream_analysis_results(content: bytes, user_id: str, analysis_id: str):
    """Stream analysis results in real-time"""
    try:
        # Use Vertex AI streaming analysis
        async for result_chunk in vertex_ai_service._stream_predictions([{
            "image": {"b64": content.decode()},
            "user_id": user_id,
            "streaming": True
        }]):
            yield f"data: {json.dumps(result_chunk)}\n\n"
            
    except Exception as e:
        logger.error(f"❌ Streaming analysis failed: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

# Enhanced product search endpoint
@app.post("/search-products")
async def search_products_enhanced(
    request: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Enhanced product search with AI-powered recommendations
    
    Args:
        request: Search request with conditions, preferences, etc.
        current_user_id: Authenticated user ID
        background_tasks: Background tasks for performance tracking
    """
    start_time = time.time()
    
    try:
        # Extract search parameters
        conditions = request.get("conditions", [])
        user_profile = request.get("user_profile", {})
        search_type = request.get("type", "comprehensive")
        
        # Get AI-powered recommendations
        if VERTEX_AI_ENABLED:
            # Use AI recommendation engine
            recommendations = await ai_recommendation_engine.get_ai_recommendations(
                skin_analysis={"detected_conditions": conditions},
                user_profile=user_profile,
                recommendation_type=search_type,
                max_recommendations=request.get("limit", 10)
            )
            
            # Track performance
            if PERFORMANCE_MONITORING_ENABLED:
                background_tasks.add_task(
                    performance_monitoring_service.track_recommendation_performance,
                    recommendation_type=search_type,
                    start_time=start_time,
                    end_time=time.time(),
                    success=recommendations.get("success", False),
                    quality_score=recommendations.get("personalization_score", 0.5),
                    user_id=current_user_id
                )
            
            return recommendations
        else:
            # Fallback to existing search
            result = elasticsearch_service.search_products(
                skin_conditions=conditions,
                user_profile=user_profile,
                limit=request.get("limit", 10)
            )
            
            return {
                "success": result.get("success", False),
                "recommendations": result.get("products", []),
                "source": "elasticsearch_fallback"
            }
            
    except Exception as e:
        logger.error(f"❌ Enhanced product search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Product search failed: {str(e)}")

# Enhanced routine generation endpoint
@app.post("/generate-routine")
async def generate_routine_enhanced(
    request: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Enhanced routine generation with AI optimization
    
    Args:
        request: Routine generation request
        current_user_id: Authenticated user ID
        background_tasks: Background tasks for performance tracking
    """
    start_time = time.time()
    
    try:
        # Extract routine parameters
        skin_analysis = request.get("skin_analysis", {})
        user_profile = request.get("user_profile", {})
        routine_type = request.get("type", "comprehensive")
        
        # Get AI-powered recommendations first
        recommendations = await ai_recommendation_engine.get_ai_recommendations(
            skin_analysis=skin_analysis,
            user_profile=user_profile,
            recommendation_type="routine",
            max_recommendations=20
        )
        
        if not recommendations.get("success", False):
            raise HTTPException(status_code=500, detail="Failed to get product recommendations")
        
        # Generate enhanced routine
        routine = await _generate_enhanced_routine(
            skin_analysis=skin_analysis,
            recommendations=recommendations["recommendations"],
            user_profile=user_profile,
            routine_type=routine_type
        )
        
        # Track performance
        if PERFORMANCE_MONITORING_ENABLED:
            background_tasks.add_task(
                performance_monitoring_service.track_recommendation_performance,
                recommendation_type="routine_generation",
                start_time=start_time,
                end_time=time.time(),
                success=True,
                quality_score=routine.get("personalization_score", 0.5),
                user_id=current_user_id
            )
        
        return {
            "success": True,
            "routine": routine,
            "ai_enhanced": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced routine generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Routine generation failed: {str(e)}")

async def _generate_enhanced_routine(
    skin_analysis: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
    routine_type: str
) -> Dict[str, Any]:
    """Generate enhanced skincare routine using AI"""
    try:
        # Categorize products
        product_categories = {
            "cleansers": [],
            "serums": [],
            "moisturizers": [],
            "sunscreens": [],
            "toners": [],
            "treatments": []
        }
        
        for product in recommendations:
            category = _categorize_product(product)
            if category in product_categories:
                product_categories[category].append(product)
        
        # Generate morning routine
        morning_routine = []
        step = 1
        
        # Cleanser
        if product_categories["cleansers"]:
            morning_routine.append({
                "step": step,
                "action": "Gentle Cleanser",
                "product": product_categories["cleansers"][0],
                "instructions": "Cleanse face with lukewarm water, massage for 60 seconds, rinse thoroughly",
                "duration": "1-2 minutes"
            })
            step += 1
        
        # Toner
        if product_categories["toners"]:
            morning_routine.append({
                "step": step,
                "action": "Toner",
                "product": product_categories["toners"][0],
                "instructions": "Apply with cotton pad or hands, pat gently into skin",
                "duration": "30 seconds"
            })
            step += 1
        
        # Serums (up to 2)
        for serum in product_categories["serums"][:2]:
            morning_routine.append({
                "step": step,
                "action": "Treatment Serum",
                "product": serum,
                "instructions": "Apply 2-3 drops, gently pat into skin, wait 1-2 minutes before next step",
                "duration": "30 seconds"
            })
            step += 1
        
        # Moisturizer
        if product_categories["moisturizers"]:
            morning_routine.append({
                "step": step,
                "action": "Moisturizer",
                "product": product_categories["moisturizers"][0],
                "instructions": "Apply while skin is slightly damp for better absorption",
                "duration": "30 seconds"
            })
            step += 1
        
        # Sunscreen
        if product_categories["sunscreens"]:
            morning_routine.append({
                "step": step,
                "action": "Sunscreen SPF 30+",
                "product": product_categories["sunscreens"][0],
                "instructions": "Apply generously, reapply every 2 hours if outdoors",
                "duration": "1 minute"
            })
        
        # Generate evening routine (similar but no sunscreen)
        evening_routine = []
        step = 1
        
        # Double cleanse
        if product_categories["cleansers"]:
            evening_routine.append({
                "step": step,
                "action": "Double Cleanse",
                "product": product_categories["cleansers"][0],
                "instructions": "First with oil/balm, then with water-based cleanser",
                "duration": "2 minutes"
            })
            step += 1
        
        # Toner
        if product_categories["toners"]:
            evening_routine.append({
                "step": step,
                "action": "Toner",
                "product": product_categories["toners"][0],
                "instructions": "Apply with cotton pad or hands",
                "duration": "30 seconds"
            })
            step += 1
        
        # Serums
        for serum in product_categories["serums"][:2]:
            evening_routine.append({
                "step": step,
                "action": "Treatment Serum",
                "product": serum,
                "instructions": "Apply on clean, dry skin",
                "duration": "30 seconds"
            })
            step += 1
        
        # Moisturizer
        if product_categories["moisturizers"]:
            evening_routine.append({
                "step": step,
                "action": "Night Moisturizer",
                "product": product_categories["moisturizers"][0],
                "instructions": "Apply generously as last step to seal in treatments",
                "duration": "1 minute"
            })
        
        return {
            "morning": morning_routine,
            "evening": evening_routine,
            "key_ingredients": _extract_key_ingredients(recommendations),
            "timeline": "Expect to see improvements in 4-6 weeks with consistent use",
            "notes": [
                "Introduce new products one at a time (wait 1 week between additions)",
                "Always patch test new products",
                "Consistency is key - stick to routine for best results"
            ],
            "ai_enhanced": True,
            "personalization_score": _calculate_personalization_score(
                skin_analysis, user_profile, recommendations
            )
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced routine generation failed: {e}")
        return {
            "morning": [],
            "evening": [],
            "error": f"Routine generation failed: {str(e)}"
        }

def _categorize_product(product: Dict[str, Any]) -> str:
    """Categorize product by type"""
    name_lower = product.get("name", "").lower()
    
    if any(word in name_lower for word in ["cleanser", "wash", "foam"]):
        return "cleansers"
    elif any(word in name_lower for word in ["serum", "treatment", "ampoule"]):
        return "serums"
    elif any(word in name_lower for word in ["moisturizer", "cream", "lotion"]):
        return "moisturizers"
    elif any(word in name_lower for word in ["sunscreen", "spf", "sun"]):
        return "sunscreens"
    elif any(word in name_lower for word in ["toner", "essence", "mist"]):
        return "toners"
    else:
        return "treatments"

def _extract_key_ingredients(recommendations: List[Dict[str, Any]]) -> List[str]:
    """Extract key ingredients from recommendations"""
    ingredients = set()
    for product in recommendations:
        product_ingredients = product.get("ingredients", [])
        ingredients.update(product_ingredients)
    
    # Return top 10 most common ingredients
    return list(ingredients)[:10]

def _calculate_personalization_score(
    skin_analysis: Dict[str, Any],
    user_profile: Dict[str, Any],
    recommendations: List[Dict[str, Any]]
) -> float:
    """Calculate personalization score"""
    try:
        score = 0.0
        
        # Base score for having analysis
        if skin_analysis.get("detected_conditions"):
            score += 0.3
        
        # Score for user profile integration
        if user_profile:
            if user_profile.get("allergies"):
                score += 0.2
            if user_profile.get("skin_type"):
                score += 0.2
            if user_profile.get("sensitivity_level"):
                score += 0.1
        
        # Score for product variety
        if len(recommendations) >= 5:
            score += 0.2
        
        return min(1.0, score)
        
    except Exception as e:
        logger.error(f"❌ Personalization score calculation failed: {e}")
        return 0.5

# Performance monitoring endpoints
@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    try:
        if not PERFORMANCE_MONITORING_ENABLED:
            return {"error": "Performance monitoring is disabled"}
        
        analytics = await performance_monitoring_service.get_performance_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"❌ Metrics retrieval failed: {e}")
        return {"error": str(e)}

@app.get("/metrics/summary")
async def get_metrics_summary():
    """Get metrics summary"""
    try:
        if not PERFORMANCE_MONITORING_ENABLED:
            return {"error": "Performance monitoring is disabled"}
        
        summary = await performance_monitoring_service.get_metrics_summary()
        return summary
        
    except Exception as e:
        logger.error(f"❌ Metrics summary retrieval failed: {e}")
        return {"error": str(e)}

# Cache management endpoints
@app.post("/cache/clear")
async def clear_cache():
    """Clear all caches"""
    try:
        if not intelligent_caching_service.enabled:
            return {"error": "Caching is disabled"}
        
        # Clear memory cache
        intelligent_caching_service.memory_cache.clear()
        
        # Clear Redis cache
        if intelligent_caching_service.redis_client:
            await intelligent_caching_service.redis_client.flushdb()
        
        return {"success": True, "message": "All caches cleared"}
        
    except Exception as e:
        logger.error(f"❌ Cache clearing failed: {e}")
        return {"error": str(e)}

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        if not intelligent_caching_service.enabled:
            return {"error": "Caching is disabled"}
        
        stats = await intelligent_caching_service.get_cache_stats()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Cache stats retrieval failed: {e}")
        return {"error": str(e)}

# Existing endpoints (maintained for compatibility)
@app.post("/auth/signup")
async def signup(request: SignUpRequest):
    """User signup"""
    return await auth_manager.signup(request)

@app.post("/auth/signin")
async def signin(request: SignInRequest):
    """User signin"""
    return await auth_manager.signin(request)

@app.post("/auth/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token"""
    return await auth_manager.refresh_token(current_user)

@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    return await db_manager.get_profile(current_user["id"])

@app.put("/profile")
async def update_profile(
    request: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    return await db_manager.update_profile(current_user["id"], request)

@app.get("/skin-profile")
async def get_skin_profile(current_user: dict = Depends(get_current_user)):
    """Get user skin profile"""
    return await db_manager.get_skin_profile(current_user["id"])

@app.put("/skin-profile")
async def update_skin_profile(
    request: SkinProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user skin profile"""
    return await db_manager.update_skin_profile(current_user["id"], request)

# Application startup
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting Enhanced Dermalens API v2.0.0")
    logger.info(f"   - Vertex AI: {'✅' if VERTEX_AI_ENABLED else '❌'}")
    logger.info(f"   - Streaming: {'✅' if VERTEX_AI_STREAMING_ENABLED else '❌'}")
    logger.info(f"   - Ensemble: {'✅' if ENSEMBLE_ENABLED else '❌'}")
    logger.info(f"   - Monitoring: {'✅' if PERFORMANCE_MONITORING_ENABLED else '❌'}")

# Application shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Shutting down Enhanced Dermalens API")

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="info"
    )
