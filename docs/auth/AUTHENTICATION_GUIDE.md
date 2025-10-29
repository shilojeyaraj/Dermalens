# Dermalens Authentication Guide

## Overview

Dermalens uses a custom authentication system built on FastAPI with JWT tokens for secure user management. This guide covers the complete authentication flow, including signup, login, and session management.

## Architecture

### Backend (FastAPI)
- **Authentication Service**: `apps/api/core/auth.py`
- **Database Models**: `apps/api/database/connection.py`
- **JWT Token Management**: Built-in with `python-jose`
- **Password Hashing**: `passlib` with bcrypt

### Frontend (Next.js)
- **Auth Context**: `frontend/contexts/user-context-simple.tsx`
- **Auth Pages**: `frontend/app/signup/page.tsx`, `frontend/app/login/page.tsx`
- **Protected Routes**: Dashboard, Settings, Scan pages
- **Token Storage**: Browser localStorage

## Authentication Flow

### 1. User Registration (Signup)

#### Backend Endpoint
```
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Response
```json
{
  "success": true,
  "message": "User created successfully",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Frontend Implementation
```typescript
// frontend/app/signup/page.tsx
const handleSignup = async (email: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  
  const data = await response.json()
  if (data.success) {
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    router.push('/dashboard')
  }
}
```

### 2. User Login

#### Backend Endpoint
```
POST /auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Response
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "username": "user123",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Skincare enthusiast",
    "skin_type": "combination",
    "skin_concerns": "acne, dark spots",
    "allergies": "fragrance",
    "routine_preference": "moderate"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Frontend Implementation
```typescript
// frontend/app/login/page.tsx
const handleLogin = async (email: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/auth/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  
  const data = await response.json()
  if (data.success) {
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    router.push('/dashboard')
  }
}
```

### 3. Token Verification

#### Backend Middleware
```python
# apps/api/core/auth.py
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
```

#### Frontend Token Usage
```typescript
// All authenticated API calls include the token
const token = localStorage.getItem('token')
const response = await fetch(`${API_BASE_URL}/protected-endpoint`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

## User Profile Management

### Profile Data Structure
```typescript
interface User {
  id: string
  email: string
  username?: string
  first_name?: string
  last_name?: string
  bio?: string
  skin_type?: string
  skin_concerns?: string
  allergies?: string
  routine_preference?: string
  created_at: string
  updated_at: string
}
```

### Profile Update
```typescript
// frontend/app/settings/page.tsx
const updateProfile = async (profileData: any) => {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_BASE_URL}/auth/profile`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(profileData)
  })
}
```

## Protected Routes

### Route Protection Implementation
```typescript
// frontend/contexts/user-context-simple.tsx
export const useUser = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (token && userData) {
      setUser(JSON.parse(userData))
    }
    setLoading(false)
  }, [])

  return { user, loading }
}
```

### Protected Page Example
```typescript
// frontend/app/dashboard/page.tsx
export default function Dashboard() {
  const { user, loading } = useUser()
  
  if (loading) return <div>Loading...</div>
  if (!user) return <div>Please log in</div>
  
  return <div>Dashboard content</div>
}
```

## Security Features

### Password Security
- **Hashing**: bcrypt with salt rounds
- **Minimum Requirements**: 8+ characters
- **Storage**: Never stored in plain text

### JWT Token Security
- **Algorithm**: HS256
- **Expiration**: Configurable (default 24 hours)
- **Secret Key**: Environment variable
- **Claims**: User ID, expiration time

### CORS Configuration
```python
# apps/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling

### Common Error Responses
```json
// Invalid credentials
{
  "success": false,
  "error": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
}

// Token expired
{
  "success": false,
  "error": "Token has expired",
  "code": "TOKEN_EXPIRED"
}

// User not found
{
  "success": false,
  "error": "User not found",
  "code": "USER_NOT_FOUND"
}
```

### Frontend Error Handling
```typescript
const handleAuthError = (error: any) => {
  if (error.code === 'TOKEN_EXPIRED') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
  // Show user-friendly error message
  setError(error.message)
}
```

## Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=your-database-url
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# For production: https://your-backend-domain.com
```

## Deployment Considerations

### Production Security
1. **HTTPS Only**: All authentication must use HTTPS
2. **Secure Headers**: Implement security headers
3. **Rate Limiting**: Prevent brute force attacks
4. **Token Refresh**: Implement token refresh mechanism
5. **Session Management**: Proper logout and session cleanup

### Database Security
1. **Encrypted Connections**: Use SSL for database connections
2. **User Data Protection**: Encrypt sensitive user information
3. **Audit Logging**: Log authentication events
4. **Backup Security**: Secure database backups

## Troubleshooting

### Common Issues

#### 1. "Token has expired"
**Solution**: Implement token refresh or redirect to login
```typescript
if (response.status === 401) {
  localStorage.removeItem('token')
  router.push('/login')
}
```

#### 2. "CORS error"
**Solution**: Update CORS configuration in backend
```python
allow_origins=["https://your-frontend-domain.com"]
```

#### 3. "User not found"
**Solution**: Check user context initialization
```typescript
useEffect(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    setUser(JSON.parse(userData))
  }
}, [])
```

### Debug Mode
```typescript
// Enable debug logging
const DEBUG_AUTH = process.env.NODE_ENV === 'development'

if (DEBUG_AUTH) {
  console.log('Auth state:', { user, token })
}
```

## API Reference

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/signup` | POST | Create new user account | No |
| `/auth/signin` | POST | Login user | No |
| `/auth/me` | GET | Get current user info | Yes |
| `/auth/profile` | PUT | Update user profile | Yes |
| `/auth/logout` | POST | Logout user | Yes |

### Request/Response Examples

#### Signup Request
```bash
curl -X POST "https://api.dermalens.com/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

#### Login Request
```bash
curl -X POST "https://api.dermalens.com/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

#### Authenticated Request
```bash
curl -X GET "https://api.dermalens.com/auth/me" \
  -H "Authorization: Bearer your-jwt-token"
```

## Best Practices

### Frontend
1. **Token Storage**: Use localStorage for simplicity, consider httpOnly cookies for production
2. **Auto-logout**: Implement automatic logout on token expiration
3. **Loading States**: Show loading indicators during authentication
4. **Error Messages**: Provide clear, user-friendly error messages
5. **Form Validation**: Validate inputs before submission

### Backend
1. **Input Validation**: Validate all inputs using Pydantic models
2. **Rate Limiting**: Implement rate limiting for auth endpoints
3. **Logging**: Log authentication events for security monitoring
4. **Password Policy**: Enforce strong password requirements
5. **Token Management**: Implement proper token expiration and refresh

## Security Checklist

- [ ] Passwords are hashed with bcrypt
- [ ] JWT tokens use secure secret keys
- [ ] CORS is properly configured
- [ ] HTTPS is enforced in production
- [ ] Input validation is implemented
- [ ] Error messages don't leak sensitive information
- [ ] Rate limiting is enabled
- [ ] Authentication events are logged
- [ ] Tokens are properly expired
- [ ] User sessions are cleaned up on logout

---

For additional support or questions about the authentication system, please refer to the main documentation or contact the development team.
