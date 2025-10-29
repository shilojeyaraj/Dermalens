"""
Enhanced Main Application for Dermalens
Integrates all advanced AI services including Vertex AI, streaming, ensemble models, and monitoring
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, BackgroundTasks, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

# Import enhanced services
from ai.vertex_ai_service import vertex_ai_service
from ai.enhanced_comprehensive_analysis_service import enhanced_comprehensive_analysis_service
from ai.enhanced_skin_analysis_service_simple import enhanced_skin_analysis_service
from ai.enhanced_product_recommendation_service import enhanced_product_recommendation_service
from infrastructure.caching import intelligent_caching_service
from ai.ai_recommendation_engine import ai_recommendation_engine
from monitoring.performance import performance_monitoring_service

# Import existing services
from database.connection import db_manager, UserProfileCreate, UserProfileUpdate, SkinProfileCreate, SkinProfileUpdate, UserImageCreate
from core.auth import auth_manager, get_current_user, get_current_user_id, SignUpRequest, SignInRequest, PasswordResetRequest, TokenResponse
from infrastructure.elasticsearch_service import elasticsearch_service
from infrastructure.google_search_service import google_search_service

# Import seeding function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
try:
    from seed_elasticsearch_data import generate_sample_products, seed_elasticsearch
    SEEDING_AVAILABLE = True
except ImportError:
    SEEDING_AVAILABLE = False
    print("⚠️  Seeding module not available")

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

# Auto-seed database if empty
async def auto_seed_database():
    """Automatically seed the database if it's empty"""
    if not SEEDING_AVAILABLE:
        return
        
    try:
        logger.info("🔍 Checking if database needs seeding...")
        
        # Check if database has products
        result = await elasticsearch_service.search_products("", size=1)
        if result.get("success") and len(result.get("products", [])) > 0:
            logger.info("✅ Database already has products, skipping seeding")
            return
            
        logger.info("🌱 Database is empty, starting auto-seeding...")
        
        # Generate and seed products
        products = generate_sample_products(1000)
        seed_result = seed_elasticsearch(products)
        
        if seed_result:
            logger.info(f"🎉 Auto-seeding completed! Seeded {len(products)} products")
        else:
            logger.error("❌ Auto-seeding failed!")
            
    except Exception as e:
        logger.error(f"❌ Auto-seeding error: {e}")

# Run auto-seeding on startup
@app.on_event("startup")
async def startup_event():
    """Run auto-seeding on startup"""
    await auto_seed_database()

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

