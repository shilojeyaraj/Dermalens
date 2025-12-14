"""
Authentication management for Dermalens Backend
"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import HTTPException, Depends
import jwt
from datetime import datetime, timedelta

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# JWT Configuration
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class SignUpRequest(BaseModel):
    email: str
    password: str
    username: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

class TokenResponse(BaseModel):
    access_token: str
    user: Dict[str, Any]

class AuthManager:
    def __init__(self):
        self.supabase = supabase

    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Sign up a new user using custom database function"""
        print(f" [AUTH] Starting signup process for email: {email}")
        
        try:
            print(f" [AUTH] Calling register_user_with_rls function...")
            result = self.supabase.rpc(
                'register_user_with_rls',
                {
                    'user_email': email,
                    'user_password': password,
                    'user_username': email.split('@')[0]
                }
            ).execute()
            
            if result.data:
                print(f" [AUTH] User registered successfully")
                
                # Generate JWT token
                token_payload = {
                    "user_id": result.data[0]["id"],
                    "email": email,
                    "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
                }
                
                token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                
                return {
                    "success": True,
                    "user": result.data[0],
                    "access_token": token
                }
            else:
                return {
                    "success": False,
                    "error": "Registration failed"
                }
                
        except Exception as e:
            print(f" [AUTH] Signup failed with error: {str(e)}")
            if "already exists" in str(e).lower():
                return {
                    "success": False,
                    "error": "User with this email already exists"
                }
            return {
                "success": False,
                "error": str(e)
            }

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user using custom database function"""
        print(f" [AUTH] Starting signin process for email: {email}")
        
        try:
            print(f" [AUTH] Calling authenticate_user_with_rls function...")
            result = self.supabase.rpc(
                'authenticate_user_with_rls',
                {
                    'user_email': email,
                    'user_password': password
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                print(f" [AUTH] User authenticated successfully")
                
                # Generate JWT token
                token_payload = {
                    "user_id": result.data[0]["id"],
                    "email": email,
                    "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
                }
                
                token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                
                return {
                    "success": True,
                    "user": result.data[0],
                    "access_token": token
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
                
        except Exception as e:
            print(f" [AUTH] Signin failed with error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Reset password for user"""
        try:
            # This would typically send a password reset email
            # For now, just return success
            return {
                "success": True,
                "message": "Password reset email sent"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "success": True,
            "user_id": payload.get("user_id"),
            "email": payload.get("email")
        }
    except jwt.ExpiredSignatureError:
        return {"success": False, "error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"success": False, "error": "Invalid token"}

async def get_current_user_id(token: str = Depends(lambda: None)) -> str:
    """Get current user ID from token"""
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    # Extract token from "Bearer <token>" format
    if token.startswith("Bearer "):
        token = token[7:]
    
    result = verify_token(token)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result["user_id"]

async def get_current_user(token: str = Depends(lambda: None)) -> Dict[str, Any]:
    """Get current user info from token"""
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    # Extract token from "Bearer <token>" format
    if token.startswith("Bearer "):
        token = token[7:]
    
    result = verify_token(token)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return {
        "id": result["user_id"],
        "email": result["email"]
    }

# Create global auth manager instance
auth_manager = AuthManager()
