"""
Authentication handlers and middleware for Supabase integration
Uses custom database functions for authentication
"""
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from supabase import create_client, Client
import sys
import os

from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Validate Supabase URL format
def validate_supabase_url(url: str) -> bool:
    """Validate that Supabase URL is properly formatted"""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        if parsed.scheme not in ['http', 'https']:
            return False
        return True
    except Exception:
        return False

# Initialize Supabase client for auth operations with connection options
# Use lazy initialization to prevent startup crashes
supabase_auth: Optional[Client] = None
supabase_admin: Optional[Client] = None

def get_supabase_auth() -> Client:
    """Get or create Supabase auth client with lazy initialization"""
    global supabase_auth
    if supabase_auth is None:
        try:
            # Validate URL
            if not validate_supabase_url(SUPABASE_URL):
                raise ValueError(f"Invalid Supabase URL format: {SUPABASE_URL}")
            
            # Configure client with options for Cloud Run
            supabase_options = {
                "auto_refresh_token": False,
                "persist_session": False,
            }
            
            print(f"[AUTH] Initializing Supabase client with URL: {SUPABASE_URL}")
            print(f"[AUTH] URL parsed - scheme: {urlparse(SUPABASE_URL).scheme}, netloc: {urlparse(SUPABASE_URL).netloc}")
            
            supabase_auth = create_client(SUPABASE_URL, SUPABASE_ANON_KEY, options=supabase_options)
            print(f"[AUTH] Supabase auth client created successfully")
        except Exception as e:
            print(f"[AUTH] ERROR: Failed to create Supabase auth client: {str(e)}")
            print(f"[AUTH] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    return supabase_auth

def get_supabase_admin() -> Client:
    """Get or create Supabase admin client with lazy initialization"""
    global supabase_admin
    if supabase_admin is None:
        try:
            # Validate URL
            if not validate_supabase_url(SUPABASE_URL):
                raise ValueError(f"Invalid Supabase URL format: {SUPABASE_URL}")
            
            # Configure client with options for Cloud Run
            supabase_options = {
                "auto_refresh_token": False,
                "persist_session": False,
            }
            
            supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY, options=supabase_options)
            print(f"[AUTH] Supabase admin client created successfully")
        except Exception as e:
            print(f"[AUTH] ERROR: Failed to create Supabase admin client: {str(e)}")
            print(f"[AUTH] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    return supabase_admin

# HTTP Bearer token security
security = HTTPBearer()

class AuthManager:
    """Handles all authentication operations using custom database functions"""
    
    def __init__(self):
        self.supabase = None  # Will be initialized lazily
    
    def _get_supabase(self) -> Client:
        """Get Supabase client with lazy initialization"""
        if self.supabase is None:
            self.supabase = get_supabase_auth()
        return self.supabase
    
    async def sign_up(self, email: str, password: str) -> Dict:
        """Sign up a new user using custom database function"""
        print(f" [AUTH] Starting signup process for email: {email}")
        
        try:
            # Use the custom database function register_user_with_rls
            print(f" [AUTH] Calling register_user_with_rls function...")
            print(f" [AUTH] Supabase URL: {SUPABASE_URL}")
            print(f" [AUTH] Email: {email}")
            
            # Get Supabase client
            supabase = self._get_supabase()
            
            # Test connection first
            try:
                # Simple test query to verify connection
                test_result = supabase.table('profiles').select('id').limit(1).execute()
                print(f" [AUTH] Connection test successful")
            except Exception as conn_error:
                print(f" [AUTH] Connection test failed: {str(conn_error)}")
                print(f" [AUTH] Connection error type: {type(conn_error).__name__}")
                import traceback
                traceback.print_exc()
                return {
                    "success": False,
                    "error": f"Database connection failed: {str(conn_error)}"
                }
            
            # Retry logic for RPC calls (DNS/network issues)
            max_retries = 3
            result = None
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    print(f" [AUTH] RPC call attempt {attempt + 1}/{max_retries}")
                    result = supabase.rpc(
                        'register_user_with_rls',
                        {
                            'user_email': email,
                            'user_password': password,
                            'user_username': email.split('@')[0]  # Use email prefix as username
                        }
                    ).execute()
                    print(f" [AUTH] Registration result: {result}")
                    break  # Success, exit retry loop
                except Exception as rpc_error:
                    last_error = rpc_error
                    error_str = str(rpc_error)
                    print(f" [AUTH] RPC call attempt {attempt + 1} failed: {error_str}")
                    print(f" [AUTH] Error type: {type(rpc_error).__name__}")
                    
                    # If it's a DNS error, wait before retrying
                    if "Name or service not known" in error_str or "Errno -2" in error_str:
                        if attempt < max_retries - 1:
                            import time
                            wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                            print(f" [AUTH] DNS error detected, waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                        else:
                            # Last attempt failed
                            raise Exception(f"Failed to connect to Supabase after {max_retries} attempts. DNS resolution error: {error_str}")
                    else:
                        # Non-DNS error, don't retry
                        raise
            
            if result is None:
                raise Exception(f"RPC call failed after {max_retries} attempts: {last_error}")
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                print(f" [AUTH] User created successfully with ID: {user_data.get('user_id')}")
                
                # Generate JWT token for the session
                token_payload = {
                    'user_id': str(user_data.get('user_id')),
                    'email': user_data.get('email'),
                    'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
                }
                access_token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                
                return {
                    "success": True,
                    "access_token": access_token,
                    "user": {
                        "id": str(user_data.get('user_id')),
                        "email": user_data.get('email'),
                        "username": user_data.get('username'),
                        "created_at": str(user_data.get('created_at')),
                    }
                }
            else:
                print(f" [AUTH] No data returned from registration")
                return {
                    "success": False,
                    "error": "Failed to create user - no data returned"
                }
                
        except Exception as e:
            print(f" [AUTH] Signup failed with error: {str(e)}")
            # Check if user already exists
            if "already exists" in str(e).lower():
                return {
                    "success": False,
                    "error": "User with this email already exists"
                }
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_in(self, email: str, password: str) -> Dict:
        """Sign in an existing user using custom database function"""
        print(f" [AUTH] Starting signin process for email: {email}")
        
        try:
            # Use the custom database function authenticate_user_with_rls
            print(f" [AUTH] Calling authenticate_user_with_rls function...")
            supabase = self._get_supabase()
            result = supabase.rpc(
                'authenticate_user_with_rls',
                {
                    'user_email': email,
                    'user_password': password
                }
            ).execute()
            
            print(f" [AUTH] Authentication result: {result}")
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                print(f" [AUTH] User authenticated successfully with ID: {user_data.get('user_id')}")
                
                # Generate JWT token for the session
                token_payload = {
                    'user_id': str(user_data.get('user_id')),
                    'email': user_data.get('email'),
                    'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
                }
                access_token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                
                return {
                    "success": True,
                    "access_token": access_token,
                    "user": {
                        "id": str(user_data.get('user_id')),
                        "email": user_data.get('email'),
                        "username": user_data.get('username'),
                        "created_at": str(user_data.get('created_at')),
                    }
                }
            else:
                print(f" [AUTH] Invalid credentials - no data returned")
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
                
        except Exception as e:
            print(f" [AUTH] Signin failed with error: {str(e)}")
            if "Invalid email or password" in str(e):
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_out(self, access_token: str) -> Dict:
        """Sign out user"""
        try:
            # For custom auth, just return success (token will be discarded by client)
            return {"success": True, "message": "Signed out successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user(self, access_token: str) -> Dict:
        """Get current user from access token"""
        try:
            # Decode JWT token
            payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get('user_id')
            
            if not user_id:
                return {
                    "success": False,
                    "error": "Invalid token - no user_id"
                }
            
            # Get user profile from database
            supabase = self._get_supabase()
            result = supabase.rpc(
                'get_user_profile_with_rls',
                {'user_uuid': user_id}
            ).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                return {
                    "success": True,
                    "user": {
                        "id": str(user_data.get('user_id')),
                        "email": user_data.get('email'),
                        "username": user_data.get('username'),
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "User not found"
                }
                
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Invalid token"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def reset_password(self, email: str) -> Dict:
        """Request password reset"""
        try:
            # For now, just return success (implement email sending later)
            return {"success": True, "message": "Password reset email sent"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def refresh_token(self, current_user: dict) -> Dict:
        """Refresh JWT token"""
        try:
            # Create new token with same user data
            new_token = self.create_token(current_user['id'], current_user['email'])
            return {
                "success": True,
                "access_token": new_token
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token"""
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
    
    def create_token(self, user_id: str, email: str) -> str:
        """Create JWT token for user"""
        payload = {
            "user_id": user_id,
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
    """Dependency to get current user ID from token"""
    try:
        token = credentials.credentials
        result = auth_manager.verify_token(token)
        
        if not result["success"]:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return result["user_id"]
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Pydantic models for request/response
class SignUpRequest(BaseModel):
    email: str
    password: str

class SignInRequest(BaseModel):
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