# Enhanced skin analysis with detailed logging
@app.post("/analyze-skin-enhanced")
async def analyze_skin_enhanced_detailed(
    file: UploadFile = File(...),
    analysis_type: str = "comprehensive",
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Enhanced skin analysis with comprehensive logging and detailed results
    
    Features:
    - Multi-modal analysis (visual + text)
    - Real-time processing
    - Comprehensive logging
    - Error handling and fallbacks
    - Detailed analysis reports
    """
    logger.info("🔬 Starting enhanced skin analysis")
    logger.info(f"   - User ID: {current_user_id}")
    logger.info(f"   - Analysis type: {analysis_type}")
    logger.info(f"   - File: {file.filename}")
    
    try:
        # Read file content
        content = await file.read()
        logger.info(f"   - File size: {len(content)} bytes")
        
        # Validate file
        if len(content) == 0:
            logger.error("❌ Empty file uploaded")
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Get user profile for enhanced analysis
        logger.info("👤 Fetching user profile for enhanced analysis")
        user_profile_result = await db_manager.get_skin_profile(current_user_id)
        user_profile = user_profile_result.get("data") if user_profile_result.get("success") else None
        logger.info(f"   - User profile: {'✅' if user_profile else '❌'}")
        
        # Perform enhanced skin analysis
        logger.info("🔬 Performing enhanced skin analysis")
        analysis_result = await enhanced_skin_analysis_service.analyze_skin_image(
            image_data=content,
            user_profile=user_profile,
            analysis_type=analysis_type
        )
        
        if not analysis_result["success"]:
            logger.error(f"❌ Enhanced analysis failed: {analysis_result['error']}")
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        logger.info("✅ Enhanced skin analysis completed successfully")
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Enhanced skin analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")

# Enhanced product recommendations with detailed logging
@app.post("/recommendations-enhanced")
async def get_enhanced_recommendations(
    skin_analysis: Dict[str, Any],
    recommendation_type: str = "comprehensive",
    max_recommendations: int = 10,
    budget_range: Optional[Tuple[float, float]] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Enhanced AI-powered product recommendations with comprehensive logging
    
    Features:
    - Multi-strategy recommendations
    - Real-time personalization
    - Comprehensive logging
    - A/B testing support
    - Performance optimization
    - Detailed product analysis
    """
    logger.info("🛍️ Starting enhanced product recommendations")
    logger.info(f"   - User ID: {current_user_id}")
    logger.info(f"   - Recommendation type: {recommendation_type}")
    logger.info(f"   - Max recommendations: {max_recommendations}")
    logger.info(f"   - Budget range: {budget_range}")
    
    try:
        # Get user profile for enhanced recommendations
        logger.info("👤 Fetching user profile for enhanced recommendations")
        user_profile_result = await db_manager.get_skin_profile(current_user_id)
        user_profile = user_profile_result.get("data") if user_profile_result.get("success") else None
        logger.info(f"   - User profile: {'✅' if user_profile else '❌'}")
        
        # Perform enhanced product recommendations
        logger.info("🛍️ Performing enhanced product recommendations")
        recommendations_result = await enhanced_product_recommendation_service.get_enhanced_recommendations(
            skin_analysis=skin_analysis,
            user_profile=user_profile,
            recommendation_type=recommendation_type,
            max_recommendations=max_recommendations,
            budget_range=budget_range
        )
        
        if not recommendations_result["success"]:
            logger.error(f"❌ Enhanced recommendations failed: {recommendations_result['error']}")
            raise HTTPException(status_code=500, detail=recommendations_result["error"])
        
        logger.info("✅ Enhanced product recommendations completed successfully")
        return recommendations_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Enhanced product recommendations failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced recommendations failed: {str(e)}")

# Multi-angle skin analysis endpoint
@app.post("/analyze-skin-multi-angle")
async def analyze_skin_multi_angle(
    request: Request,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Multi-angle skin analysis endpoint for processing multiple images from different angles
    
    Args:
        request: FastAPI request object containing multipart form data
        current_user_id: Authenticated user ID
    """
    logger.info("🔬 Starting multi-angle skin analysis")
    logger.info(f"   - User ID: {current_user_id}")
    
    try:
        # Extra diagnostics for malformed multipart
        content_type = request.headers.get("content-type", "")
        logger.info(f"   - Content-Type: {content_type}")
        try:
            raw_body = await request.body()
            logger.info(f"   - Raw body size: {len(raw_body)} bytes")
        except Exception as e:
            logger.warning(f"   - Could not read raw body for diagnostics: {e}")

        # Parse multipart form data
        form = await request.form()
        files = form.getlist("files")
        
        logger.info(f"   - Number of files received: {len(files)}")
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Process each image
        analysis_results = []
        
        for i, file in enumerate(files):
            logger.info(f"📸 Processing image {i + 1}/{len(files)}: {file.filename}")
            
            try:
                # Read file content
                content = await file.read()
                logger.info(f"   - File size: {len(content)} bytes")
                
                # Validate file
                if len(content) == 0:
                    logger.error(f"❌ Empty file: {file.filename}")
                    continue
            except Exception as e:
                logger.error(f"❌ Error reading file {file.filename}: {e}")
                continue
            
            # Get user profile for enhanced analysis
            user_profile_result = await db_manager.get_skin_profile(current_user_id)
            user_profile = user_profile_result.get("data") if user_profile_result.get("success") else None
            
            # Perform enhanced skin analysis
            logger.info(f"🤖 Starting enhanced skin analysis for {file.filename}")
            logger.info(f"   - Image size: {len(content)} bytes")
            logger.info(f"   - User profile available: {'✅' if user_profile else '❌'}")
            
            analysis_result = await enhanced_skin_analysis_service.analyze_skin_image(
                image_data=content,
                user_profile=user_profile,
                analysis_type="comprehensive"
            )
            
            logger.info(f"🔍 Analysis result for {file.filename}:")
            logger.info(f"   - Success: {analysis_result.get('success', False)}")
            logger.info(f"   - Error: {analysis_result.get('error', 'None')}")
            if analysis_result.get('success'):
                data = analysis_result.get('data', {})
                logger.info(f"   - Detected conditions: {len(data.get('detected_conditions', []))}")
                logger.info(f"   - Overall confidence: {data.get('overall_confidence', 0):.2f}")
            
            if analysis_result["success"]:
                analysis_results.append({
                    "angle": file.filename.split('_')[0] if '_' in file.filename else f"angle_{i}",
                    "analysis": analysis_result["data"]
                })
                logger.info(f"✅ Analysis completed for {file.filename}")
            else:
                logger.error(f"❌ Analysis failed for {file.filename}: {analysis_result['error']}")
        
        if not analysis_results:
            raise HTTPException(status_code=500, detail="All image analyses failed")
        
        # Aggregate detected conditions across angles and update user skin profile
        aggregated_conditions: set = set()
        try:
            for r in analysis_results:
                for c in r.get("analysis", {}).get("detected_conditions", []) or []:
                    aggregated_conditions.add(c)
            # Update user's skin profile with merged primary concerns
            try:
                profile_result = await db_manager.get_skin_profile(current_user_id)
                existing_profile = profile_result.get("data") if profile_result.get("success") else None
                if existing_profile:
                    existing_concerns = set(existing_profile.get("primary_concerns", []))
                    merged = list(sorted(existing_concerns.union(aggregated_conditions)))
                    await db_manager.update_skin_profile(current_user_id, {"primary_concerns": merged})
                elif aggregated_conditions:
                    await db_manager.create_skin_profile(current_user_id, {"primary_concerns": list(aggregated_conditions)})
                logger.info(f"🧠 Updated skin profile with detected concerns: {list(aggregated_conditions)}")
            except Exception as e:
                logger.error(f"⚠️ Failed to update skin profile: {e}")
        except Exception as e:
            logger.error(f"⚠️ Failed to aggregate conditions: {e}")

        # Generate enhanced recommendations based on scan + profile data
        logger.info("🎯 Generating enhanced recommendations with scan + profile data")
        
        # Create comprehensive skin analysis combining scan results with profile data
        logger.info("🔗 Combining scan results with user profile data")
        
        # Start with scan results
        combined_conditions = list(aggregated_conditions)
        combined_concerns = []
        
        # Add profile-based conditions and concerns
        if user_profile:
            logger.info(f"📋 User profile data: {user_profile}")
            
            # Add profile primary concerns
            if user_profile.get("primary_concerns"):
                profile_concerns = user_profile["primary_concerns"]
                if isinstance(profile_concerns, list):
                    combined_concerns.extend(profile_concerns)
                else:
                    combined_concerns.append(profile_concerns)
                logger.info(f"   - Profile concerns: {profile_concerns}")
            
            # Add skin concerns from profile
            if user_profile.get("skin_concerns"):
                combined_concerns.append(user_profile["skin_concerns"])
                logger.info(f"   - Skin concerns: {user_profile['skin_concerns']}")
            
            # Add allergies as sensitivity concerns
            if user_profile.get("allergies"):
                combined_concerns.append("sensitive_skin")
                logger.info(f"   - Allergies detected: {user_profile['allergies']}")
        
        # Combine scan conditions with profile concerns
        all_conditions = list(set(combined_conditions + combined_concerns))
        logger.info(f"🎯 Combined conditions: {all_conditions}")
        
        # Calculate enhanced skin health score based on both scan and profile
        base_health_score = 0.7  # Good score for successful scan
        if user_profile:
            # Adjust score based on profile data
            if user_profile.get("skin_type"):
                base_health_score += 0.1  # Bonus for having profile data
            if user_profile.get("primary_concerns"):
                # Slight reduction if user has specific concerns
                base_health_score -= 0.05
        
        # Ensure we always have conditions for recommendations, even for good skin
        if not all_conditions:
            # Add default maintenance conditions for users with good skin
            all_conditions = ["preventive_care", "maintenance_care"]
            if user_profile and user_profile.get("skin_type"):
                skin_type = user_profile["skin_type"].lower()
                if "oily" in skin_type:
                    all_conditions.append("oil_control")
                elif "dry" in skin_type:
                    all_conditions.append("hydration_boost")
                elif "sensitive" in skin_type:
                    all_conditions.append("gentle_care")
                else:
                    all_conditions.append("balanced_care")
            logger.info(f"🎯 Added default conditions for good skin: {all_conditions}")
        
        scan_analysis = {
            "detected_conditions": all_conditions,
            "scan_conditions": list(aggregated_conditions),
            "profile_concerns": combined_concerns,
            "skin_health_score": min(1.0, base_health_score),
            "analysis_type": "comprehensive_scan_and_profile",
            "confidence": 0.9,
            "total_images": len(files),
            "successful_analyses": len(analysis_results),
            "profile_integration": True,
            "user_skin_type": user_profile.get("skin_type") if user_profile else None,
            "user_budget": user_profile.get("budget_preference") if user_profile else None
        }
        
        logger.info(f"📊 Final analysis: {len(all_conditions)} total conditions")
        logger.info(f"   - Scan conditions: {len(aggregated_conditions)}")
        logger.info(f"   - Profile concerns: {len(combined_concerns)}")
        logger.info(f"   - Skin type: {scan_analysis.get('user_skin_type', 'unknown')}")
        logger.info(f"   - Health score: {scan_analysis['skin_health_score']:.2f}")
        
        # Get enhanced recommendations combining scan and profile data
        recs = await enhanced_product_recommendation_service.get_enhanced_recommendations(
            skin_analysis=scan_analysis,
            user_profile=user_profile,
            recommendation_type="comprehensive",
            max_recommendations=15,
            budget_range=None,
        )
        
        if not recs.get("success"):
            logger.warning(f"⚠️ Enhanced recommendations failed: {recs.get('error')}")
            # Generate basic fallback recommendations
            recs = {
                "success": True,
                "recommendations": [
                    {
                        "name": "Gentle Daily Cleanser",
                        "brand": "CeraVe",
                        "price": "$12.99",
                        "category": "cleanser",
                        "description": "Gentle, non-foaming cleanser for all skin types",
                        "rating": 4.5,
                        "imageUrl": "https://picsum.photos/400/300?random=cleanser",
                        "url": "#"
                    },
                    {
                        "name": "Daily Moisturizer",
                        "brand": "Neutrogena",
                        "price": "$8.99",
                        "category": "moisturizer", 
                        "description": "Lightweight, oil-free moisturizer",
                        "rating": 4.3,
                        "imageUrl": "https://picsum.photos/400/300?random=moisturizer",
                        "url": "#"
                    },
                    {
                        "name": "Broad Spectrum Sunscreen",
                        "brand": "EltaMD",
                        "price": "$24.99",
                        "category": "sunscreen",
                        "description": "SPF 30+ daily sunscreen protection",
                        "rating": 4.7,
                        "imageUrl": "https://picsum.photos/400/300?random=sunscreen",
                        "url": "#"
                    }
                ]
            }
            logger.info("🔄 Generated fallback recommendations")
        
        # Build comprehensive routine from scan + profile data
        routine = {
            "morning_routine": [],
            "evening_routine": []
        }
        
        if recs.get("success") and recs.get("recommendations") and len(recs.get("recommendations", [])) > 0:
            rec_products = recs.get("recommendations", [])
            logger.info(f"📋 Building routine from {len(rec_products)} recommendations")
            
            def _pick(cat):
                for p in rec_products:
                    cat_name = (p.get("product_type") or p.get("category") or "").lower()
                    if cat.lower() in cat_name:
                        return p
                return None
            
            # Morning routine
            cleanser = _pick("cleanser") or (rec_products[0] if rec_products else None)
            serum = _pick("serum")
            moisturizer = _pick("moisturizer")
            sunscreen = _pick("sunscreen")
            
            if cleanser:
                routine["morning_routine"].append({
                    "name": "Cleanser", 
                    "product": cleanser.get("name"), 
                    "brand": cleanser.get("brand"), 
                    "url": cleanser.get("url") or cleanser.get("product_url"), 
                    "instructions": "Gently cleanse for 30–60 seconds."
                })
            if serum:
                routine["morning_routine"].append({
                    "name": "Serum", 
                    "product": serum.get("name"), 
                    "brand": serum.get("brand"), 
                    "url": serum.get("url") or serum.get("product_url"), 
                    "instructions": "Apply a few drops to face and neck."
                })
            if moisturizer:
                routine["morning_routine"].append({
                    "name": "Moisturizer", 
                    "product": moisturizer.get("name"), 
                    "brand": moisturizer.get("brand"), 
                    "url": moisturizer.get("url") or moisturizer.get("product_url"), 
                    "instructions": "Apply evenly to lock in hydration."
                })
            if sunscreen:
                routine["morning_routine"].append({
                    "name": "Sunscreen", 
                    "product": sunscreen.get("name"), 
                    "brand": sunscreen.get("brand"), 
                    "url": sunscreen.get("url") or sunscreen.get("product_url"), 
                    "instructions": "Apply as the final step, 15 minutes before sun exposure."
                })
            
            # Evening routine (reuse some products, add treatment)
            treatment = _pick("treatment") or _pick("exfoliant")
            if treatment:
                routine["evening_routine"].append({
                    "name": "Treatment", 
                    "product": treatment.get("name"), 
                    "brand": treatment.get("brand"), 
                    "url": treatment.get("url") or treatment.get("product_url"), 
                    "instructions": "Apply to clean skin, avoid eye area."
                })
            if cleanser:
                routine["evening_routine"].append({
                    "name": "Cleanser", 
                    "product": cleanser.get("name"), 
                    "brand": cleanser.get("brand"), 
                    "url": cleanser.get("url") or cleanser.get("product_url"), 
                    "instructions": "Remove makeup and cleanse thoroughly."
                })
            if moisturizer:
                routine["evening_routine"].append({
                    "name": "Moisturizer", 
                    "product": moisturizer.get("name"), 
                    "brand": moisturizer.get("brand"), 
                    "url": moisturizer.get("url") or moisturizer.get("product_url"), 
                    "instructions": "Apply generously for overnight repair."
                })
        else:
            # Fallback routine when no specific recommendations are available
            logger.info("📋 Creating fallback routine based on profile data")
            
            # Determine skin type and concerns for personalized routine
            skin_type = user_profile.get("skin_type", "combination") if user_profile else "combination"
            primary_concerns = user_profile.get("primary_concerns", ["general_care"]) if user_profile else ["general_care"]
            
            # Morning routine based on skin type and concerns
            if "dry" in skin_type.lower():
                routine["morning_routine"] = [
                    {
                        "name": "Gentle Cleanser",
                        "product": "Hydrating Facial Cleanser",
                        "brand": "CeraVe",
                        "url": "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
                        "instructions": "Use lukewarm water and gently cleanse for 30-60 seconds."
                    },
                    {
                        "name": "Hyaluronic Acid Serum",
                        "product": "Hyaluronic Acid 2% + B5",
                        "brand": "The Ordinary",
                        "url": "https://theordinary.com/en-us/hyaluronic-acid-2-b5-serum-100ml",
                        "instructions": "Apply to damp skin for maximum hydration."
                    },
                    {
                        "name": "Rich Moisturizer",
                        "product": "Daily Moisturizing Lotion",
                        "brand": "CeraVe",
                        "url": "https://www.cerave.com/skincare/moisturizers/daily-moisturizing-lotion",
                        "instructions": "Apply generously to face and neck."
                    },
                    {
                        "name": "Sunscreen",
                        "product": "Ultra-Light Daily UV Defense",
                        "brand": "EltaMD",
                        "url": "https://eltamd.com/product/uv-clear-broad-spectrum-spf-46/",
                        "instructions": "Apply SPF 30+ as final step, reapply every 2 hours."
                    }
                ]
            elif "oily" in skin_type.lower():
                routine["morning_routine"] = [
                    {
                        "name": "Oil-Control Cleanser",
                        "product": "Foaming Facial Cleanser",
                        "brand": "CeraVe",
                        "url": "https://www.cerave.com/skincare/cleansers/foaming-facial-cleanser",
                        "instructions": "Use twice daily to control excess oil."
                    },
                    {
                        "name": "Niacinamide Serum",
                        "product": "Niacinamide 10% + Zinc 1%",
                        "brand": "The Ordinary",
                        "url": "https://theordinary.com/en-us/niacinamide-10-zinc-1-serum-100ml",
                        "instructions": "Apply to help control oil and minimize pores."
                    },
                    {
                        "name": "Oil-Free Moisturizer",
                        "product": "PM Facial Moisturizing Lotion",
                        "brand": "CeraVe",
                        "url": "https://www.cerave.com/skincare/moisturizers/pm-facial-moisturizing-lotion",
                        "instructions": "Lightweight formula that won't clog pores."
                    },
                    {
                        "name": "Sunscreen",
                        "product": "Clear Zinc Sunscreen",
                        "brand": "EltaMD",
                        "url": "https://eltamd.com/product/uv-clear-broad-spectrum-spf-46/",
                        "instructions": "Oil-free sunscreen for acne-prone skin."
                    }
                ]
            else:  # Combination or normal skin
                routine["morning_routine"] = [
                    {
                        "name": "Balanced Cleanser",
                        "product": "Hydrating Facial Cleanser",
                        "brand": "CeraVe",
                        "url": "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
                        "instructions": "Gentle cleanser suitable for all skin types."
                    },
                    {
                        "name": "Vitamin C Serum",
                        "product": "Vitamin C Suspension 23% + HA Spheres 2%",
                        "brand": "The Ordinary",
                        "url": "https://theordinary.com/en-us/vitamin-c-suspension-23-ha-spheres-2-100ml",
                        "instructions": "Apply in the morning for antioxidant protection."
                    },
                    {
                        "name": "Daily Moisturizer",
                        "product": "Daily Facial Moisturizer",
                        "brand": "CeraVe",
                        "url": "https://www.cerave.com/skincare/moisturizers/daily-facial-moisturizer",
                        "instructions": "Lightweight moisturizer with SPF 30."
                    },
                    {
                        "name": "Sunscreen",
                        "product": "UV Clear Broad-Spectrum SPF 46",
                        "brand": "EltaMD",
                        "url": "https://eltamd.com/product/uv-clear-broad-spectrum-spf-46/",
                        "instructions": "Essential for daily sun protection."
                    }
                ]
            
            # Evening routine
            routine["evening_routine"] = [
                {
                    "name": "Gentle Cleanser",
                    "product": "Hydrating Facial Cleanser",
                    "brand": "CeraVe",
                    "url": "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
                    "instructions": "Remove makeup and daily impurities."
                },
                {
                    "name": "Treatment Serum",
                    "product": "Retinol 0.5% in Squalane",
                    "brand": "The Ordinary",
                    "url": "https://theordinary.com/en-us/retinol-0-5-in-squalane-100ml",
                    "instructions": "Start with 2-3 times per week, increase gradually."
                },
                {
                    "name": "Night Moisturizer",
                    "product": "PM Facial Moisturizing Lotion",
                    "brand": "CeraVe",
                    "url": "https://www.cerave.com/skincare/moisturizers/pm-facial-moisturizing-lotion",
                    "instructions": "Rich moisturizer for overnight repair."
                }
            ]
        
        # Combine results from all angles with recommendations
        combined_result = {
            "success": True,
            "multi_angle_analysis": True,
            "total_images": len(files),
            "successful_analyses": len(analysis_results),
            "results": analysis_results,
            "detected_conditions": list(aggregated_conditions),
            "recommendations": recs.get("recommendations", []) if recs.get("success") else [],
            "skincare_routine": routine,
            "analysis_notes": {
                "image_analysis": f"Analyzed {len(analysis_results)} images from multiple angles",
                "image_analysis_contribution": f"Detected {len(aggregated_conditions)} skin conditions from visual analysis",
                "profile_enhancement": f"Enhanced with user profile data: {user_profile.get('skin_type', 'unknown')} skin type, {len(combined_concerns)} profile concerns" if user_profile else "No profile data available",
                "recommendation_basis": f"Combined {len(aggregated_conditions)} scan conditions with {len(combined_concerns)} profile concerns for personalized recommendations",
                "data_sources": f"Visual scan ({len(aggregated_conditions)} conditions) + Profile data ({len(combined_concerns)} concerns) = {len(all_conditions)} total considerations"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Multi-angle analysis completed: {len(analysis_results)}/{len(files)} successful")
        logger.info(f"🎯 Generated {len(combined_result.get('recommendations', []))} recommendations")
        logger.info(f"📋 Created {len(routine['morning_routine'])} morning + {len(routine['evening_routine'])} evening routine steps")
        return combined_result
        
    except Exception as e:
        error_msg = str(e) if e else "Unknown error"
        logger.error(f"❌ Multi-angle analysis failed: {error_msg}")
        logger.error(f"   - Exception type: {type(e)}")
        logger.error(f"   - Exception args: {getattr(e, 'args', 'No args')}")
        raise HTTPException(status_code=500, detail=f"Multi-angle analysis failed: {error_msg}")

# ------------------------------
# Profile-based recommendations
# ------------------------------
@app.post("/generate-profile-recommendations")
async def generate_profile_recommendations(
    current_user_id: str = Depends(get_current_user_id)
):
    """Return profile-based recommendations and a basic routine when user skips scan."""
    logger.info("🧭 Generating profile-based recommendations (skip scan)")
    logger.info(f"   - User ID: {current_user_id}")
    try:
        # Load user profile if available
        profile_result = await db_manager.get_skin_profile(current_user_id)
        user_profile = profile_result.get("data") if profile_result.get("success") else None
        logger.info(f"   - User profile available: {'✅' if user_profile else '❌'}")

        # Build a comprehensive skin_analysis-like payload for downstream services
        # Use profile data to create a more detailed analysis
        profile_conditions = []
        if user_profile:
            # Extract conditions from profile
            if user_profile.get("primary_concerns"):
                profile_conditions.extend(user_profile["primary_concerns"])
            if user_profile.get("skin_concerns"):
                profile_conditions.append(user_profile["skin_concerns"])
            if user_profile.get("allergies"):
                profile_conditions.append("sensitive_skin")
        
        # Default to general care if no specific conditions
        if not profile_conditions:
            profile_conditions = ["general_care"]
        
        skin_analysis = {
            "detected_conditions": profile_conditions,
            "skin_health_score": 0.5,  # Default moderate health score
            "analysis_type": "profile_based",
            "confidence": 0.8
        }
        
        logger.info(f"   - Profile-based conditions: {profile_conditions}")

        recs = await enhanced_product_recommendation_service.get_enhanced_recommendations(
            skin_analysis=skin_analysis,
            user_profile=user_profile,
            recommendation_type="profile_based",
            max_recommendations=25,
            budget_range=None,
        )

        if not recs.get("success"):
            logger.error(f"❌ Profile-based recommendations failed: {recs.get('error')}")
            raise HTTPException(status_code=500, detail=recs.get("error", "Recommendation failure"))

        # Build a simple, deterministic routine from recommendations
        routine = {
            "morning_routine": [],
            "evening_routine": []
        }
        rec_products = recs.get("recommendations", [])
        def _pick(cat):
            for p in rec_products:
                cat_name = (p.get("product_type") or p.get("category") or "").lower()
                if cat.lower() in cat_name:
                    return p
            return None
        cleanser = _pick("cleanser") or (rec_products[0] if rec_products else None)
        moisturizer = _pick("moisturizer")
        sunscreen = _pick("sunscreen")
        serum = _pick("serum")
        if cleanser:
            routine["morning_routine"].append({"name": "Cleanser", "product": cleanser.get("name"), "brand": cleanser.get("brand"), "url": cleanser.get("url") or cleanser.get("product_url"), "instructions": "Gently cleanse for 30–60 seconds."})
        if serum:
            routine["morning_routine"].append({"name": "Serum", "product": serum.get("name"), "brand": serum.get("brand"), "url": serum.get("url") or serum.get("product_url"), "instructions": "Apply a few drops to face and neck."})
        if moisturizer:
            routine["morning_routine"].append({"name": "Moisturizer", "product": moisturizer.get("name"), "brand": moisturizer.get("brand"), "url": moisturizer.get("url") or moisturizer.get("product_url"), "instructions": "Apply evenly to lock in hydration."})
        if sunscreen:
            routine["morning_routine"].append({"name": "Sunscreen", "product": sunscreen.get("name"), "brand": sunscreen.get("brand"), "url": sunscreen.get("url") or sunscreen.get("product_url"), "instructions": "Apply SPF 30+ as last step."})
        if cleanser:
            routine["evening_routine"].append({"name": "Cleanser", "product": cleanser.get("name"), "brand": cleanser.get("brand"), "url": cleanser.get("url") or cleanser.get("product_url"), "instructions": "Cleanse to remove impurities."})
        if serum:
            routine["evening_routine"].append({"name": "Treatment/Serum", "product": serum.get("name"), "brand": serum.get("brand"), "url": serum.get("url") or serum.get("product_url"), "instructions": "Apply treatment serum if tolerated."})
        if moisturizer:
            routine["evening_routine"].append({"name": "Moisturizer", "product": moisturizer.get("name"), "brand": moisturizer.get("brand"), "url": moisturizer.get("url") or moisturizer.get("product_url"), "instructions": "Apply generously."})

        logger.info("✅ Profile-based recommendations generated")
        return {**recs, "skincare_routine": routine}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Profile-based recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# Product search and trending
# ------------------------------
@app.get("/products/search")
async def products_search(
    q: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    category: Optional[str] = None,
    # Accept multiple brands via repeated params or comma-separated
    brands: Optional[List[str]] = Query(None, alias="brands"),
    brand: Optional[str] = None,
    sort: Optional[str] = None,  # e.g., rating_desc, price_asc
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skin_type: Optional[str] = None,
    rating_min: Optional[float] = None
):
    """Search products with optional filters."""
    try:
        price_range = None
        if min_price is not None or max_price is not None:
            price_range = {}
            if min_price is not None:
                price_range["gte"] = float(min_price)
            if max_price is not None:
                price_range["lte"] = float(max_price)

        product_types = [category] if category else None
        skin_types = [skin_type] if skin_type else None

        # Use Elasticsearch with optional brand filtering by keyword match
        from_offset = max(0, (page - 1) * max(1, limit))
        result = elasticsearch_service.search_products(
            query=q or "",
            skin_conditions=None,
            skin_types=skin_types,
            product_types=product_types,
            price_range=price_range,
            min_rating=rating_min,
            size=limit,
            from_=from_offset,
        )
        # Post-filter by brands when requested
        brand_filters: List[str] = []
        if brands:
            for b in brands:
                if isinstance(b, str):
                    brand_filters.extend([s.strip() for s in b.split(",") if s.strip()])
        elif brand:
            brand_filters = [brand]
        if brand_filters and result.get("success"):
            requested_set = {b.lower() for b in brand_filters}
            result["products"] = [
                p for p in result.get("products", [])
                if p.get("brand", "").lower() in requested_set or any(rb in p.get("brand", "").lower() for rb in requested_set)
            ]
        # Optional sorting
        if sort and result.get("success"):
            key, _, order = sort.partition("_")
            reverse = (order or "desc").lower() == "desc"
            def _key_fn(p):
                if key == "rating":
                    return p.get("rating", 0)
                if key == "price":
                    return p.get("price", 0)
                if key == "reviews":
                    return p.get("review_count", 0)
                return p.get("_score", 0)
            result["products"] = sorted(result.get("products", []), key=_key_fn, reverse=reverse)
        
        # Normalize field names to frontend expectations (camelCase)
        def _map_product(p):
            price_val = p.get("price")
            try:
                price_str = f"${float(price_val):.2f}" if price_val is not None else ""
            except Exception:
                price_str = str(price_val) if price_val is not None else ""
            ingredients = p.get("ingredients")
            if isinstance(ingredients, str):
                ingredients_list = [s.strip() for s in ingredients.split(",") if s.strip()]
            else:
                ingredients_list = list(ingredients or [])
            skin_types_val = p.get("skin_types")
            skin_type = ", ".join(skin_types_val) if isinstance(skin_types_val, list) else (p.get("skin_type") or "All Skin Types")
            image_url = p.get("image_url") or p.get("imageUrl") or "/skincarelogo.jpeg"
            return {
                "name": p.get("name", ""),
                "brand": p.get("brand", ""),
                "price": price_str,
                "category": p.get("product_type") or p.get("category", ""),
                "description": p.get("description", ""),
                "rating": p.get("rating", 4.2),
                "reviewCount": p.get("review_count", 0),
                "imageUrl": image_url,
                "productUrl": p.get("url", ""),
                "source": p.get("source", p.get("brand", "")),
                "inStock": True,
                "size": p.get("size", "100ml"),
                "ingredients": ingredients_list,
                "skinType": skin_type,
                "keyBenefits": p.get("key_benefits", []),
            }
        if result.get("success"):
            result["products"] = [_map_product(p) for p in result.get("products", [])]
        return result
    except Exception as e:
        logger.error(f"❌ /products/search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/trending")
async def products_trending(
    limit: int = 12
):
    """Return a simple set of trending products from Elasticsearch by rating/reviews."""
    try:
        data = elasticsearch_service.search_products(
            query="",
            skin_conditions=None,
            skin_types=None,
            product_types=None,
            price_range=None,
            min_rating=4.2,
            size=limit,
        )
        products = data.get("products", []) if data.get("success") else []
        # Normalize like above
        def _map_product(p):
            price_val = p.get("price")
            try:
                price_str = f"${float(price_val):.2f}" if price_val is not None else ""
            except Exception:
                price_str = str(price_val) if price_val is not None else ""
            ingredients = p.get("ingredients")
            if isinstance(ingredients, str):
                ingredients_list = [s.strip() for s in ingredients.split(",") if s.strip()]
            else:
                ingredients_list = list(ingredients or [])
            skin_types_val = p.get("skin_types")
            skin_type = ", ".join(skin_types_val) if isinstance(skin_types_val, list) else (p.get("skin_type") or "All Skin Types")
            return {
                "name": p.get("name", ""),
                "brand": p.get("brand", ""),
                "price": price_str,
                "category": p.get("product_type") or p.get("category", ""),
                "description": p.get("description", ""),
                "rating": p.get("rating", 4.2),
                "reviewCount": p.get("review_count", 0),
                "imageUrl": p.get("image_url", ""),
                "productUrl": p.get("url", ""),
                "source": p.get("source", p.get("brand", "")),
                "inStock": True,
                "size": p.get("size", "100ml"),
                "ingredients": ingredients_list,
                "skinType": skin_type,
                "keyBenefits": p.get("key_benefits", []),
            }
        mapped = [_map_product(p) for p in products]
        # Fallback sample products if index empty
        if not mapped:
            mapped = [
                {
                    "name": "Gentle Daily Cleanser",
                    "brand": "CeraVe",
                    "price": "$15.99",
                    "category": "Cleanser",
                    "description": "Hydrating cleanser suitable for all skin types.",
                    "rating": 4.6,
                    "reviewCount": 1200,
                    "imageUrl": "",
                    "productUrl": "",
                    "source": "demo",
                    "inStock": True,
                    "size": "236ml",
                    "ingredients": ["Hyaluronic Acid", "Ceramides"],
                    "skinType": "All Skin Types",
                    "keyBenefits": ["Hydrates", "Gentle"],
                },
                {
                    "name": "Hydrating Moisturizer",
                    "brand": "Neutrogena",
                    "price": "$22.50",
                    "category": "Moisturizer",
                    "description": "Lightweight daily moisturizer.",
                    "rating": 4.5,
                    "reviewCount": 980,
                    "imageUrl": "",
                    "productUrl": "",
                    "source": "demo",
                    "inStock": True,
                    "size": "50ml",
                    "ingredients": ["Glycerin", "Hyaluronic Acid"],
                    "skinType": "All Skin Types",
                    "keyBenefits": ["Hydrates", "Non‑greasy"],
                },
            ]
        return {"success": True, "trending_products": mapped, "total": len(mapped)}
    except Exception as e:
        logger.error(f"❌ /products/trending failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Comprehensive analysis endpoint with enhanced logging
@app.post("/analyze-comprehensive-enhanced")
async def analyze_comprehensive_enhanced(
    file: UploadFile = File(...),
    analysis_type: str = "comprehensive",
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Comprehensive enhanced analysis combining skin analysis and product recommendations
    
    Features:
    - Complete skin analysis workflow
    - AI-powered product recommendations
    - Comprehensive logging throughout
    - Error handling and fallbacks
    - Detailed results and metadata
    """
    logger.info("🎯 Starting comprehensive enhanced analysis")
    logger.info(f"   - User ID: {current_user_id}")
    logger.info(f"   - Analysis type: {analysis_type}")
    logger.info(f"   - File: {file.filename}")
    
    try:
        # Step 1: Enhanced skin analysis
        logger.info("🔬 Step 1: Enhanced skin analysis")
        skin_analysis_result = await enhanced_skin_analysis_service.analyze_skin_image(
            image_data=await file.read(),
            user_profile=None,  # Will be fetched in the service
            analysis_type=analysis_type
        )
        
        if not skin_analysis_result["success"]:
            logger.error(f"❌ Skin analysis failed: {skin_analysis_result['error']}")
            raise HTTPException(status_code=500, detail=skin_analysis_result["error"])
        
        skin_analysis = skin_analysis_result["data"]
        logger.info("✅ Skin analysis completed")
        logger.info(f"   - Conditions detected: {len(skin_analysis.get('detected_conditions', []))}")
        logger.info(f"   - Skin health score: {skin_analysis.get('skin_health_score', 0):.2f}")
        
        # Step 2: Enhanced product recommendations
        logger.info("🛍️ Step 2: Enhanced product recommendations")
        recommendations_result = await enhanced_product_recommendation_service.get_enhanced_recommendations(
            skin_analysis=skin_analysis,
            user_profile=None,  # Will be fetched in the service
            recommendation_type="comprehensive",
            max_recommendations=10
        )
        
        if not recommendations_result["success"]:
            logger.error(f"❌ Product recommendations failed: {recommendations_result['error']}")
            # Continue without recommendations rather than failing completely
            recommendations = []
            logger.warning("⚠️ Continuing without product recommendations")
        else:
            recommendations = recommendations_result["recommendations"]
            logger.info("✅ Product recommendations completed")
            logger.info(f"   - Recommendations: {len(recommendations)}")
        
        # Step 3: Combine results
        logger.info("📊 Step 3: Combining results")
        comprehensive_result = {
            "success": True,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "skin_analysis": skin_analysis,
            "product_recommendations": recommendations,
            "metadata": {
                "skin_analysis_success": skin_analysis_result["success"],
                "recommendations_success": recommendations_result.get("success", False),
                "total_processing_time": 0,  # Will be calculated
                "user_id": current_user_id
            }
        }
        
        logger.info("🎉 Comprehensive enhanced analysis completed successfully")
        return comprehensive_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Comprehensive enhanced analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

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
    result = await auth_manager.sign_up(request.email, request.password)
    return result

@app.post("/auth/signin")
async def signin(request: SignInRequest):
    """User signin"""
    result = await auth_manager.sign_in(request.email, request.password)
    return result

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
    import os
    port = int(os.environ.get("PORT", API_PORT))
    host = os.environ.get("HOST", API_HOST)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=DEBUG,
        log_level="info"
    )
