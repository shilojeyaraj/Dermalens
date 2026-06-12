"""
Database management for Dermalens Backend
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from supabase import Client, create_client

from config import (
    PROFILES_TABLE,
    SUPABASE_SERVICE_KEY,
    SUPABASE_URL,
    USER_IMAGES_TABLE,
    USER_SKIN_PROFILES_TABLE,
)


# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def _clean_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Remove keys where the value is None."""
    return {key: value for key, value in payload.items() if value is not None}


def _current_timestamp() -> str:
    """Return an ISO formatted UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


class UserProfileCreate(BaseModel):
    user_id: str
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None


class SkinProfileCreate(BaseModel):
    user_id: Optional[str] = None
    skin_type: Optional[str] = None
    skin_tone: Optional[str] = None
    acne_severity: Optional[str] = None
    pore_size: Optional[str] = None
    sensitivity_level: Optional[str] = None
    primary_concerns: List[str] = Field(default_factory=list)
    pre_existing_conditions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    preferred_brands: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)
    diet_type: Optional[str] = None
    water_intake: Optional[str] = None
    sleep_hours: Optional[str] = None
    sun_exposure: Optional[str] = None
    routine_frequency: Optional[str] = None
    routine_type: Optional[str] = None
    skin_goals: List[str] = Field(default_factory=list)
    additional_info: Optional[str] = None


class SkinProfileUpdate(BaseModel):
    skin_type: Optional[str] = None
    skin_tone: Optional[str] = None
    acne_severity: Optional[str] = None
    pore_size: Optional[str] = None
    sensitivity_level: Optional[str] = None
    primary_concerns: Optional[List[str]] = None
    pre_existing_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    preferred_brands: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    diet_type: Optional[str] = None
    water_intake: Optional[str] = None
    sleep_hours: Optional[str] = None
    sun_exposure: Optional[str] = None
    routine_frequency: Optional[str] = None
    routine_type: Optional[str] = None
    skin_goals: Optional[List[str]] = None
    additional_info: Optional[str] = None


class UserImageCreate(BaseModel):
    user_id: str
    image_url: str
    image_type: str
    analysis_results: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DatabaseManager:
    def __init__(self):
        self.supabase = supabase
        self.profiles_table = PROFILES_TABLE
        self.skin_profiles_table = USER_SKIN_PROFILES_TABLE
        self.images_table = USER_IMAGES_TABLE

    def _extract_single(self, result: Any) -> Optional[Dict[str, Any]]:
        """Return the first row from a Supabase response, if present."""
        data = getattr(result, "data", None)
        if isinstance(data, list) and data:
            return data[0]
        if isinstance(data, dict):
            return data
        return None

    def _fetch_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a profile row by id or user_id."""
        lookup = (
            self.supabase
            .table(self.profiles_table)
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        profile = self._extract_single(lookup)
        if profile:
            return profile

        lookup = (
            self.supabase
            .table(self.profiles_table)
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return self._extract_single(lookup)

    async def create_profile(
        self,
        user_id: str,
        email: str,
        username: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        age: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create or upsert a user profile."""
        try:
            payload = _clean_payload(
                {
                    "id": user_id,
                    "user_id": user_id,
                    "email": email,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "age": age,
                    "updated_at": _current_timestamp(),
                }
            )

            response = (
                self.supabase
                .table(self.profiles_table)
                .upsert(payload, on_conflict="id")
                .execute()
            )

            profile = self._extract_single(response) or self._fetch_profile(user_id)
            return {"success": True, "data": profile}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile by user id."""
        try:
            profile = self._fetch_profile(user_id)
            return {"success": True, "data": profile}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def update_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile."""
        try:
            updates = _clean_payload(update_data)
            if not updates:
                current = await self.get_profile(user_id)
                return {"success": True, "data": current.get("data")}

            updates["updated_at"] = _current_timestamp()
            response = (
                self.supabase
                .table(self.profiles_table)
                .update(updates)
                .eq("id", user_id)
                .execute()
            )

            profile = self._extract_single(response) or self._fetch_profile(user_id)
            return {"success": True, "data": profile}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def create_skin_profile(self, user_id: str, skin_profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or upsert a skin profile."""
        try:
            payload_data = dict(skin_profile_data or {})
            payload_data.pop("user_id", None)
            payload = SkinProfileCreate(user_id=user_id, **payload_data)
            data = payload.dict(exclude_none=True)
            data["updated_at"] = _current_timestamp()

            response = (
                self.supabase
                .table(self.skin_profiles_table)
                .upsert(data, on_conflict="user_id")
                .execute()
            )

            record = self._extract_single(response)
            if not record:
                record = (await self.get_skin_profile(user_id))["data"]
            return {"success": True, "data": record}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def get_skin_profile(self, user_id: str) -> Dict[str, Any]:
        """Get skin profile by user id."""
        try:
            response = (
                self.supabase
                .table(self.skin_profiles_table)
                .select("*")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            return {"success": True, "data": self._extract_single(response)}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def update_skin_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user skin profile."""
        try:
            update_payload = dict(update_data or {})
            update_payload.pop("user_id", None)
            updates = SkinProfileUpdate(**update_payload).dict(exclude_none=True)
            if not updates:
                return await self.get_skin_profile(user_id)

            updates["updated_at"] = _current_timestamp()
            response = (
                self.supabase
                .table(self.skin_profiles_table)
                .update(updates)
                .eq("user_id", user_id)
                .execute()
            )

            record = self._extract_single(response)
            if not record:
                record = (await self.get_skin_profile(user_id))["data"]
            return {"success": True, "data": record}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Alias for get_profile."""
        return await self.get_profile(user_id)

    async def get_user_images(self, user_id: str) -> Dict[str, Any]:
        """Get user images."""
        try:
            response = (
                self.supabase
                .table(self.images_table)
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            data = getattr(response, "data", []) or []
            return {"success": True, "data": data}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def delete_user_image(self, image_id: str) -> Dict[str, Any]:
        """Delete a user image by id."""
        try:
            response = (
                self.supabase
                .table(self.images_table)
                .delete()
                .eq("id", image_id)
                .execute()
            )
            return {"success": True, "data": getattr(response, "data", None)}
        except Exception as exc:
            return {"success": False, "error": str(exc)}


# Create global database manager instance
db_manager = DatabaseManager()

