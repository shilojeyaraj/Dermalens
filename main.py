from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import io
import base64
import requests
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import google.generativeai as genai
from googlesearch import search

# Import our custom modules
from config import ALLOWED_ORIGINS, API_HOST, API_PORT, DEBUG, OPENAI_API_KEY, GOOGLE_WEB_SEARCH_API_KEY, GEMINI_API_KEY, GEMINI_ENABLED
from database import db_manager, UserProfileCreate, UserProfileUpdate, SkinProfileCreate, SkinProfileUpdate, UserImageCreate
from auth import auth_manager, get_current_user, get_current_user_id, SignUpRequest, SignInRequest, PasswordResetRequest, TokenResponse
import logging

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Dermalens Skin Analysis API", version="1.0.0")

# CORS middleware for frontend integration
print(f"≡ƒîÉ [CORS] Allowed origins: {ALLOWED_ORIGINS}")
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

# Global variables for models
face_cascade = None
skin_model = None
device = None

# Initialize OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Skin condition classes
SKIN_CONDITIONS = [
    "acne", "hyperpigmentation", "dark_spots", "wrinkles", 
    "dry_skin", "oily_skin", "sensitive_skin", "normal_skin",
    "blackheads", "whiteheads", "rosacea", "eczema"
]

class SkinConditionClassifier(nn.Module):
    """PyTorch model for skin condition classification"""
    def __init__(self, num_classes=len(SKIN_CONDITIONS)):
        super(SkinConditionClassifier, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

def initialize_models():
    """Initialize OpenCV and PyTorch models"""
    global face_cascade, skin_model, device
    
    # Initialize OpenCV face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Initialize PyTorch model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    skin_model = SkinConditionClassifier()
    skin_model.to(device)
    skin_model.eval()
    
    # Load pre-trained weights if available
    model_path = "models/skin_classifier.pth"
    if os.path.exists(model_path):
        skin_model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"Loaded pre-trained model from {model_path}")
    else:
        print("No pre-trained model found. Using random weights.")

def detect_faces(image: np.ndarray) -> List[tuple]:
    """Detect faces in image using OpenCV"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return faces

def extract_face_regions(image: np.ndarray, faces: List[tuple]) -> List[np.ndarray]:
    """Extract face regions from image"""
    face_regions = []
    for (x, y, w, h) in faces:
        # Add some padding around the face
        padding = 20
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        face_region = image[y1:y2, x1:x2]
        face_regions.append(face_region)
    return face_regions

def preprocess_image(image: np.ndarray) -> torch.Tensor:
    """Preprocess image for PyTorch model"""
    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize to model input size
    image_resized = cv2.resize(image_rgb, (224, 224))
    
    # Convert to PIL Image and apply transforms
    pil_image = Image.fromarray(image_resized)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    tensor = transform(pil_image).unsqueeze(0)
    return tensor.to(device)

def classify_skin_conditions(face_regions: List) -> List[Dict[str, Any]]:
    """Classify skin conditions in face regions"""
    results = []
    
    for i, face_region in enumerate(face_regions):
        # Preprocess image
        input_tensor = preprocess_image(face_region)
        
        # Get predictions
        with torch.no_grad():
            outputs = skin_model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            top_probs, top_indices = torch.topk(probabilities, 5)
        
        # Format results
        face_result = {
            "face_id": i,
            "conditions": []
        }
        
        for prob, idx in zip(top_probs[0], top_indices[0]):
            condition = SKIN_CONDITIONS[idx.item()]
            confidence = prob.item()
            face_result["conditions"].append({
                "condition": condition,
                "confidence": confidence,
                "severity": "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
            })
        
        results.append(face_result)
    
    return results



def normalize_user_profile(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure user profile has consistent defaults."""
    if not profile:
        return {}
    normalized = dict(profile)
    age_value = normalized.get("age")
    if age_value is not None:
        try:
            normalized["age"] = int(age_value)
        except (TypeError, ValueError):
            normalized["age"] = age_value
    for key in ("first_name", "last_name", "username", "phone"):
        if normalized.get(key) is None:
            normalized[key] = ""
    return normalized


