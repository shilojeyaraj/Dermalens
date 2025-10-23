from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import io
import os
from typing import List, Dict, Any
import json
from datetime import datetime

# Import our custom modules
from config import ALLOWED_ORIGINS, API_HOST, API_PORT, DEBUG, GEMINI_API_KEY, GEMINI_ENABLED
from database import db_manager, UserProfileCreate, UserProfileUpdate, SkinProfileCreate, SkinProfileUpdate, UserImageCreate
from auth import auth_manager, get_current_user, get_current_user_id, SignUpRequest, SignInRequest, PasswordResetRequest, TokenResponse
import logging

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Dermalens Skin Analysis API", version="1.0.0")

# CORS middleware for frontend integration
print(f"🔧 [CORS] Allowed origins: {ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add explicit OPTIONS handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "OK"}

@app.get("/")
async def root():
    return {"message": "Dermalens Skin Analysis API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "api_version": "1.0.0"}

@app.get("/test-db")
async def test_database():
    """Test database connection and table existence"""
    try:
        print("🔍 [TEST] Testing database connection...")
        
        # Test profiles table
        try:
            result = db_manager.supabase.table("profiles").select("*").limit(1).execute()
            print(f"✅ [TEST] Profiles table exists and accessible")
        except Exception as e:
            print(f"❌ [TEST] Profiles table error: {str(e)}")
            return {"error": f"Profiles table issue: {str(e)}"}
        
        # Test user_skin_profiles table
        try:
            result = db_manager.supabase.table("user_skin_profiles").select("*").limit(1).execute()
            print(f"✅ [TEST] User skin profiles table exists and accessible")
        except Exception as e:
            print(f"❌ [TEST] User skin profiles table error: {str(e)}")
            return {"error": f"User skin profiles table issue: {str(e)}"}
        
        # Test user_images table
        try:
            result = db_manager.supabase.table("user_images").select("*").limit(1).execute()
            print(f"✅ [TEST] User images table exists and accessible")
        except Exception as e:
            print(f"❌ [TEST] User images table error: {str(e)}")
            return {"error": f"User images table issue: {str(e)}"}
        
        return {"status": "all_tables_accessible", "message": "Database connection successful"}
        
    except Exception as e:
        print(f"❌ [TEST] Database test failed: {str(e)}")
        return {"error": f"Database test failed: {str(e)}"}

@app.post("/test-analyze-skin")
async def test_analyze_skin(file: UploadFile = File(...)):
    """Test skin analysis without authentication"""
    print(f"🔍 [TEST-ANALYZE] Testing skin analysis with file: {file.filename}")
    
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        contents = await file.read()
        print(f"📁 [TEST-ANALYZE] File size: {len(contents)} bytes")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        print(f"🖼️ [TEST-ANALYZE] Image size: {image.size}")
        
        # Simulate analysis (since we don't have the model loaded)
        mock_result = {
            "analysis_results": [
                {
                    "face_id": 0,
                    "conditions": [
                        {"condition": "acne", "confidence": 0.85, "severity": "moderate"},
                        {"condition": "dry_skin", "confidence": 0.72, "severity": "mild"},
                        {"condition": "dark_spots", "confidence": 0.68, "severity": "mild"}
                    ]
                }
            ],
            "detected_conditions": ["acne", "dry_skin", "dark_spots"],
            "recommended_products": [
                {
                    "name": "Salicylic Acid Cleanser",
                    "brand": "CeraVe",
                    "price": 15.99,
                    "rating": 4.5,
                    "description": "Gentle cleanser for acne-prone skin",
                    "image": "/facial-moisturizer-pump-bottle.jpg",
                    "type": "cleanser",
                    "personalized_score": 92
                }
            ],
            "skincare_routine": {
                "morning_routine": [
                    {
                        "step": 1,
                        "name": "Cleanse",
                        "product": "Salicylic Acid Cleanser",
                        "brand": "CeraVe",
                        "duration": "1-2 minutes",
                        "instructions": "Gently massage onto wet face, then rinse thoroughly"
                    }
                ],
                "evening_routine": [],
                "total_products": 1,
                "estimated_cost": 15.99,
                "generated_at": datetime.now().isoformat()
            },
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ [TEST-ANALYZE] Mock analysis complete")
        return mock_result
        
    except Exception as e:
        print(f"❌ [TEST-ANALYZE] Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Authentication Endpoints
@app.post("/auth/signup", response_model=TokenResponse)
async def signup(request: SignUpRequest):
    """Sign up a new user"""
    print(f"🔐 [SIGNUP] Starting signup endpoint for email: {request.email}")
    print(f"👤 [SIGNUP] Username: {request.username}")
    
    try:
        # Create user in Supabase Auth
        print(f"🔑 [SIGNUP] Calling auth_manager.sign_up...")
        auth_result = await auth_manager.sign_up(request.email, request.password)
        
        if not auth_result["success"]:
            print(f"❌ [SIGNUP] Auth signup failed: {auth_result['error']}")
            raise HTTPException(status_code=400, detail=auth_result["error"])
        
        user = auth_result["user"]
        print(f"✅ [SIGNUP] Auth signup successful")
        print(f"👤 [SIGNUP] User ID: {user.id}")
        print(f"📧 [SIGNUP] User email: {user.email}")
        
        # Create user profile in database
        print(f"💾 [SIGNUP] Creating user profile in database...")
        
        # Use firstName and lastName from request, fallback to parsing username
        first_name = request.firstName or ""
        last_name = request.lastName or ""
        
        # If firstName/lastName not provided, try to parse from username
        if not first_name and not last_name and request.username:
            name_parts = request.username.strip().split(" ", 1)
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        print(f"👤 [SIGNUP] First Name: {first_name}")
        print(f"👤 [SIGNUP] Last Name: {last_name}")
        
        profile_result = await db_manager.create_profile(
            user_id=user.id,
            email=request.email,
            username=request.username,
            first_name=first_name,
            last_name=last_name
        )
        
        if not profile_result["success"]:
            print(f"❌ [SIGNUP] Database profile creation failed: {profile_result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=500, detail="Failed to create user profile")
        
        print(f"✅ [SIGNUP] Database profile created successfully")
        
        # Convert Supabase User object to dictionary for Pydantic with safe attribute access
        user_dict = {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "email_confirmed_at": user.email_confirmed_at.isoformat() if user.email_confirmed_at else None,
            "phone": getattr(user, 'phone', '') or "",
            "app_metadata": getattr(user, 'app_metadata', {}) or {},
            "user_metadata": getattr(user, 'user_metadata', {}) or {},
            "aud": getattr(user, 'aud', 'authenticated') or "authenticated",
            "confirmation_sent_at": user.confirmation_sent_at.isoformat() if user.confirmation_sent_at else None,
            "recovery_sent_at": user.recovery_sent_at.isoformat() if user.recovery_sent_at else None,
            "email_change_sent_at": user.email_change_sent_at.isoformat() if user.email_change_sent_at else None,
            "new_email": getattr(user, 'new_email', '') or "",
            "new_phone": getattr(user, 'new_phone', '') or "",
            "invited_at": user.invited_at.isoformat() if user.invited_at else None,
            "action_link": getattr(user, 'action_link', '') or "",
            "phone_confirmed_at": user.phone_confirmed_at.isoformat() if user.phone_confirmed_at else None,
            "confirmed_at": user.confirmed_at.isoformat() if user.confirmed_at else None,
            "email_change": getattr(user, 'email_change', '') or "",
            "phone_change": getattr(user, 'phone_change', '') or "",
            "last_sign_in_at": user.last_sign_in_at.isoformat() if user.last_sign_in_at else None,
            "is_anonymous": getattr(user, 'is_anonymous', False) or False,
            "factors": getattr(user, 'factors', []) or []
        }
        
        # Handle case where session might be None
        if auth_result.get("session") and auth_result["session"].access_token:
            print(f"🎫 [SIGNUP] Returning access token: {auth_result['session'].access_token[:20]}...")
            return TokenResponse(
                access_token=auth_result["session"].access_token,
                user=user_dict
            )
        else:
            print(f"⚠️ [SIGNUP] No session available, user created but needs to sign in")
            # Create a temporary token or redirect to login
            # For now, we'll create a simple success response
            return TokenResponse(
                access_token="temp_token_please_sign_in",
                user=user_dict
            )
        
    except HTTPException as e:
        print(f"❌ [SIGNUP] HTTPException: {e.detail}")
        raise
    except Exception as e:
        print(f"❌ [SIGNUP] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/auth/signin", response_model=TokenResponse)
async def signin(request: SignInRequest):
    """Sign in an existing user"""
    try:
        result = await auth_manager.sign_in(request.email, request.password)
        
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])
        
        return TokenResponse(
            access_token=result["access_token"],
            user=result["user"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signin failed: {str(e)}")

@app.post("/auth/signout")
async def signout(current_user: Dict = Depends(get_current_user)):
    """Sign out current user"""
    try:
        # Note: In a real implementation, you'd need to handle token blacklisting
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signout failed: {str(e)}")

@app.post("/auth/reset-password")
async def reset_password(request: PasswordResetRequest):
    """Send password reset email"""
    try:
        result = await auth_manager.reset_password(request.email)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {"message": "Password reset email sent"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@app.get("/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    try:
        # Get user profile from database
        profile_result = await db_manager.get_profile(current_user.id)
        
        if not profile_result["success"]:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {
            "user": current_user,
            "profile": profile_result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

# User Profile Management Endpoints
@app.put("/profile")
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user profile"""
    try:
        result = await db_manager.update_profile(current_user_id, profile_update.dict(exclude_unset=True))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {"message": "Profile updated successfully", "profile": result["data"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.get("/profile")
async def get_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get user profile"""
    try:
        result = await db_manager.get_profile(current_user_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return result["data"]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

# Skin Profile Management Endpoints
@app.post("/skin-profile")
async def create_skin_profile(
    skin_profile: SkinProfileCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create or update user skin profile"""
    try:
        # Check if skin profile already exists
        existing_result = await db_manager.get_skin_profile(current_user_id)
        
        if existing_result["success"] and existing_result["data"]:
            # Update existing profile
            result = await db_manager.update_skin_profile(current_user_id, skin_profile.dict(exclude_unset=True))
        else:
            # Create new profile
            result = await db_manager.create_skin_profile(current_user_id, skin_profile.dict())
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {"message": "Skin profile saved successfully", "skin_profile": result["data"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save skin profile: {str(e)}")

@app.get("/skin-profile")
async def get_skin_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get user skin profile"""
    try:
        result = await db_manager.get_skin_profile(current_user_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail="Skin profile not found")
        
        return result["data"]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skin profile: {str(e)}")

@app.put("/skin-profile")
async def update_skin_profile(
    skin_profile: SkinProfileUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user skin profile"""
    try:
        result = await db_manager.update_skin_profile(current_user_id, skin_profile.dict(exclude_unset=True))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {"message": "Skin profile updated successfully", "skin_profile": result["data"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update skin profile: {str(e)}")

# User Images Management
@app.get("/images")
async def get_user_images(current_user_id: str = Depends(get_current_user_id)):
    """Get all user images"""
    try:
        result = await db_manager.get_user_images(current_user_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {"images": result["data"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get images: {str(e)}")

@app.delete("/images/{image_id}")
async def delete_user_image(image_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Delete user image"""
    try:
        # Verify image belongs to user
        images_result = await db_manager.get_user_images(current_user_id)
        if not images_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to verify image ownership")
        
        user_images = images_result["data"]
        image_exists = any(img["id"] == image_id for img in user_images)
        
        if not image_exists:
            raise HTTPException(status_code=404, detail="Image not found or access denied")
        
        result = await db_manager.delete_user_image(image_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {"message": "Image deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")

@app.post("/analyze-skin")
async def analyze_skin(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id)
):
    """Analyze skin conditions from uploaded image (simplified version)"""
    try:
        # Read file content
        content = await file.read()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Convert to PIL Image for basic processing
        image = Image.open(io.BytesIO(content))
        
        # Mock analysis results
        analysis_results = [
            {
                "face_id": 0,
                "conditions": [
                    {"condition": "acne", "confidence": 0.85, "severity": "moderate"},
                    {"condition": "dry_skin", "confidence": 0.72, "severity": "mild"},
                    {"condition": "dark_spots", "confidence": 0.68, "severity": "mild"}
                ]
            }
        ]
        
        detected_conditions = ["acne", "dry_skin", "dark_spots"]
        
        # Get product recommendations
        recommended_products = [
            {
                "name": "Salicylic Acid Cleanser",
                "brand": "CeraVe",
                "price": 15.99,
                "rating": 4.5,
                "description": "Gentle cleanser for acne-prone skin",
                "image": "/facial-moisturizer-pump-bottle.jpg",
                "type": "Cleanser"
            },
            {
                "name": "Hyaluronic Acid Moisturizer",
                "brand": "The Ordinary",
                "price": 12.90,
                "rating": 4.6,
                "description": "Hydrating moisturizer for dry skin",
                "image": "/moisturizer.jpg",
                "type": "Moisturizer"
            }
        ]
        
        # Get user's skin profile for enhanced recommendations
        skin_profile_result = await db_manager.get_skin_profile(current_user_id)
        user_skin_profile = skin_profile_result["data"] if skin_profile_result["success"] else None
        
        # Generate skincare routine
        routine = {
            "morning_routine": [
                {
                    "step": 1,
                    "name": "Cleanse",
                    "product": "Salicylic Acid Cleanser",
                    "brand": "CeraVe",
                    "duration": "1-2 minutes",
                    "instructions": "Gently massage onto wet face, then rinse thoroughly"
                },
                {
                    "step": 2,
                    "name": "Moisturize",
                    "product": "Hyaluronic Acid Moisturizer",
                    "brand": "The Ordinary",
                    "duration": "30 seconds",
                    "instructions": "Apply evenly to face and neck"
                }
            ],
            "evening_routine": [
                {
                    "step": 1,
                    "name": "Cleanse",
                    "product": "Salicylic Acid Cleanser",
                    "brand": "CeraVe",
                    "duration": "1-2 minutes",
                    "instructions": "Gently massage onto wet face, then rinse thoroughly"
                },
                {
                    "step": 2,
                    "name": "Moisturize",
                    "product": "Hyaluronic Acid Moisturizer",
                    "brand": "The Ordinary",
                    "duration": "30 seconds",
                    "instructions": "Apply evenly to face and neck"
                }
            ],
            "total_products": len(recommended_products),
            "estimated_cost": sum(p["price"] for p in recommended_products),
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate AI report
        ai_report = {
            "report": f"Analysis detected {len(detected_conditions)} skin concerns: {', '.join(detected_conditions)}. Based on your skin profile, we recommend a gentle cleansing routine with targeted treatments.",
            "recommendations": [
                "Use a gentle cleanser twice daily",
                "Apply moisturizer while skin is still damp",
                "Use sunscreen with SPF 30+ every morning",
                "Consider consulting a dermatologist for persistent acne"
            ],
            "timeframe": "2-4 weeks for initial improvements"
        }
        
        return {
            "analysis_results": analysis_results,
            "detected_conditions": detected_conditions,
            "recommended_products": recommended_products,
            "skincare_routine": routine,
            "ai_report": ai_report,
            "skin_health_score": 0.75,
            "faces_detected": 1,
            "analysis_timestamp": datetime.now().isoformat(),
            "user_skin_profile": user_skin_profile
        }
        
    except Exception as e:
        logger.error(f"Skin analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/search-products")
async def search_products_endpoint(
    conditions: List[str],
    current_user_id: str = Depends(get_current_user_id)
):
    """Search for products based on skin conditions (requires authentication)"""
    try:
        # Mock product search
        products = []
        for condition in conditions:
            if condition == "acne":
                products.append({
                    "name": "Salicylic Acid Cleanser",
                    "brand": "CeraVe",
                    "price": 15.99,
                    "rating": 4.5,
                    "description": "Gentle cleanser for acne-prone skin",
                    "type": "Cleanser"
                })
            elif condition == "dry_skin":
                products.append({
                    "name": "Hyaluronic Acid Moisturizer",
                    "brand": "The Ordinary",
                    "price": 12.90,
                    "rating": 4.6,
                    "description": "Hydrating moisturizer for dry skin",
                    "type": "Moisturizer"
                })
        
        return {"products": products, "conditions_searched": conditions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product search failed: {str(e)}")

@app.post("/generate-routine")
async def generate_routine_endpoint(
    request: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate skincare routine based on conditions and products (requires authentication)"""
    try:
        conditions = request.get("conditions", [])
        products = request.get("products", [])
        
        # Generate basic routine
        routine = {
            "morning_routine": [
                {
                    "step": 1,
                    "name": "Cleanse",
                    "product": "Gentle Cleanser",
                    "duration": "1-2 minutes",
                    "instructions": "Gently massage onto wet face, then rinse thoroughly"
                }
            ],
            "evening_routine": [
                {
                    "step": 1,
                    "name": "Cleanse",
                    "product": "Gentle Cleanser",
                    "duration": "1-2 minutes",
                    "instructions": "Gently massage onto wet face, then rinse thoroughly"
                }
            ],
            "total_products": len(products),
            "estimated_cost": sum(p.get("price", 0) for p in products),
            "generated_at": datetime.now().isoformat()
        }
        
        return routine
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routine generation failed: {str(e)}")

# Import the comprehensive analysis service
from comprehensive_analysis_service import ComprehensiveSkinAnalysisService

# Initialize the comprehensive analysis service
comprehensive_analysis_service = ComprehensiveSkinAnalysisService()

@app.post("/api/analyze-user-comprehensive")
async def analyze_user_comprehensive(
    request: Dict[str, Any]
    # Temporarily removed authentication for testing
    # current_user_id: str = Depends(get_current_user_id)
):
    """
    Comprehensive skin analysis using OpenAI Vision API and Google Custom Search
    
    Request body:
    {
        "user_id": "uuid-here",
        "image_id": "optional-specific-image-id"
    }
    """
    try:
        user_id = request.get("user_id")
        image_id = request.get("image_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Use the comprehensive analysis service
        result = await comprehensive_analysis_service.analyze_user_by_id(
            user_id=user_id,
            image_id=image_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

@app.get("/api/services-status")
async def get_services_status():
    """Check the status of all integrated services"""
    try:
        status = {
            "gemini": {
                "enabled": GEMINI_ENABLED and bool(GEMINI_API_KEY),
                "model": "gemini-1.5-pro" if (GEMINI_ENABLED and bool(GEMINI_API_KEY)) else None
            },
            "google_search": {
                "enabled": comprehensive_analysis_service.search.is_enabled(),
                "max_results": 10 if comprehensive_analysis_service.search.is_enabled() else None
            },
            "database": {
                "connected": True,  # We can add a health check here
                "tables": ["profiles", "user_skin_profiles", "user_images"]
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Service status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service status check failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
