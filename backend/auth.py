"""
Authentication handlers and middleware for Supabase integration
"""
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import jwt
from datetime import datetime, timedelta
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

# Initialize Supabase client for auth operations
supabase_auth: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# HTTP Bearer token security
security = HTTPBearer()

class AuthManager:
    """Handles all authentication operations"""
    
    def __init__(self):
        self.supabase = supabase_auth
    
    async def sign_up(self, email: str, password: str) -> Dict:
        """Sign up a new user"""
        try:
            result = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if result.user:
                return {
                    "success": True,
                    "user": result.user,
                    "session": result.session,
                    "message": "User created successfully. Please check your email for verification."
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create user"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_in(self, email: str, password: str) -> Dict:
        """Sign in an existing user"""
        try:
            result = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if result.user and result.session:
                return {
                    "success": True,
                    "user": result.user,
                    "session": result.session,
                    "access_token": result.session.access_token
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_out(self, access_token: str) -> Dict:
        """Sign out user"""
        try:
            # Set the session for the client
            self.supabase.auth.set_session(access_token, "")
            result = self.supabase.auth.sign_out()
            return {"success": True, "message": "Signed out successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user(self, access_token: str) -> Dict:
        """Get current user from access token"""
        try:
            # Set the session for the client
            self.supabase.auth.set_session(access_token, "")
            result = self.supabase.auth.get_user()
            
            if result.user:
                return {
                    "success": True,
                    "user": result.user
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid token"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reset_password(self, email: str) -> Dict:
        """Send password reset email"""
        try:
            result = self.supabase.auth.reset_password_email(email)
            return {
                "success": True,
                "message": "Password reset email sent"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return {
                "success": True,
                "user_id": payload.get("sub"),
                "email": payload.get("email")
            }
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Invalid token"}
    
    def create_token(self, user_id: str, email: str) -> str:
        """Create JWT token for user"""
        payload = {
            "sub": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Global auth manager instance
auth_manager = AuthManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        user_result = await auth_manager.get_user(token)
        
        if not user_result["success"]:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_result["user"]
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency to get current user ID"""
    user = await get_current_user(credentials)
    return user.id

# Request models for authentication
from pydantic import BaseModel, EmailStr

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict
