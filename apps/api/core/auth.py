"""
Authentication handlers and middleware for Supabase integration
"""
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import jwt
from datetime import datetime, timedelta
from supabase import create_client, Client
<<<<<<< HEAD
from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

# Initialize Supabase client for auth operations
supabase_auth: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Initialize Supabase admin client for user creation without email confirmation
supabase_admin: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)
# HTTP Bearer token security
security = HTTPBearer()

class AuthManager:
    """Handles all authentication operations"""
    
    def __init__(self):
        self.supabase = supabase_auth
    
    async def sign_up(self, email: str, password: str) -> Dict:
        """Sign up a new user without email confirmation"""
        print(f"🔐 [AUTH] Starting signup process for email: {email}")
        
        try:
            # First, try to sign in to see if user already exists
            print(f"🔍 [AUTH] Checking if user already exists...")
            try:
                sign_in_result = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if sign_in_result.user and sign_in_result.session:
                    print(f"✅ [AUTH] User already exists, signing in successfully")
                    print(f"👤 [AUTH] User ID: {sign_in_result.user.id}")
                    print(f"🎫 [AUTH] Session created: {sign_in_result.session.access_token[:20]}...")
                    
                    # Convert User object to dictionary with safe attribute access
                    user_dict = {
                        "id": sign_in_result.user.id,
                        "email": sign_in_result.user.email,
                        "created_at": sign_in_result.user.created_at.isoformat() if sign_in_result.user.created_at else None,
                        "updated_at": sign_in_result.user.updated_at.isoformat() if sign_in_result.user.updated_at else None,
                        "email_confirmed_at": sign_in_result.user.email_confirmed_at.isoformat() if sign_in_result.user.email_confirmed_at else None,
                        "phone": getattr(sign_in_result.user, 'phone', '') or "",
                        "app_metadata": getattr(sign_in_result.user, 'app_metadata', {}) or {},
                        "user_metadata": getattr(sign_in_result.user, 'user_metadata', {}) or {},
                        "aud": getattr(sign_in_result.user, 'aud', 'authenticated') or "authenticated",
                        "confirmation_sent_at": sign_in_result.user.confirmation_sent_at.isoformat() if sign_in_result.user.confirmation_sent_at else None,
                        "recovery_sent_at": sign_in_result.user.recovery_sent_at.isoformat() if sign_in_result.user.recovery_sent_at else None,
                        "email_change_sent_at": sign_in_result.user.email_change_sent_at.isoformat() if sign_in_result.user.email_change_sent_at else None,
                        "new_email": getattr(sign_in_result.user, 'new_email', '') or "",
                        "new_phone": getattr(sign_in_result.user, 'new_phone', '') or "",
                        "invited_at": sign_in_result.user.invited_at.isoformat() if sign_in_result.user.invited_at else None,
                        "action_link": getattr(sign_in_result.user, 'action_link', '') or "",
                        "phone_confirmed_at": sign_in_result.user.phone_confirmed_at.isoformat() if sign_in_result.user.phone_confirmed_at else None,
                        "confirmed_at": sign_in_result.user.confirmed_at.isoformat() if sign_in_result.user.confirmed_at else None,
                        "email_change": getattr(sign_in_result.user, 'email_change', '') or "",
                        "phone_change": getattr(sign_in_result.user, 'phone_change', '') or "",
                        "last_sign_in_at": sign_in_result.user.last_sign_in_at.isoformat() if sign_in_result.user.last_sign_in_at else None,
                        "is_anonymous": getattr(sign_in_result.user, 'is_anonymous', False) or False,
                        "factors": getattr(sign_in_result.user, 'factors', []) or []
                    }
                    
                    return {
                        "success": True,
                        "user": user_dict,
                        "session": sign_in_result.session,
                        "access_token": sign_in_result.session.access_token,
                        "message": "User already exists and signed in successfully."
                    }
            except Exception as e:
                print(f"ℹ️ [AUTH] User doesn't exist yet, proceeding with creation: {str(e)}")
                pass
            
            # Use admin client to create user without email confirmation
            print(f"👤 [AUTH] Creating new user with admin client...")
            try:
                result = supabase_admin.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True,  # Auto-confirm email
                    "user_metadata": {
                        "email_confirmed": True
                    }
                })
                print(f"📊 [AUTH] Admin create_user result: {result}")
            except Exception as create_error:
                print(f"❌ [AUTH] Admin create_user failed: {str(create_error)}")
                # Try alternative approach - create user with different method
                try:
                    result = supabase_admin.auth.admin.create_user({
                        "email": email,
                        "password": password,
                        "email_confirm": False,  # Don't auto-confirm
                        "user_metadata": {
                            "email_confirmed": False
                        }
                    })
                    print(f"📊 [AUTH] Alternative create_user result: {result}")
                except Exception as alt_error:
                    print(f"❌ [AUTH] Alternative create_user also failed: {str(alt_error)}")
                    raise create_error
            
            if result.user:
                print(f"✅ [AUTH] User created successfully with admin client")
                print(f"👤 [AUTH] New User ID: {result.user.id}")
                print(f"📧 [AUTH] Email confirmed: {result.user.email_confirmed_at}")
                
                # Try to sign in with the regular client first
                print(f"🔑 [AUTH] Attempting to sign in with regular client...")
                try:
                    sign_in_result = self.supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if sign_in_result.user and sign_in_result.session:
                        print(f"✅ [AUTH] Sign in successful with regular client")
                        print(f"🎫 [AUTH] Session token: {sign_in_result.session.access_token[:20]}...")
                        
                        # Convert User object to dictionary with safe attribute access
                        user_dict = {
                            "id": sign_in_result.user.id,
                            "email": sign_in_result.user.email,
                            "created_at": sign_in_result.user.created_at.isoformat() if sign_in_result.user.created_at else None,
                            "updated_at": sign_in_result.user.updated_at.isoformat() if sign_in_result.user.updated_at else None,
                            "email_confirmed_at": sign_in_result.user.email_confirmed_at.isoformat() if sign_in_result.user.email_confirmed_at else None,
                            "phone": getattr(sign_in_result.user, 'phone', '') or "",
                            "app_metadata": getattr(sign_in_result.user, 'app_metadata', {}) or {},
                            "user_metadata": getattr(sign_in_result.user, 'user_metadata', {}) or {},
                            "aud": getattr(sign_in_result.user, 'aud', 'authenticated') or "authenticated",
                            "confirmation_sent_at": sign_in_result.user.confirmation_sent_at.isoformat() if sign_in_result.user.confirmation_sent_at else None,
                            "recovery_sent_at": sign_in_result.user.recovery_sent_at.isoformat() if sign_in_result.user.recovery_sent_at else None,
                            "email_change_sent_at": sign_in_result.user.email_change_sent_at.isoformat() if sign_in_result.user.email_change_sent_at else None,
                            "new_email": getattr(sign_in_result.user, 'new_email', '') or "",
                            "new_phone": getattr(sign_in_result.user, 'new_phone', '') or "",
                            "invited_at": sign_in_result.user.invited_at.isoformat() if sign_in_result.user.invited_at else None,
                            "action_link": getattr(sign_in_result.user, 'action_link', '') or "",
                            "phone_confirmed_at": sign_in_result.user.phone_confirmed_at.isoformat() if sign_in_result.user.phone_confirmed_at else None,
                            "confirmed_at": sign_in_result.user.confirmed_at.isoformat() if sign_in_result.user.confirmed_at else None,
                            "email_change": getattr(sign_in_result.user, 'email_change', '') or "",
                            "phone_change": getattr(sign_in_result.user, 'phone_change', '') or "",
                            "last_sign_in_at": sign_in_result.user.last_sign_in_at.isoformat() if sign_in_result.user.last_sign_in_at else None,
                            "is_anonymous": getattr(sign_in_result.user, 'is_anonymous', False) or False,
                            "factors": getattr(sign_in_result.user, 'factors', []) or []
                        }
                        
                        return {
                            "success": True,
                            "user": user_dict,
                            "session": sign_in_result.session,
                            "access_token": sign_in_result.session.access_token,
                            "message": "User created and signed in successfully."
                        }
                except Exception as e:
                    print(f"⚠️ [AUTH] Regular client sign in failed: {str(e)}")
                    
                    # If regular sign in fails, try with admin client
                    print(f"🔑 [AUTH] Attempting to sign in with admin client...")
                    try:
                        admin_sign_in = supabase_admin.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        
                        if admin_sign_in.user and admin_sign_in.session:
                            print(f"✅ [AUTH] Sign in successful with admin client")
                            print(f"🎫 [AUTH] Admin session token: {admin_sign_in.session.access_token[:20]}...")
                            
                            # Convert User object to dictionary with safe attribute access
                            user_dict = {
                                "id": admin_sign_in.user.id,
                                "email": admin_sign_in.user.email,
                                "created_at": admin_sign_in.user.created_at.isoformat() if admin_sign_in.user.created_at else None,
                                "updated_at": admin_sign_in.user.updated_at.isoformat() if admin_sign_in.user.updated_at else None,
                                "email_confirmed_at": admin_sign_in.user.email_confirmed_at.isoformat() if admin_sign_in.user.email_confirmed_at else None,
                                "phone": getattr(admin_sign_in.user, 'phone', '') or "",
                                "app_metadata": getattr(admin_sign_in.user, 'app_metadata', {}) or {},
                                "user_metadata": getattr(admin_sign_in.user, 'user_metadata', {}) or {},
                                "aud": getattr(admin_sign_in.user, 'aud', 'authenticated') or "authenticated",
                                "confirmation_sent_at": admin_sign_in.user.confirmation_sent_at.isoformat() if admin_sign_in.user.confirmation_sent_at else None,
                                "recovery_sent_at": admin_sign_in.user.recovery_sent_at.isoformat() if admin_sign_in.user.recovery_sent_at else None,
                                "email_change_sent_at": admin_sign_in.user.email_change_sent_at.isoformat() if admin_sign_in.user.email_change_sent_at else None,
                                "new_email": getattr(admin_sign_in.user, 'new_email', '') or "",
                                "new_phone": getattr(admin_sign_in.user, 'new_phone', '') or "",
                                "invited_at": admin_sign_in.user.invited_at.isoformat() if admin_sign_in.user.invited_at else None,
                                "action_link": getattr(admin_sign_in.user, 'action_link', '') or "",
                                "phone_confirmed_at": admin_sign_in.user.phone_confirmed_at.isoformat() if admin_sign_in.user.phone_confirmed_at else None,
                                "confirmed_at": admin_sign_in.user.confirmed_at.isoformat() if admin_sign_in.user.confirmed_at else None,
                                "email_change": getattr(admin_sign_in.user, 'email_change', '') or "",
                                "phone_change": getattr(admin_sign_in.user, 'phone_change', '') or "",
                                "last_sign_in_at": admin_sign_in.user.last_sign_in_at.isoformat() if admin_sign_in.user.last_sign_in_at else None,
                                "is_anonymous": getattr(admin_sign_in.user, 'is_anonymous', False) or False,
                                "factors": getattr(admin_sign_in.user, 'factors', []) or []
                            }
                            
                            return {
                                "success": True,
                                "user": user_dict,
                                "session": admin_sign_in.session,
                                "access_token": admin_sign_in.session.access_token,
                                "message": "User created and signed in successfully."
                            }
                    except Exception as e2:
                        print(f"❌ [AUTH] Admin client sign in also failed: {str(e2)}")
                        pass
                
                # If all sign in attempts fail, return the created user without session
                print(f"⚠️ [AUTH] All sign in attempts failed, returning user without session")
                
                # Convert User object to dictionary with safe attribute access
                user_dict = {
                    "id": result.user.id,
                    "email": result.user.email,
                    "created_at": result.user.created_at.isoformat() if result.user.created_at else None,
                    "updated_at": result.user.updated_at.isoformat() if result.user.updated_at else None,
                    "email_confirmed_at": result.user.email_confirmed_at.isoformat() if result.user.email_confirmed_at else None,
                    "phone": getattr(result.user, 'phone', '') or "",
                    "app_metadata": getattr(result.user, 'app_metadata', {}) or {},
                    "user_metadata": getattr(result.user, 'user_metadata', {}) or {},
                    "aud": getattr(result.user, 'aud', 'authenticated') or "authenticated",
                    "confirmation_sent_at": result.user.confirmation_sent_at.isoformat() if result.user.confirmation_sent_at else None,
                    "recovery_sent_at": result.user.recovery_sent_at.isoformat() if result.user.recovery_sent_at else None,
                    "email_change_sent_at": result.user.email_change_sent_at.isoformat() if result.user.email_change_sent_at else None,
                    "new_email": getattr(result.user, 'new_email', '') or "",
                    "new_phone": getattr(result.user, 'new_phone', '') or "",
                    "invited_at": result.user.invited_at.isoformat() if result.user.invited_at else None,
                    "action_link": getattr(result.user, 'action_link', '') or "",
                    "phone_confirmed_at": result.user.phone_confirmed_at.isoformat() if result.user.phone_confirmed_at else None,
                    "confirmed_at": result.user.confirmed_at.isoformat() if result.user.confirmed_at else None,
                    "email_change": getattr(result.user, 'email_change', '') or "",
                    "phone_change": getattr(result.user, 'phone_change', '') or "",
                    "last_sign_in_at": result.user.last_sign_in_at.isoformat() if result.user.last_sign_in_at else None,
                    "is_anonymous": getattr(result.user, 'is_anonymous', False) or False,
                    "factors": getattr(result.user, 'factors', []) or []
                }
                
                return {
                    "success": True,
                    "user": user_dict,
                    "session": None,
                    "access_token": None,
                    "message": "User created successfully."
                }
            else:
                print(f"❌ [AUTH] Failed to create user - no user returned from admin client")
                return {
                    "success": False,
                    "error": "Failed to create user"
                }
        except Exception as e:
            print(f"❌ [AUTH] Signup process failed with error: {str(e)}")
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
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict
