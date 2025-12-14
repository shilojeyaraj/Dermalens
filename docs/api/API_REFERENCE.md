# 🔬 Dermalens API Reference

## Base URL
```
Development: http://localhost:8000
Production: https://dermalens-backend-xxx-uc.a.run.app
```

## Authentication
All endpoints require authentication via Supabase JWT tokens.

```http
Authorization: Bearer your-jwt-token
```

## Core Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### 2. Services Status
```http
GET /api/services-status
```

**Response:**
```json
{
  "gemini": {
    "enabled": true,
    "model": "gemini-1.5-pro"
  },
  "elasticsearch": {
    "enabled": true,
    "index_count": 1000
  },
  "google_search": {
    "enabled": true,
    "max_results": 10
  },
  "database": {
    "connected": true,
    "tables": ["profiles", "skin_profiles", "user_images"]
  }
}
```

## Skin Analysis

### 3. Analyze Skin Image
```http
POST /analyze-skin
Content-Type: multipart/form-data
Authorization: Bearer your-token

file: [image file]
```

**Request:**
- `file`: Image file (JPEG, PNG, max 10MB)

**Response:**
```json
{
  "success": true,
  "analysis_results": [
    {
      "face_id": 0,
      "conditions": [
        {
          "condition": "acne",
          "confidence": 0.85,
          "severity": "moderate",
          "description": "Several active pimples visible on forehead and chin"
        },
        {
          "condition": "oily_skin",
          "confidence": 0.72,
          "severity": "mild",
          "description": "Visible shine in T-zone area"
        }
      ],
      "skin_type": {
        "primary": "oily",
        "secondary": ["combination"],
        "health_score": 75
      },
      "recommendations": {
        "priority_treatments": ["gentle_cleanser", "salicylic_acid_serum"],
        "ingredients_to_use": ["niacinamide", "hyaluronic_acid"],
        "ingredients_to_avoid": ["alcohol", "fragrance"],
        "general_advice": "Focus on gentle cleansing and oil control in T-zone"
      }
    }
  ],
  "detected_conditions": ["acne", "oily_skin"],
  "recommended_products": [...],
  "skincare_routine": {...},
  "ai_report": {...},
  "skin_health_score": 75,
  "faces_detected": 1,
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}
```

### 4. Comprehensive User Analysis
```http
POST /api/analyze-user-comprehensive
Content-Type: application/json
Authorization: Bearer your-token

{
  "user_id": "user_123",
  "image_id": "img_456"
}
```

**Request:**
- `user_id`: User ID (required)
- `image_id`: Specific image ID (optional, uses latest if not provided)

**Response:**
```json
{
  "success": true,
  "user_profile": {
    "username": "john_doe",
    "email": "john@example.com"
  },
  "skin_profile": {
    "skin_type": "oily",
    "concerns": ["acne", "blackheads"],
    "sensitivity_level": "moderate"
  },
  "ai_analysis": {
    "conditions_detected": ["acne", "oily_skin"],
    "skin_type": "oily",
    "recommended_ingredients": ["niacinamide", "salicylic_acid"],
    "recommended_products": ["cleanser", "serum"],
    "full_diagnosis": {...},
    "model_used": "gemini-1.5-pro"
  },
  "product_recommendations": [...],
  "personalized_routine": {...},
  "image_analyzed": {
    "id": "img_456",
    "path": "user_images/img_456.jpg",
    "uploaded_at": "2024-01-15T09:00:00Z"
  },
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}
```

## Product Search

### 5. Search Products
```http
POST /search-products
Content-Type: application/json
Authorization: Bearer your-token

{
  "conditions": ["acne", "oily_skin"],
  "skin_type": "oily",
  "price_range": {
    "min": 10,
    "max": 50
  },
  "min_rating": 4.0,
  "allergen_free": true,
  "fragrance_free": true
}
```

**Request:**
- `conditions`: Array of skin conditions to target
- `skin_type`: User's skin type
- `price_range`: Min/max price range
- `min_rating`: Minimum product rating
- `allergen_free`: Filter for allergen-free products
- `fragrance_free`: Filter for fragrance-free products

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": "sephora_12345",
      "name": "CeraVe Foaming Facial Cleanser",
      "brand": "CeraVe",
      "description": "Gentle foaming cleanser for normal to oily skin",
      "ingredients": ["Ceramides", "Hyaluronic Acid", "Niacinamide"],
      "price": 16.99,
      "rating": 4.5,
      "review_count": 1250,
      "product_type": "cleanser",
      "skin_conditions": ["acne", "oily_skin"],
      "skin_types": ["oily", "combination"],
      "url": "https://www.sephora.com/product/cerave-foaming-facial-cleanser",
      "image_url": "https://www.sephora.com/images/cerave-cleanser.jpg",
      "allergen_free": true,
      "fragrance_free": true,
      "cruelty_free": false,
      "vegan": false,
      "spf_level": null,
      "recommendation_reason": "Targets: acne, oily_skin; Perfect for oily skin; Fragrance-free for sensitive skin"
    }
  ],
  "total": 25,
  "took": 45,
  "max_score": 8.5
}
```

### 6. Get Product Recommendations
```http
POST /api/recommendations
Content-Type: application/json
Authorization: Bearer your-token

