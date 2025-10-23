# Real Product Search System Upgrade Guide

## Overview
This guide outlines the steps to upgrade Dermalens from placeholder products to a comprehensive real product search system that fetches actual skincare products with images, reviews, prices, and detailed information using Google Search APIs.

## Current Status
- ✅ Created `real_product_search_service.py` with comprehensive product search functionality
- ✅ Updated `main.py` to use the new real product search service
- ✅ Added Google Search Engine ID configuration
- 🔄 **Next Steps**: Complete implementation and testing

## Implementation Steps

### 1. Google Custom Search Engine Setup

#### 1.1 Create Google Custom Search Engine
1. Go to [Google Custom Search Engine](https://cse.google.com/cse/)
2. Click "Add" to create a new search engine
3. Configure search engine:
   - **Sites to search**: `*.amazon.com, *.sephora.com, *.ulta.com, *.target.com, *.walmart.com, *.cvs.com, *.walgreens.com`
   - **Language**: English
   - **Region**: United States
4. Copy the **Search Engine ID** (looks like: `96653b7de4a3d49fe`)

#### 1.2 Enable Image Search
1. In your Custom Search Engine settings
2. Go to "Setup" → "Basics"
3. Enable "Image search"
4. Set image size preference to "Medium" or "Large"

#### 1.3 Configure Search Features
1. Go to "Setup" → "Advanced"
2. Enable "SafeSearch" (set to "Active")
3. Set "Country" to "United States"
4. Set "Language" to "English"

### 2. Environment Configuration

#### 2.1 Update `.env` file
```bash
# Google Search Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
GOOGLE_SEARCH_ENABLED=True
GOOGLE_SEARCH_MAX_RESULTS=20
GOOGLE_SEARCH_SAFE_SEARCH=active
GOOGLE_SEARCH_COUNTRY=us
GOOGLE_SEARCH_LANGUAGE=en
```

#### 2.2 Update `config.py`
```python
# Add these configurations
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "your_search_engine_id")
GOOGLE_SEARCH_MAX_RESULTS = int(os.getenv("GOOGLE_SEARCH_MAX_RESULTS", "20"))
GOOGLE_SEARCH_SAFE_SEARCH = os.getenv("GOOGLE_SEARCH_SAFE_SEARCH", "active")
GOOGLE_SEARCH_COUNTRY = os.getenv("GOOGLE_SEARCH_COUNTRY", "us")
GOOGLE_SEARCH_LANGUAGE = os.getenv("GOOGLE_SEARCH_LANGUAGE", "en")
```

### 3. Enhanced Product Search Service

#### 3.1 Key Features to Implement

**A. Multi-Source Product Discovery**
- Amazon product pages
- Sephora product listings
- Ulta Beauty products
- Target beauty section
- CVS/Walgreens pharmacy products
- Brand websites (CeraVe, The Ordinary, etc.)

**B. Product Data Extraction**
- Product names and brands
- Real prices (with currency detection)
- High-quality product images
- Customer ratings and review counts
- Product descriptions
- Ingredient lists
- Size/volume information
- Availability status

**C. Smart Search Queries**
```python
# Example search strategies
search_queries = [
    f"{condition} {product_type} site:amazon.com",
    f"{brand} {condition} {product_type} site:sephora.com",
    f"best {condition} treatment {product_type} 2024",
    f"{condition} skincare {product_type} reviews",
    f"dermatologist recommended {condition} {product_type}"
]
```

#### 3.2 Advanced Product Parsing

**A. Price Extraction Patterns**
```python
price_patterns = [
    r'\$(\d+\.?\d*)',  # $19.99
    r'(\d+\.?\d*)\s*dollars?',  # 19.99 dollars
    r'USD\s*(\d+\.?\d*)',  # USD 19.99
    r'Price:\s*\$?(\d+\.?\d*)',  # Price: $19.99
    r'From\s*\$(\d+\.?\d*)',  # From $19.99
    r'Starting at\s*\$(\d+\.?\d*)'  # Starting at $19.99
]
```

**B. Rating Extraction Patterns**
```python
rating_patterns = [
    r'(\d+\.?\d*)\s*stars?',  # 4.5 stars
    r'rating:\s*(\d+\.?\d*)',  # rating: 4.5
    r'(\d+\.?\d*)\s*\/\s*5',  # 4.5/5
    r'(\d+\.?\d*)\s*out\s*of\s*5',  # 4.5 out of 5
    r'★\s*(\d+\.?\d*)',  # ★ 4.5
    r'⭐\s*(\d+\.?\d*)'  # ⭐ 4.5
]
```

**C. Review Count Extraction**
```python
review_patterns = [
    r'(\d+)\s*reviews?',  # 150 reviews
    r'(\d+)\s*ratings?',  # 150 ratings
    r'(\d+)\s*customers?',  # 150 customers
    r'(\d+)\s*verified\s*purchases?',  # 150 verified purchases
    r'(\d+)\s*user\s*reviews?'  # 150 user reviews
]
```

### 4. Product Data Enhancement

#### 4.1 Product Categorization
```python
def categorize_product(title, description, query):
    """Smart product categorization"""
    text = f"{title} {description} {query}".lower()
    
    categories = {
        'Cleanser': ['cleanser', 'face wash', 'cleansing', 'wash', 'foam'],
        'Moisturizer': ['moisturizer', 'cream', 'lotion', 'hydrating', 'hydrate'],
        'Serum': ['serum', 'treatment', 'concentrate', 'essence'],
        'Sunscreen': ['sunscreen', 'spf', 'sun protection', 'uv', 'sunblock'],
        'Toner': ['toner', 'astringent', 'freshener', 'mist'],
        'Exfoliant': ['exfoliant', 'scrub', 'peel', 'acid', 'aha', 'bha'],
        'Eye Cream': ['eye cream', 'eye treatment', 'eye serum', 'eye gel'],
        'Face Mask': ['mask', 'treatment mask', 'clay mask', 'sheet mask'],
        'Treatment': ['treatment', 'spot treatment', 'corrector', 'repair']
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    return 'Treatment'
```

#### 4.2 Ingredient Analysis
```python
def extract_ingredients(description, category):
    """Extract key ingredients from product description"""
    common_ingredients = {
        'Hyaluronic Acid': ['hyaluronic acid', 'sodium hyaluronate'],
        'Retinol': ['retinol', 'retinoid', 'retinyl palmitate'],
        'Vitamin C': ['vitamin c', 'ascorbic acid', 'l-ascorbic acid'],
        'Niacinamide': ['niacinamide', 'vitamin b3'],
        'Ceramides': ['ceramides', 'ceramide'],
        'Peptides': ['peptides', 'palmitoyl pentapeptide'],
        'Salicylic Acid': ['salicylic acid', 'bha'],
        'Glycolic Acid': ['glycolic acid', 'aha'],
        'Benzoyl Peroxide': ['benzoyl peroxide'],
        'Zinc Oxide': ['zinc oxide'],
        'Titanium Dioxide': ['titanium dioxide']
    }
    
    found_ingredients = []
    description_lower = description.lower()
    
    for ingredient, variations in common_ingredients.items():
        if any(var in description_lower for var in variations):
            found_ingredients.append(ingredient)
    
    return found_ingredients[:5]  # Top 5 ingredients
```

#### 4.3 Skin Type Detection
```python
def detect_skin_type(title, description, query):
    """Detect recommended skin type from product info"""
    text = f"{title} {description} {query}".lower()
    
    skin_type_indicators = {
        'Oily': ['oily', 'oil control', 'matte', 'non-comedogenic'],
        'Dry': ['dry', 'hydrating', 'moisturizing', 'nourishing'],
        'Sensitive': ['sensitive', 'gentle', 'fragrance-free', 'hypoallergenic'],
        'Combination': ['combination', 'normal to oily', 'normal to dry'],
        'Normal': ['normal', 'all skin types', 'universal']
    }
    
    for skin_type, indicators in skin_type_indicators.items():
        if any(indicator in text for indicator in indicators):
            return skin_type
    
    return 'All Skin Types'
```

### 5. Frontend Integration

#### 5.1 Enhanced Product Cards
```typescript
interface RealProduct {
  name: string;
  brand: string;
  price: string;
  originalPrice?: string;
  category: string;
  description: string;
  rating: number;
  reviewCount: number;
  imageUrl: string;
  productUrl: string;
  source: string;
  inStock: boolean;
  size: string;
  ingredients: string[];
  skinType: string;
  keyBenefits: string[];
  discount?: string;
  isNew?: boolean;
  isBestSeller?: boolean;
}
```

#### 5.2 Product Grid Component
```typescript
const ProductCard = ({ product }: { product: RealProduct }) => (
  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
    {/* Product Image */}
    <div className="relative h-48 bg-gray-100">
      <img 
        src={product.imageUrl} 
        alt={product.name}
        className="w-full h-full object-cover"
        onError={(e) => {
          e.currentTarget.src = '/placeholder-product.jpg';
        }}
      />
      
      {/* Badges */}
      <div className="absolute top-2 left-2 flex flex-col gap-1">
        {product.isNew && <Badge className="bg-green-500">New</Badge>}
        {product.isBestSeller && <Badge className="bg-orange-500">Best Seller</Badge>}
        {product.discount && <Badge className="bg-red-500">{product.discount}</Badge>}
      </div>
      
      {/* Wishlist Button */}
      <button className="absolute top-2 right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md hover:bg-gray-50">
        <Heart className="w-4 h-4 text-gray-600" />
      </button>
    </div>
    
    {/* Product Details */}
    <div className="p-4">
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
        {product.brand}
      </div>
      
      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
        {product.name}
      </h3>
      
      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {product.description}
      </p>
      
      {/* Rating */}
      <div className="flex items-center mb-3">
        <div className="flex items-center">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star 
              key={star} 
              className={`w-4 h-4 ${
                star <= Math.floor(product.rating) 
                  ? 'text-yellow-400 fill-current' 
                  : 'text-gray-300'
              }`} 
            />
          ))}
        </div>
        <span className="text-sm text-gray-600 ml-2">
          {product.rating} ({product.reviewCount} reviews)
        </span>
      </div>
      
      {/* Price */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-green-600">
            {product.price}
          </span>
          {product.originalPrice && (
            <span className="text-sm text-gray-500 line-through">
              {product.originalPrice}
            </span>
          )}
        </div>
        <div className="text-xs font-semibold text-gray-500 bg-gray-200 px-2 py-1 rounded">
          {product.category}
        </div>
      </div>
      
      {/* Key Benefits */}
      <div className="mb-4">
        <div className="text-xs font-semibold text-gray-700 mb-1">Key Benefits:</div>
        <div className="flex flex-wrap gap-1">
          {product.keyBenefits.slice(0, 2).map((benefit, idx) => (
            <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {benefit}
            </span>
          ))}
        </div>
      </div>
      
      {/* Ingredients */}
      <div className="mb-4">
        <div className="text-xs font-semibold text-gray-700 mb-1">Key Ingredients:</div>
        <div className="flex flex-wrap gap-1">
          {product.ingredients.slice(0, 3).map((ingredient, idx) => (
            <span key={idx} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
              {ingredient}
            </span>
          ))}
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2">
          Add to Routine
        </Button>
        <Button variant="outline" className="px-3">
          <ExternalLink className="w-4 h-4" />
        </Button>
      </div>
    </div>
  </div>
);
```

### 6. API Endpoints Enhancement

#### 6.1 New Endpoints
```python
@app.get("/products/search")
async def search_products(
    q: str = Query(..., description="Search query"),
    category: str = Query(None, description="Product category filter"),
    brand: str = Query(None, description="Brand filter"),
    min_price: float = Query(None, description="Minimum price"),
    max_price: float = Query(None, description="Maximum price"),
    skin_type: str = Query(None, description="Skin type filter"),
    rating_min: float = Query(None, description="Minimum rating"),
    limit: int = Query(20, description="Number of results")
):
    """Search for real skincare products with filters"""
    pass

@app.get("/products/{product_id}")
async def get_product_details(product_id: str):
    """Get detailed information about a specific product"""
    pass

@app.get("/products/trending")
async def get_trending_products():
    """Get trending skincare products"""
    pass

@app.get("/products/categories")
async def get_product_categories():
    """Get available product categories"""
    pass
```

### 7. Caching and Performance

#### 7.1 Redis Caching
```python
import redis
import json
from datetime import timedelta

# Cache product search results
def cache_search_results(query: str, results: List[Dict], ttl: int = 3600):
    """Cache search results for 1 hour"""
    cache_key = f"search:{hash(query)}"
    redis_client.setex(cache_key, ttl, json.dumps(results))

def get_cached_results(query: str) -> List[Dict]:
    """Get cached search results"""
    cache_key = f"search:{hash(query)}"
    cached = redis_client.get(cache_key)
    return json.loads(cached) if cached else None
```

#### 7.2 Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze-skin")
@limiter.limit("10/minute")  # 10 requests per minute
async def analyze_skin(request: Request, ...):
    """Rate limited skin analysis"""
    pass
```

### 8. Testing and Validation

#### 8.1 Unit Tests
```python
def test_product_search():
    """Test product search functionality"""
    service = RealProductSearchService(api_key, search_engine_id)
    results = await service.search_skincare_products(['acne'], 'oily')
    
    assert len(results) > 0
    assert all('name' in product for product in results)
    assert all('price' in product for product in results)
    assert all('image_url' in product for product in results)

def test_price_extraction():
    """Test price extraction from text"""
    service = RealProductSearchService(api_key, search_engine_id)
    
    test_cases = [
        ("$19.99", 19.99),
        ("Price: $25.50", 25.50),
        ("From $15.00", 15.00),
        ("Starting at $30", 30.00)
    ]
    
    for text, expected in test_cases:
        result = service._extract_price(text, "")
        assert result == f"${expected:.2f}"
```

#### 8.2 Integration Tests
```python
def test_end_to_end_product_search():
    """Test complete product search flow"""
    # Test API endpoint
    response = client.post("/analyze-skin", files={"file": test_image})
    assert response.status_code == 200
    
    data = response.json()
    assert "recommended_products" in data
    assert len(data["recommended_products"]) > 0
    
    # Verify product data structure
    product = data["recommended_products"][0]
    required_fields = ["name", "brand", "price", "image_url", "rating"]
    assert all(field in product for field in required_fields)
```

### 9. Monitoring and Analytics

#### 9.1 Search Analytics
```python
# Track search performance
def log_search_metrics(query: str, results_count: int, response_time: float):
    """Log search performance metrics"""
    logger.info(f"Search: {query}, Results: {results_count}, Time: {response_time}ms")
    
    # Send to analytics service
    analytics.track("product_search", {
        "query": query,
        "results_count": results_count,
        "response_time": response_time
    })
```

#### 9.2 Error Monitoring
```python
import sentry_sdk

def handle_search_error(error: Exception, query: str):
    """Handle and log search errors"""
    logger.error(f"Search error for '{query}': {str(error)}")
    
    # Send to error monitoring
    sentry_sdk.capture_exception(error)
    
    # Return fallback results
    return get_fallback_products(query)
```

### 10. Deployment Checklist

#### 10.1 Environment Setup
- [ ] Google Custom Search Engine created and configured
- [ ] Google API key with Custom Search API enabled
- [ ] Search Engine ID added to environment variables
- [ ] Redis instance configured for caching
- [ ] Rate limiting configured

#### 10.2 Code Deployment
- [ ] `real_product_search_service.py` deployed
- [ ] Updated `main.py` with new search function
- [ ] Frontend components updated for real product data
- [ ] API endpoints tested and working
- [ ] Caching layer implemented

#### 10.3 Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Load testing completed
- [ ] Error handling tested
- [ ] Fallback mechanisms working

### 11. Future Enhancements

#### 11.1 Advanced Features
- **Price Comparison**: Compare prices across multiple retailers
- **Product Reviews**: Aggregate reviews from multiple sources
- **Stock Availability**: Real-time inventory checking
- **Price Alerts**: Notify users of price drops
- **Wishlist**: Save products for later
- **Product Recommendations**: AI-powered suggestions

#### 11.2 Machine Learning Integration
- **Product Similarity**: Find similar products using ML
- **Price Prediction**: Predict price trends
- **Review Sentiment**: Analyze review sentiment
- **Personalization**: Improve recommendations based on user behavior

#### 11.3 Additional Data Sources
- **Social Media**: Instagram, TikTok product mentions
- **Beauty Blogs**: Influencer recommendations
- **Dermatologist Reviews**: Professional opinions
- **Clinical Studies**: Scientific backing for products

## Conclusion

This upgrade will transform Dermalens from a basic skin analysis tool to a comprehensive skincare shopping platform with real products, detailed information, and professional-grade recommendations. The implementation should be done incrementally, starting with basic product search and gradually adding advanced features.

## Next Steps
1. Set up Google Custom Search Engine
2. Update environment configuration
3. Test the real product search service
4. Update frontend to display real product data
5. Implement caching and performance optimizations
6. Add comprehensive testing
7. Deploy and monitor the system