def normalize_skin_profile(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure skin profile fields and aliases are available."""
    if not profile:
        return {}
    normalized = dict(profile)
    alias_source = normalized.get("skin_concerns") or normalized.get("primary_concerns")
    normalized["skin_concerns"] = list(alias_source or [])
    normalized["primary_concerns"] = list(normalized.get("primary_concerns") or normalized["skin_concerns"])
    for key in (
        "pre_existing_conditions",
        "allergies",
        "skin_goals",
        "preferred_brands",
        "medical_conditions",
    ):
        normalized[key] = list(normalized.get(key) or [])
    if normalized.get("additional_info") is None:
        normalized["additional_info"] = ""
    return normalized



def normalize_user_profile(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure user profile has consistent defaults."""
    if not profile:
        return {}
    normalized = dict(profile)
    age_value = normalized.get("age")
    if age_value is not None:
        try:
            normalized["age"] = int(age_value)
        except (TypeError, ValueError):
            normalized["age"] = age_value
    for key in ("first_name", "last_name", "username", "phone"):
        if normalized.get(key) is None:
            normalized[key] = ""
    return normalized


def normalize_skin_profile(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure skin profile fields and aliases are available."""
    if not profile:
        return {}
    normalized = dict(profile)
    alias_source = normalized.get("skin_concerns") or normalized.get("primary_concerns")
    normalized["skin_concerns"] = list(alias_source or [])
    normalized["primary_concerns"] = list(normalized.get("primary_concerns") or normalized["skin_concerns"])
    for key in (
        "pre_existing_conditions",
        "allergies",
        "skin_goals",
        "preferred_brands",
        "medical_conditions",
    ):
        normalized[key] = list(normalized.get(key) or [])
    if normalized.get("additional_info") is None:
        normalized["additional_info"] = ""
    return normalized

def enhance_product_recommendations(products: List[Dict[str, Any]], user_skin_profile: Dict, detected_conditions: List[str]) -> List[Dict[str, Any]]:
    """Enhance product recommendations based on user's skin profile"""
    profile = normalize_skin_profile(user_skin_profile)
    if not profile:
        return products

    enhanced_products = []

    for product in products:
        # Add personalized scoring based on user profile
        personalized_score = 0

        # Consider skin type compatibility
        skin_type = profile.get("skin_type")
        if skin_type == "dry" and "moisturizer" in product["type"].lower():
            personalized_score += 2
        elif skin_type == "oily" and "cleanser" in product["type"].lower():
            personalized_score += 2
        elif skin_type == "sensitive" and "gentle" in product["description"].lower():
            personalized_score += 3

        # Consider allergies
        allergies = profile.get("allergies", [])
        product_safe = True
        for allergy in allergies:
            if allergy.lower() in product["description"].lower():
                product_safe = False
                break

        if not product_safe:
            continue

        # Consider sensitivity level
        sensitivity = profile.get("sensitivity_level")
        if sensitivity == "high" and "fragrance-free" in product["description"].lower():
            personalized_score += 3
        elif sensitivity == "high" and "gentle" in product["description"].lower():
            personalized_score += 2

        # Boost for detected conditions
        for condition in detected_conditions:
            if condition.replace("_", " ") in product["description"].lower():
                personalized_score += 1

        # Boost for matching concerns
        for concern in profile.get("skin_concerns", []):
            if concern.replace("_", " ") in product["description"].lower():
                personalized_score += 2

        product_copy = dict(product)
        product_copy["personalized_score"] = personalized_score
        enhanced_products.append(product_copy)

    enhanced_products.sort(key=lambda x: x.get("personalized_score", 0), reverse=True)

    return enhanced_products

def generate_personalized_report(user_skin_profile: Dict, analysis_results: List[Dict], detected_conditions: List[str]) -> Dict[str, Any]:
    """Generate personalized skin report using Google Gemini 1.5 Pro"""
    if not GEMINI_API_KEY:
        return {
            "report": "AI report generation not available. Please check Gemini API configuration.",
            "recommendations": [],
            "timeframe": "N/A"
        }
    
    try:
        # Use Gemini for report generation
        from gemini_analysis_service import get_gemini_service
        gemini_service = get_gemini_service(GEMINI_API_KEY)
        
        # Generate report using Gemini
        report_result = gemini_service.generate_personalized_report(
            user_profile=user_skin_profile,
            analysis_results=analysis_results,
            detected_conditions=detected_conditions
        )
        
        if report_result["success"]:
            return report_result["report"]
        else:
            # Fallback to basic report
            return {
                "report": f"Analysis detected {len(detected_conditions)} skin concerns: {', '.join(detected_conditions)}. Please consult with a dermatologist for detailed recommendations.",
                "recommendations": [
                    "Use a gentle cleanser twice daily",
                    "Apply sunscreen with SPF 30+ every morning",
                    "Moisturize with a non-comedogenic formula"
                ],
                "timeframe": "2-4 weeks for initial improvements"
            }
        
    except Exception as e:
        logger.error(f"Error generating Gemini report: {e}")
        return {
            "report": f"Unable to generate AI report: {str(e)}",
            "recommendations": [],
            "timeframe": "N/A"
        }

async def search_skincare_products(conditions: List[str], user_preferences: Dict = None) -> List[Dict[str, Any]]:
    """Search for skincare products using Google Search API"""
    try:
        products = []
        
        for condition in conditions:
            # Create search query based on condition and user preferences
            search_terms = []
            
            if condition == "acne":
                search_terms = ["best acne treatment products 2024", "acne cleanser recommendations"]
            elif condition == "hyperpigmentation":
                search_terms = ["best hyperpigmentation treatment", "dark spot corrector products"]
            elif condition == "dry_skin":
                search_terms = ["best moisturizer for dry skin", "hydrating skincare products"]
            elif condition == "wrinkles":
                search_terms = ["anti-aging skincare products", "wrinkle treatment recommendations"]
            else:
                search_terms = [f"best {condition} treatment products"]
            
            # Add user preferences to search
            if user_preferences and user_preferences.get('preferred_brands'):
                for brand in user_preferences['preferred_brands'][:2]:  # Limit to top 2 brands
                    search_terms.append(f"{brand} {condition} products")
            
            # Perform searches (limited to avoid rate limits)
            for term in search_terms[:2]:  # Limit searches per condition
                try:
                    search_results = list(search(term, num_results=3))
                    for url in search_results:
                        products.append({
                            "name": f"Product for {condition}",
                            "brand": "Recommended Brand",
                            "price": "Varies",
                            "rating": 4.5,
                            "description": f"Recommended product for {condition} treatment",
                            "url": url,
                            "condition": condition,
                            "source": "Google Search"
                        })
                except Exception as e:
                    print(f"Search error for '{term}': {e}")
                    continue
        
        # Remove duplicates and limit results
        unique_products = []
        seen_urls = set()
        for product in products:
            if product['url'] not in seen_urls:
                unique_products.append(product)
                seen_urls.add(product['url'])
                if len(unique_products) >= 10:  # Limit total results
                    break
        
        return unique_products
        
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def generate_skincare_routine(conditions: List[str], products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate personalized skincare routine based on conditions and products"""
    
    # Categorize products by type
    cleansers = [p for p in products if p["type"] == "Cleanser"]
    treatments = [p for p in products if p["type"] in ["Serum", "Treatment"]]
    moisturizers = [p for p in products if p["type"] == "Moisturizer"]
    sunscreens = [p for p in products if p["type"] == "Sunscreen"]
    
    # Generate morning routine
    morning_routine = []
    step = 1
    
    if cleansers:
        morning_routine.append({
            "step": step,
            "name": "Gentle Cleanser",
            "product": cleansers[0]["name"],
            "brand": cleansers[0]["brand"],
            "duration": "1 min",
            "instructions": "Massage onto damp skin in circular motions, then rinse with lukewarm water."
        })
        step += 1
    
    if treatments:
        for treatment in treatments[:2]:  # Max 2 treatments
            morning_routine.append({
                "step": step,
                "name": treatment["name"].split(" - ")[0] if " - " in treatment["name"] else treatment["name"],
                "product": treatment["name"],
                "brand": treatment["brand"],
                "duration": "30 sec",
                "instructions": "Apply evenly to face and neck. Wait for absorption before next step."
            })
            step += 1
    
    if moisturizers:
        morning_routine.append({
            "step": step,
            "name": "Moisturizer",
            "product": moisturizers[0]["name"],
            "brand": moisturizers[0]["brand"],
            "duration": "30 sec",
            "instructions": "Apply evenly to face and neck while skin is still slightly damp."
        })
        step += 1
    
    if sunscreens:
        morning_routine.append({
            "step": step,
            "name": "Sunscreen SPF 50",
            "product": sunscreens[0]["name"],
            "brand": sunscreens[0]["brand"],
            "duration": "1 min",
            "instructions": "Apply generously as the final step. Reapply every 2 hours if outdoors."
        })
    
    # Generate evening routine (similar but without sunscreen)
    evening_routine = []
    step = 1
    
    if cleansers:
        evening_routine.append({
            "step": step,
            "name": "Gentle Cleanser",
            "product": cleansers[0]["name"],
            "brand": cleansers[0]["brand"],
            "duration": "1 min",
            "instructions": "Massage onto damp skin in circular motions, then rinse with lukewarm water."
        })
        step += 1
    
    if treatments:
        for treatment in treatments[:2]:
            evening_routine.append({
                "step": step,
                "name": treatment["name"].split(" - ")[0] if " - " in treatment["name"] else treatment["name"],
                "product": treatment["name"],
                "brand": treatment["brand"],
                "duration": "30 sec",
                "instructions": "Apply evenly to face and neck. Wait for absorption before next step."
            })
            step += 1
    
    if moisturizers:
        evening_routine.append({
            "step": step,
            "name": "Night Moisturizer",
            "product": moisturizers[0]["name"],
            "brand": moisturizers[0]["brand"],
            "duration": "1 min",
            "instructions": "Apply generously as the final step to lock in moisture overnight."
        })
    
    return {
        "morning_routine": morning_routine,
        "evening_routine": evening_routine,
        "total_products": len(products),
        "estimated_cost": sum(p["price"] for p in products),
        "generated_at": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    initialize_models()

@app.get("/")
async def root():
    return {"message": "Dermalens Skin Analysis API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": skin_model is not None}

@app.get("/test-db")
async def test_database():
    """Test database connection and table existence"""
    try:
        print("≡ƒº¬ [TEST] Testing database connection...")
        
        # Test profiles table
        try:
            result = db_manager.supabase.table("profiles").select("*").limit(1).execute()
            print(f"Γ£à [TEST] Profiles table exists and accessible")
        except Exception as e:
            print(f"Γ¥î [TEST] Profiles table error: {str(e)}")
            return {"error": f"Profiles table issue: {str(e)}"}
        
        # Test user_skin_profiles table
        try:
            result = db_manager.supabase.table("user_skin_profiles").select("*").limit(1).execute()
            print(f"Γ£à [TEST] User skin profiles table exists and accessible")
        except Exception as e:
            print(f"Γ¥î [TEST] User skin profiles table error: {str(e)}")
            return {"error": f"User skin profiles table issue: {str(e)}"}
        
        # Test user_images table
        try:
            result = db_manager.supabase.table("user_images").select("*").limit(1).execute()
            print(f"Γ£à [TEST] User images table exists and accessible")
        except Exception as e:
            print(f"Γ¥î [TEST] User images table error: {str(e)}")
            return {"error": f"User images table issue: {str(e)}"}
        
        return {"status": "all_tables_accessible", "message": "Database connection successful"}
        
    except Exception as e:
        print(f"Γ¥î [TEST] Database test failed: {str(e)}")
        return {"error": f"Database test failed: {str(e)}"}

@app.post("/test-analyze-skin")
async def test_analyze_skin(file: UploadFile = File(...)):
    """Test skin analysis without authentication"""
    print(f"≡ƒº¬ [TEST-ANALYZE] Testing skin analysis with file: {file.filename}")
    
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        contents = await file.read()
        print(f"≡ƒôü [TEST-ANALYZE] File size: {len(contents)} bytes")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        print(f"≡ƒû╝∩╕Å [TEST-ANALYZE] Image size: {image.size}")
        
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
        
        print(f"Γ£à [TEST-ANALYZE] Mock analysis complete")
        return mock_result
        
    except Exception as e:
        print(f"Γ¥î [TEST-ANALYZE] Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Authentication Endpoints
@app.post("/auth/signup", response_model=TokenResponse)
async def signup(request: SignUpRequest):
    """Sign up a new user"""
    print(f"≡ƒÜÇ [SIGNUP] Starting signup endpoint for email: {request.email}")
    print(f"≡ƒæñ [SIGNUP] Username: {request.username}")
    
    try:
        # Create user in Supabase Auth
        print(f"≡ƒöÉ [SIGNUP] Calling auth_manager.sign_up...")
        auth_result = await auth_manager.sign_up(request.email, request.password)
        
        if not auth_result["success"]:
            print(f"Γ¥î [SIGNUP] Auth signup failed: {auth_result['error']}")
            raise HTTPException(status_code=400, detail=auth_result["error"])
        
        user = auth_result["user"]
        print(f"Γ£à [SIGNUP] Auth signup successful")
        print(f"≡ƒæñ [SIGNUP] User ID: {user.id}")
        print(f"≡ƒôº [SIGNUP] User email: {user.email}")
        
        # Create user profile in database
        print(f"≡ƒÆ╛ [SIGNUP] Creating user profile in database...")
        
        # Use firstName and lastName from request, fallback to parsing username
        first_name = request.firstName or ""
        last_name = request.lastName or ""
        
        # If firstName/lastName not provided, try to parse from username
        if not first_name and not last_name and request.username:
            name_parts = request.username.strip().split(" ", 1)
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        print(f"≡ƒæñ [SIGNUP] First Name: {first_name}")
        print(f"≡ƒæñ [SIGNUP] Last Name: {last_name}")
        
        profile_result = await db_manager.create_profile(
            user_id=user.id,
            email=request.email,
            username=request.username,
            first_name=first_name,
            last_name=last_name
        )
        
        if not profile_result["success"]:
            print(f"Γ¥î [SIGNUP] Database profile creation failed: {profile_result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=500, detail="Failed to create user profile")
        
        print(f"Γ£à [SIGNUP] Database profile created successfully")
        
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
            print(f"≡ƒÄ½ [SIGNUP] Returning access token: {auth_result['session'].access_token[:20]}...")
            return TokenResponse(
                access_token=auth_result["session"].access_token,
                user=user_dict
            )
        else:
            print(f"ΓÜá∩╕Å [SIGNUP] No session available, user created but needs to sign in")
            # Create a temporary token or redirect to login
            # For now, we'll create a simple success response
            return TokenResponse(
                access_token="temp_token_please_sign_in",
                user=user_dict
            )
        
    except HTTPException as e:
        print(f"Γ¥î [SIGNUP] HTTPException: {e.detail}")
        raise
    except Exception as e:
        print(f"Γ¥î [SIGNUP] Unexpected error: {str(e)}")
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

        profile = normalize_user_profile(result.get("data"))
        return {"message": "Profile updated successfully", "profile": profile}
        
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
            result = await db_manager.update_skin_profile(current_user_id, skin_profile.dict(exclude_unset=True, exclude={"user_id"}))
        else:
            # Create new profile
            result = await db_manager.create_skin_profile(current_user_id, skin_profile.dict(exclude={"user_id"}))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])

        saved_profile = normalize_skin_profile(result.get("data"))
        return {"message": "Skin profile saved successfully", "skin_profile": saved_profile}
        
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
        result = await db_manager.update_skin_profile(current_user_id, skin_profile.dict(exclude_unset=True, exclude={"user_id"}))
        
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
    """Analyze skin conditions from uploaded image using real PyTorch model and Elasticsearch"""
    try:
        # Read file content
        content = await file.read()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Use the enhanced skin analysis service
        analysis_result = skin_analysis_service.analyze_skin_image(content)
        
        if not analysis_result["success"]:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Get user's skin profile for enhanced recommendations
        skin_profile_result = await db_manager.get_skin_profile(current_user_id)
        user_skin_profile = normalize_skin_profile(
            skin_profile_result.get("data") if skin_profile_result.get("success") else {}
        )
        
        # Get product recommendations using Elasticsearch
        detected_conditions = analysis_result["detected_conditions"]
        elasticsearch_result = elasticsearch_service.get_recommendations(
            user_skin_profile or {},
            analysis_result["analysis_results"],
            limit=10
        )
        
        # Get additional products from Google Search
        google_products = await search_skincare_products(detected_conditions, user_skin_profile)
        
        # Combine recommendations
        all_products = []
        if elasticsearch_result["success"]:
            all_products.extend(elasticsearch_result["recommendations"])
        all_products.extend(google_products)
        
        # Generate AI-powered personalized report using Gemini
        from gemini_analysis_service import get_gemini_service
        gemini_service = get_gemini_service(GEMINI_API_KEY)
        
        ai_report = gemini_service.generate_personalized_report(
            user_profile=user_skin_profile or {},
            analysis_results=analysis_result["analysis_results"],
            detected_conditions=detected_conditions
        )
        
        # Generate skincare routine using Gemini
        routine = gemini_service.generate_skincare_routine(
            conditions=detected_conditions,
            products=all_products,
            user_profile=user_skin_profile or {}
        )
        
        # Save analysis results to database
        analysis_data = {
            "user_id": current_user_id,
            "detected_conditions": detected_conditions,
            "analysis_results": analysis_result["analysis_results"],
            "recommended_products": all_products,
            "skincare_routine": routine,
            "skin_health_score": analysis_result.get("skin_health_score", 0),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return {
            "analysis_results": analysis_result["analysis_results"],
            "detected_conditions": detected_conditions,
            "recommended_products": all_products,
            "skincare_routine": routine,
            "ai_report": ai_report,
            "skin_health_score": analysis_result.get("skin_health_score", 0),
            "faces_detected": analysis_result.get("faces_detected", 0),
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
        products = search_products(conditions)
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
        
        routine = generate_skincare_routine(conditions, products)
        return routine
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routine generation failed: {str(e)}")

# Import the new comprehensive analysis service
from comprehensive_analysis_service import ComprehensiveSkinAnalysisService
from skin_analysis_service import skin_analysis_service
from elasticsearch_service import elasticsearch_service
from ingredient_database import ingredient_database
from validation_service import validation_service

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