{
  "user_id": "user_123",
  "analysis_results": [...],
  "limit": 10
}
```

**Request:**
- `user_id`: User ID
- `analysis_results`: Results from skin analysis
- `limit`: Maximum number of recommendations

**Response:**
```json
{
  "success": true,
  "recommendations": [...],
  "total": 10,
  "detected_conditions": ["acne", "oily_skin"]
}
```

## User Management

### 7. Get User Profile
```http
GET /profile
Authorization: Bearer your-token
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "id": "user_123",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 8. Update User Profile
```http
PUT /profile
Content-Type: application/json
Authorization: Bearer your-token

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

### 9. Get Skin Profile
```http
GET /skin-profile
Authorization: Bearer your-token
```

**Response:**
```json
{
  "success": true,
  "skin_profile": {
    "id": "skin_123",
    "user_id": "user_123",
    "skin_type": "oily",
    "concerns": ["acne", "blackheads"],
    "sensitivity_level": "moderate",
    "allergies": ["fragrance"],
    "current_routine": ["cleanser", "moisturizer"],
    "goals": ["clear_skin", "reduce_oil"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 10. Update Skin Profile
```http
PUT /skin-profile
Content-Type: application/json
Authorization: Bearer your-token

{
  "skin_type": "combination",
  "concerns": ["acne", "dry_patches"],
  "sensitivity_level": "high",
  "allergies": ["fragrance", "alcohol"],
  "goals": ["clear_skin", "hydration"]
}
```

## Image Management

### 11. Get User Images
```http
GET /images
Authorization: Bearer your-token
```

**Response:**
```json
{
  "success": true,
  "images": [
    {
      "id": "img_456",
      "user_id": "user_123",
      "filename": "face_scan_001.jpg",
      "storage_path": "user_images/img_456.jpg",
      "bucket": "dermalens-images",
      "file_size": 1024000,
      "content_type": "image/jpeg",
      "uploaded_at": "2024-01-15T09:00:00Z"
    }
  ]
}
```

### 12. Delete User Image
```http
DELETE /images/{image_id}
Authorization: Bearer your-token
```

**Response:**
```json
{
  "success": true,
  "message": "Image deleted successfully"
}
```

## Authentication

### 13. Sign Up
```http
POST /auth/signup
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "user_123",
    "username": "john_doe",
    "email": "john@example.com"
  },
  "message": "User created successfully"
}
```

### 14. Sign In
```http
POST /auth/signin
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "user_123",
    "username": "john_doe",
    "email": "john@example.com"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 15. Sign Out
```http
POST /auth/signout
Authorization: Bearer your-token
```

**Response:**
```json
{
  "success": true,
  "message": "Signed out successfully"
}
```

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Request validation failed
- `AUTHENTICATION_ERROR` - Invalid or missing authentication
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Rate Limiting

- **General endpoints**: 100 requests per minute
- **Analysis endpoints**: 10 requests per minute
- **Search endpoints**: 60 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## Pagination

For endpoints that return lists, use query parameters:

```http
GET /search-products?page=1&limit=20&sort=rating&order=desc
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Webhooks

### Analysis Complete Webhook
```http
POST /webhooks/analysis-complete
Content-Type: application/json

{
  "user_id": "user_123",
  "analysis_id": "analysis_456",
  "status": "completed",
  "results": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## SDKs and Libraries

### Python SDK
```python
from dermalens import DermalensClient

client = DermalensClient(api_key="your-api-key")

# Analyze skin
result = client.analyze_skin("path/to/image.jpg")

# Search products
products = client.search_products(
    conditions=["acne"],
    skin_type="oily"
)
```

### JavaScript SDK
```javascript
import { DermalensClient } from '@dermalens/sdk';

const client = new DermalensClient('your-api-key');

// Analyze skin
const result = await client.analyzeSkin(imageFile);

// Search products
const products = await client.searchProducts({
  conditions: ['acne'],
  skinType: 'oily'
});
```

## Support

- **Documentation**: [https://docs.dermalens.com](https://docs.dermalens.com)
- **Status Page**: [https://status.dermalens.com](https://status.dermalens.com)
- **Support Email**: support@dermalens.com
- **GitHub Issues**: [https://github.com/dermalens/api/issues](https://github.com/dermalens/api/issues)
