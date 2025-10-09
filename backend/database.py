"""
Database operations and models for Supabase integration
"""
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from config import (
    SUPABASE_URL, 
    SUPABASE_SERVICE_KEY, 
    PROFILES_TABLE, 
    USER_IMAGES_TABLE, 
    USER_SKIN_PROFILES_TABLE
)

class DatabaseManager:
    """Manages all database operations with Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Profile Operations
    async def create_profile(self, user_id: str, email: str, username: str = None, profile_picture: str = None) -> Dict:
        """Create a new user profile"""
        try:
            profile_data = {
                "id": user_id,
                "email": email,
                "username": username,
                "profile_picture": profile_picture,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table(PROFILES_TABLE).insert(profile_data).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_profile(self, user_id: str) -> Dict:
        """Get user profile by ID"""
        try:
            result = self.supabase.table(PROFILES_TABLE).select("*").eq("id", user_id).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_profile(self, user_id: str, updates: Dict) -> Dict:
        """Update user profile"""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            result = self.supabase.table(PROFILES_TABLE).update(updates).eq("id", user_id).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # User Skin Profile Operations
    async def create_skin_profile(self, user_id: str, skin_data: Dict) -> Dict:
        """Create user skin profile"""
        try:
            skin_profile_data = {
                "user_id": user_id,
                "skin_type": skin_data.get("skin_type"),
                "skin_tone": skin_data.get("skin_tone"),
                "acne_severity": skin_data.get("acne_severity"),
                "pore_size": skin_data.get("pore_size"),
                "sensitivity_level": skin_data.get("sensitivity_level"),
                "primary_concerns": skin_data.get("primary_concerns", []),
                "pre_existing_conditions": skin_data.get("pre_existing_conditions", []),
                "allergies": skin_data.get("allergies", []),
                "diet_type": skin_data.get("diet_type"),
                "water_intake": skin_data.get("water_intake"),
                "sleep_hours": skin_data.get("sleep_hours"),
                "sun_exposure": skin_data.get("sun_exposure"),
                "routine_frequency": skin_data.get("routine_frequency"),
                "routine_type": skin_data.get("routine_type"),
                "skin_goals": skin_data.get("skin_goals", []),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table(USER_SKIN_PROFILES_TABLE).insert(skin_profile_data).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_skin_profile(self, user_id: str) -> Dict:
        """Get user skin profile by user ID"""
        try:
            result = self.supabase.table(USER_SKIN_PROFILES_TABLE).select("*").eq("user_id", user_id).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_skin_profile(self, user_id: str, updates: Dict) -> Dict:
        """Update user skin profile"""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            result = self.supabase.table(USER_SKIN_PROFILES_TABLE).update(updates).eq("user_id", user_id).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # User Images Operations
    async def save_user_image(self, user_id: str, storage_path: str, bucket: str = "user-images") -> Dict:
        """Save user image metadata to database"""
        try:
            image_data = {
                "user_id": user_id,
                "storage_path": storage_path,
                "bucket": bucket,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table(USER_IMAGES_TABLE).insert(image_data).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_images(self, user_id: str) -> Dict:
        """Get all images for a user"""
        try:
            result = self.supabase.table(USER_IMAGES_TABLE).select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return {"success": True, "data": result.data if result.data else []}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_user_image(self, image_id: str) -> Dict:
        """Delete user image"""
        try:
            result = self.supabase.table(USER_IMAGES_TABLE).delete().eq("id", image_id).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Create global database manager instance
db_manager = DatabaseManager()

# Pydantic models for request/response validation
from pydantic import BaseModel, Field
from typing import List, Optional

class UserProfileCreate(BaseModel):
    email: str
    username: Optional[str] = None
    profile_picture: Optional[str] = None

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    profile_picture: Optional[str] = None

class SkinProfileCreate(BaseModel):
    skin_type: Optional[str] = None
    skin_tone: Optional[str] = None
    acne_severity: Optional[str] = None
    pore_size: Optional[str] = None
    sensitivity_level: Optional[str] = None
    primary_concerns: List[str] = []
    pre_existing_conditions: List[str] = []
    allergies: List[str] = []
    diet_type: Optional[str] = None
    water_intake: Optional[str] = None
    sleep_hours: Optional[str] = None
    sun_exposure: Optional[str] = None
    routine_frequency: Optional[str] = None
    routine_type: Optional[str] = None
    skin_goals: List[str] = []

class SkinProfileUpdate(BaseModel):
    skin_type: Optional[str] = None
    skin_tone: Optional[str] = None
    acne_severity: Optional[str] = None
    pore_size: Optional[str] = None
    sensitivity_level: Optional[str] = None
    primary_concerns: Optional[List[str]] = None
    pre_existing_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    diet_type: Optional[str] = None
    water_intake: Optional[str] = None
    sleep_hours: Optional[str] = None
    sun_exposure: Optional[str] = None
    routine_frequency: Optional[str] = None
    routine_type: Optional[str] = None
    skin_goals: Optional[List[str]] = None

class UserImageCreate(BaseModel):
    storage_path: str
    bucket: str = "user-images"
