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
from typing import List, Dict, Any
import json
from datetime import datetime

# Import our custom modules
from config import ALLOWED_ORIGINS, API_HOST, API_PORT, DEBUG
from database import db_manager, UserProfileCreate, UserProfileUpdate, SkinProfileCreate, SkinProfileUpdate, UserImageCreate
from auth import auth_manager, get_current_user, get_current_user_id, SignUpRequest, SignInRequest, PasswordResetRequest, TokenResponse

app = FastAPI(title="Dermalens Skin Analysis API", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
face_cascade = None
skin_model = None
device = None

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

def classify_skin_conditions(face_regions: List[np.ndarray]) -> List[Dict[str, Any]]:
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

def enhance_product_recommendations(products: List[Dict[str, Any]], user_skin_profile: Dict, detected_conditions: List[str]) -> List[Dict[str, Any]]:
    """Enhance product recommendations based on user's skin profile"""
    if not user_skin_profile:
        return products
    
    enhanced_products = []
    
    for product in products:
        # Add personalized scoring based on user profile
        personalized_score = 0
        
        # Consider skin type compatibility
        skin_type = user_skin_profile.get("skin_type")
        if skin_type == "dry" and "moisturizer" in product["type"].lower():
            personalized_score += 2
        elif skin_type == "oily" and "cleanser" in product["type"].lower():
            personalized_score += 2
        elif skin_type == "sensitive" and "gentle" in product["description"].lower():
            personalized_score += 3
        
        # Consider allergies
        allergies = user_skin_profile.get("allergies", [])
        product_safe = True
        for allergy in allergies:
            if allergy.lower() in product["description"].lower():
                product_safe = False
                break
        
        if not product_safe:
            continue
        
        # Consider sensitivity level
        sensitivity = user_skin_profile.get("sensitivity_level")
        if sensitivity == "high" and "fragrance-free" in product["description"].lower():
            personalized_score += 2
        elif sensitivity == "high" and any(ingredient in product["description"].lower() for ingredient in ["fragrance", "parfum", "alcohol"]):
            personalized_score -= 2
        
        # Add personalized score to product
        enhanced_product = product.copy()
        enhanced_product["personalized_score"] = product["rating"] + (personalized_score * 0.1)
        enhanced_products.append(enhanced_product)
    
    # Sort by personalized score
    enhanced_products.sort(key=lambda x: x["personalized_score"], reverse=True)
    return enhanced_products

def search_products(conditions: List[str]) -> List[Dict[str, Any]]:
    """Search for skincare products using Google Store API (mock implementation)"""
    # This is a mock implementation - in production, you'd use the actual Google Store API
    product_database = {
        "acne": [
            {
                "name": "CeraVe Acne Foaming Cream Cleanser",
                "brand": "CeraVe",
                "price": 16.99,
                "rating": 4.5,
                "description": "Contains benzoyl peroxide to treat acne",
                "image": "/cerave-acne-cleanser.jpg",
                "type": "Cleanser"
            },
            {
                "name": "The Ordinary Niacinamide 10% + Zinc 1%",
                "brand": "The Ordinary",
                "price": 12.90,
                "rating": 4.6,
                "description": "Reduces blemishes and balances oil production",
                "image": "/ordinary-niacinamide.jpg",
                "type": "Serum"
            }
        ],
        "hyperpigmentation": [
            {
                "name": "Paula's Choice 10% Azelaic Acid Booster",
                "brand": "Paula's Choice",
                "price": 36.00,
                "rating": 4.7,
                "description": "Reduces dark spots and evens skin tone",
                "image": "/paula-choice-azelaic.jpg",
                "type": "Treatment"
            },
            {
                "name": "The Ordinary Vitamin C Suspension 23%",
                "brand": "The Ordinary",
                "price": 7.20,
                "rating": 4.3,
                "description": "Brightens skin and reduces dark spots",
                "image": "/ordinary-vitamin-c.jpg",
                "type": "Serum"
            }
        ],
        "dry_skin": [
            {
                "name": "CeraVe Moisturizing Cream",
                "brand": "CeraVe",
                "price": 19.99,
                "rating": 4.8,
                "description": "Rich moisturizer with ceramides and hyaluronic acid",
                "image": "/cerave-moisturizer.jpg",
                "type": "Moisturizer"
            }
        ],
        "wrinkles": [
            {
                "name": "The Ordinary Retinol 0.5% in Squalane",
                "brand": "The Ordinary",
                "price": 9.80,
                "rating": 4.4,
                "description": "Anti-aging retinol treatment",
                "image": "/ordinary-retinol.jpg",
                "type": "Treatment"
            }
        ]
    }
    
    recommended_products = []
    for condition in conditions:
        if condition in product_database:
            recommended_products.extend(product_database[condition])
    
    # Remove duplicates and sort by rating
    unique_products = list({product["name"]: product for product in recommended_products}.values())
    return sorted(unique_products, key=lambda x: x["rating"], reverse=True)

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

# Authentication Endpoints
@app.post("/auth/signup", response_model=TokenResponse)
async def signup(request: SignUpRequest):
    """Sign up a new user"""
    try:
        # Create user in Supabase Auth
        auth_result = await auth_manager.sign_up(request.email, request.password)
        
        if not auth_result["success"]:
            raise HTTPException(status_code=400, detail=auth_result["error"])
        
        user = auth_result["user"]
        
        # Create user profile in database
        profile_result = await db_manager.create_profile(
            user_id=user.id,
            email=request.email,
            username=request.username
        )
        
        if not profile_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to create user profile")
        
        return TokenResponse(
            access_token=auth_result["session"].access_token,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
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
    """Analyze skin conditions from uploaded image or video (requires authentication)"""
    try:
        # Read file content
        content = await file.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(content, np.uint8)
        
        if file.content_type.startswith('video/'):
            # Handle video file
            temp_video = "temp_video.mp4"
            with open(temp_video, "wb") as f:
                f.write(content)
            
            # Extract frames from video
            cap = cv2.VideoCapture(temp_video)
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            cap.release()
            os.remove(temp_video)
            
            # Analyze every 10th frame to avoid too many similar images
            analysis_frames = frames[::10]
        else:
            # Handle image file
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            analysis_frames = [image]
        
        # Analyze each frame
        all_results = []
        for frame in analysis_frames:
            # Detect faces
            faces = detect_faces(frame)
            if len(faces) == 0:
                continue
            
            # Extract face regions
            face_regions = extract_face_regions(frame, faces)
            
            # Classify skin conditions
            results = classify_skin_conditions(face_regions)
            all_results.extend(results)
        
        if not all_results:
            raise HTTPException(status_code=400, detail="No faces detected in the uploaded file")
        
        # Aggregate results
        all_conditions = []
        for result in all_results:
            for condition_data in result["conditions"]:
                if condition_data["confidence"] > 0.3:  # Only include confident predictions
                    all_conditions.append(condition_data["condition"])
        
        # Get unique conditions
        unique_conditions = list(set(all_conditions))
        
        # Search for products
        products = search_products(unique_conditions)
        
        # Get user's skin profile for enhanced recommendations
        skin_profile_result = await db_manager.get_skin_profile(current_user_id)
        user_skin_profile = skin_profile_result["data"] if skin_profile_result["success"] else None
        
        # Enhance product recommendations based on user's skin profile
        enhanced_products = enhance_product_recommendations(products, user_skin_profile, unique_conditions)
        
        # Generate skincare routine
        routine = generate_skincare_routine(unique_conditions, enhanced_products)
        
        # Save analysis results to database (you might want to create a skin_analyses table)
        analysis_data = {
            "user_id": current_user_id,
            "detected_conditions": unique_conditions,
            "analysis_results": all_results,
            "recommended_products": enhanced_products,
            "skincare_routine": routine,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return {
            "analysis_results": all_results,
            "detected_conditions": unique_conditions,
            "recommended_products": enhanced_products,
            "skincare_routine": routine,
            "analysis_timestamp": datetime.now().isoformat(),
            "user_skin_profile": user_skin_profile
        }
        
    except Exception as e:
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

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
