# Supabase Integration Guide for Dermalens

This guide explains how the Supabase integration works in your Dermalens backend.

## Overview

Your backend now includes complete Supabase integration with:
- User authentication and management
- Database operations for user profiles and skin profiles
- Image storage management
- Personalized recommendations based on user data

## Database Schema

Your Supabase database has 3 main tables:

### 1. `profiles` table
- Stores basic user information
- Links to Supabase Auth users
- Fields: `id`, `email`, `username`, `profile_picture`, `created_at`, `updated_at`

### 2. `user_skin_profiles` table
- Stores detailed skin profile information from signup form
- Fields: `skin_type`, `skin_tone`, `acne_severity`, `allergies`, `primary_concerns`, etc.
- Links to user via `user_id`

### 3. `user_images` table
- Stores metadata for user-uploaded images
- Fields: `user_id`, `storage_path`, `bucket`, `created_at`
- Links to user via `user_id`

## Authentication Flow

### 1. User Registration
```
POST /auth/signup
{
  "email": "user@example.com",
  "password": "password123",
  "username": "optional_username"
}
```

**What happens:**
1. Creates user in Supabase Auth
2. Creates profile record in `profiles` table
3. Returns JWT token for authentication

### 2. User Login
```
POST /auth/signin
{
  "email": "user@example.com",
  "password": "password123"
}
```

**What happens:**
1. Authenticates user with Supabase Auth
2. Returns JWT token for API access

### 3. Authenticated Requests
All protected endpoints require the `Authorization: Bearer <token>` header.

## User Profile Management

### Complete Skin Profile Form
After signup, users should complete their skin profile:

```
POST /skin-profile
Authorization: Bearer <token>
{
  "skin_type": "dry",
  "skin_tone": "medium", 
  "acne_severity": "mild",
  "pore_size": "medium",
  "sensitivity_level": "moderate",
  "primary_concerns": ["acne", "hyperpigmentation"],
  "pre_existing_conditions": ["eczema"],
  "allergies": ["fragrance", "alcohol"],
  "diet_type": "vegetarian",
  "water_intake": "moderate",
  "sleep_hours": "6-8",
  "sun_exposure": "moderate",
  "routine_frequency": "daily",
  "routine_type": "standard",
  "skin_goals": ["clear_skin", "even_tone"]
}
```

## Enhanced Product Recommendations

The system now provides personalized recommendations by:

1. **Analyzing user's skin profile** for compatibility
2. **Checking for allergies** and filtering out problematic products
3. **Considering sensitivity level** for gentle vs. strong products
4. **Scoring products** based on user's specific needs

### Example Enhanced Recommendation Logic:
- If user has `sensitivity_level: "high"` → prioritize fragrance-free products
- If user has `allergies: ["alcohol"]` → filter out products containing alcohol
- If user has `skin_type: "dry"` → boost moisturizer recommendations

## API Endpoints Summary

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/signin` - Login user
- `POST /auth/signout` - Logout user
- `POST /auth/reset-password` - Reset password
- `GET /auth/me` - Get current user info

### Profile Management
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `POST /skin-profile` - Create/update skin profile
- `GET /skin-profile` - Get skin profile
- `GET /images` - Get user images
- `DELETE /images/{image_id}` - Delete user image

### Analysis (All require authentication)
- `POST /analyze-skin` - Analyze skin conditions
- `POST /search-products` - Search products
- `POST /generate-routine` - Generate skincare routine

## Security Features

### Row Level Security (RLS)
All tables have RLS enabled, ensuring users can only access their own data.

### JWT Authentication
- Tokens expire after 24 hours
- All protected endpoints require valid tokens
- Automatic token validation middleware

### Data Validation
- Pydantic models validate all request data
- Database operations include error handling
- Input sanitization for security

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file with your Supabase credentials (already configured in your files).

### 3. Run the Backend
```bash
python main.py
```

### 4. Test Authentication
```bash
# Register a user
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Use the returned token for authenticated requests
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <your-token>"
```

## Frontend Integration

### 1. Store Authentication Token
After successful login, store the token in localStorage or a secure cookie.

### 2. Include Token in Requests
```javascript
const token = localStorage.getItem('auth_token');

fetch('/api/analyze-skin', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: formData
});
```

### 3. Handle Authentication Errors
Implement token refresh logic and redirect to login on 401 errors.

## Database Operations

### Creating User Profile
```python
# Automatically handled during signup
profile_result = await db_manager.create_profile(
    user_id=user.id,
    email=request.email,
    username=request.username
)
```

### Getting Skin Profile
```python
skin_profile_result = await db_manager.get_skin_profile(user_id)
if skin_profile_result["success"]:
    profile = skin_profile_result["data"]
```

### Updating Profile
```python
update_result = await db_manager.update_skin_profile(
    user_id, 
    {"skin_type": "oily", "sensitivity_level": "low"}
)
```

## Error Handling

All database operations return structured responses:
```python
{
    "success": True/False,
    "data": {...},  # or None
    "error": "error message"  # if success is False
}
```

## Next Steps

1. **Test the integration** with the provided endpoints
2. **Implement frontend authentication** using the API
3. **Add more product data** to enhance recommendations
4. **Consider adding analysis history** tracking
5. **Implement image upload** to Supabase Storage (optional)

## Troubleshooting

### Common Issues:
1. **"Invalid credentials"** - Check Supabase keys in config.py
2. **"User profile not found"** - Ensure profile creation during signup
3. **"Token expired"** - Implement token refresh logic
4. **"RLS policy violation"** - Check Supabase RLS policies

### Debug Mode:
Set `DEBUG=True` in your .env file for detailed error messages.

## Support

For issues with:
- **Supabase setup** - Check Supabase dashboard and documentation
- **Authentication** - Verify JWT configuration and token handling
- **Database operations** - Check RLS policies and table permissions
- **API endpoints** - Use the built-in Swagger UI at `/docs`
