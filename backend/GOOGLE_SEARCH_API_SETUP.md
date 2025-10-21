# Google Custom Search API Setup Guide

## Overview

This guide will help you set up the Google Custom Search API to find real skincare products for detected skin conditions in the Dermalens application.

## Prerequisites

- Google Account
- Google Cloud Console access
- Dermalens backend already set up

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Dermalens-Product-Search")
4. Click "Create"

## Step 2: Enable Custom Search API

1. In your Google Cloud Project, go to **APIs & Services** → **Library**
2. Search for "**Custom Search API**"
3. Click on it and press "**Enable**"

## Step 3: Create API Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click "**Create Credentials**" → "**API key**"
3. Your API key will be generated (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
4. **Copy this key** - you'll need it for the `.env` file
5. (Optional but recommended) Click "Restrict Key" and:
   - Under "API restrictions", select "Restrict key"
   - Check only "Custom Search API"
   - Click "Save"

## Step 4: Create a Custom Search Engine

1. Go to [Google Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all)
2. Click "**Add**" or "**Create**"
3. Fill in the following:
   - **Search engine name**: Dermalens Skincare Product Search
   - **What to search**: 
     - Select "Search the entire web"
     - OR add specific sites (recommended):
       ```
       www.sephora.com
       www.ulta.com
       www.dermstore.com
       www.cultbeauty.com
       www.lookfantastic.com
       www.beautylish.com
       www.skinstore.com
       www.amazon.com/beauty
       ```
4. Click "**Create**"
5. On the next page, find your **Search engine ID** (looks like: `a1b2c3d4e5f6g7h8i`)
6. **Copy this ID** - you'll need it for the `.env` file

### Optional: Configure Search Engine Settings

1. In your search engine settings, you can:
   - Enable "Image search" for product images
   - Enable "SafeSearch" to filter inappropriate content
   - Add more sites to search
   - Set search language and region

## Step 5: Configure Your Backend

### Update `.env` file

Add these lines to your `backend/.env` file:

```env
# Google Custom Search API Configuration
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  # Your API key from Step 3
GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5f6g7h8i  # Your Search Engine ID from Step 4
GOOGLE_SEARCH_ENABLED=True  # Set to True to enable Google Search
GOOGLE_SEARCH_MAX_RESULTS=10
GOOGLE_SEARCH_SAFE_SEARCH=active
GOOGLE_SEARCH_COUNTRY=us
GOOGLE_SEARCH_LANGUAGE=en
```

### Install Required Dependencies

```bash
cd backend
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Step 6: Test Your Setup

Create a test script or use Python directly:

```python
from google_search_service import google_search_service

# Check if service is enabled
print(f"Google Search enabled: {google_search_service.is_enabled()}")

# Search for products
results = google_search_service.search_products("moisturizer for dry skin")

if results["success"]:
    print(f"Found {results['total_results']} products:")
    for product in results["products"]:
        print(f"- {product['name']}")
        print(f"  URL: {product['url']}")
        print(f"  Score: {product.get('relevance_score', 'N/A')}")
else:
    print(f"Error: {results['error']}")
```

## API Usage Limits

### Free Tier
- **100 queries per day** for free
- After that, you'll need to enable billing

### Paid Tier (if needed)
- First 100 queries/day: Free
- Additional queries: $5 per 1,000 queries
- Up to 10,000 queries per day

**For Dermalens:**
- Average 5-10 searches per skin analysis
- ~10-20 users per day = 50-200 searches
- Well within free tier limits!

## Configuration Options

### Search Settings

In your `.env` file, you can configure:

```env
# Maximum results per search (1-10)
GOOGLE_SEARCH_MAX_RESULTS=10

# SafeSearch level: off, active, high
GOOGLE_SEARCH_SAFE_SEARCH=active

# Country code: us, uk, ca, au, etc.
GOOGLE_SEARCH_COUNTRY=us

# Language: en, es, fr, de, etc.
GOOGLE_SEARCH_LANGUAGE=en
```

## How It Works in Dermalens

### 1. Skin Analysis Flow

When a user uploads an image:
```
User uploads image
  ↓
AI detects skin conditions (e.g., "acne", "hyperpigmentation")
  ↓
Google Search API searches for products:
  - "skincare products for acne"
  - "skincare products for hyperpigmentation"
  ↓
Results are filtered by user's allergies
  ↓
Products are ranked and deduplicated
  ↓
Top recommendations shown to user
```

### 2. Search Query Building

The system automatically builds optimized queries:
```python
# Basic search
"skincare products for acne"

# With user profile
"skincare products for acne fragrance-free"

# With filters
"CeraVe acne cleanser"
```

### 3. Result Processing

Each search result includes:
- Product name and description
- URL to product page
- Product image (if available)
- Price (if available from structured data)
- Brand name
- Relevance score
- Ratings (if available)

## Troubleshooting

### "Google Custom Search API is not enabled"

**Solution:**
1. Check that `GOOGLE_SEARCH_ENABLED=True` in `.env`
2. Verify API key and Search Engine ID are correct
3. Ensure Custom Search API is enabled in Google Cloud Console

### "API key not valid"

**Solutions:**
1. Check that you copied the API key correctly
2. Verify the API key has Custom Search API enabled
3. Check if API key restrictions are blocking your requests
4. Create a new API key if needed

### "Search engine ID not found"

**Solutions:**
1. Verify you copied the Search Engine ID correctly
2. Make sure the search engine is active in Programmable Search Engine console
3. Check that you're using the correct search engine

### "Quota exceeded"

**Solutions:**
1. You've hit the 100 queries/day free limit
2. Enable billing in Google Cloud Console for additional queries
3. Or wait until the next day for quota reset

### No results found

**Solutions:**
1. Try broadening your search query
2. Add more websites to your search engine configuration
3. Check if SafeSearch is too restrictive

## Best Practices

### 1. Query Optimization
```python
# Good queries
"CeraVe moisturizer for dry skin"
"The Ordinary niacinamide for acne"
"La Roche-Posay sunscreen SPF 50"

# Poor queries  
"stuff for skin"
"good product"
```

### 2. Caching Results
Consider caching search results to reduce API calls:
```python
# Cache popular searches
# Cache results for 24 hours
# Use database or Redis for caching
```

### 3. Fallback Strategy
Always have fallback mock data if Google Search is disabled:
```python
if not google_search_service.is_enabled():
    # Use mock product database
    products = get_mock_products(conditions)
```

### 4. Monitor Usage
- Check Google Cloud Console for API usage
- Set up billing alerts
- Monitor query patterns

## Integration with Main Application

The Google Search service is already integrated with your backend:

### In `main.py`:

```python
from google_search_service import google_search_service

@app.post("/analyze-skin")
async def analyze_skin(file, current_user_id):
    # ... skin analysis ...
    
    # Search for real products
    if google_search_service.is_enabled():
        search_results = google_search_service.search_products_for_conditions(
            conditions=detected_conditions,
            user_profile=user_skin_profile
        )
        products = search_results["recommended_products"]
    else:
        # Fallback to mock data
        products = search_products(detected_conditions)
    
    return {"products": products, ...}
```

## Testing

### Test Script

Create `backend/test_google_search.py`:

```python
from google_search_service import google_search_service

def test_google_search():
    print("Testing Google Custom Search API...")
    print(f"Enabled: {google_search_service.is_enabled()}")
    
    if not google_search_service.is_enabled():
        print("❌ Google Search is not enabled")
        return
    
    # Test single search
    print("\n1. Testing single product search...")
    results = google_search_service.search_products(
        query="CeraVe moisturizer",
        skin_condition="dry skin"
    )
    
    if results["success"]:
        print(f"✅ Found {results['total_results']} products")
        for p in results["products"][:3]:
            print(f"   - {p['name']}")
    else:
        print(f"❌ Error: {results['error']}")
    
    # Test multi-condition search
    print("\n2. Testing multi-condition search...")
    results = google_search_service.search_products_for_conditions(
        conditions=["acne", "dry skin"]
    )
    
    if results["success"]:
        print(f"✅ Found {results['total_products']} unique products")
    else:
        print(f"❌ Error: {results['error']}")

if __name__ == "__main__":
    test_google_search()
```

Run it:
```bash
python test_google_search.py
```

## Security Considerations

1. **Never commit API keys to Git**
   - Always use `.env` file
   - Add `.env` to `.gitignore`

2. **Use API key restrictions**
   - Restrict to specific APIs
   - Set HTTP referrer restrictions if needed
   - Consider IP restrictions for production

3. **Monitor for abuse**
   - Set up billing alerts
   - Monitor unusual usage patterns
   - Implement rate limiting in your application

## Next Steps

Once the API is set up:

1. ✅ Test with the provided test script
2. ✅ Verify products are being found
3. ✅ Start the backend server
4. ✅ Test the `/analyze-skin` endpoint
5. 🎨 Build frontend to display real products!

## Support

For issues:
- **API errors**: Check Google Cloud Console logs
- **Search issues**: Review Programmable Search Engine console
- **Integration issues**: Check backend logs with `DEBUG=True`

## Resources

- [Google Custom Search API Documentation](https://developers.google.com/custom-search/v1/overview)
- [Programmable Search Engine](https://programmablesearchengine.google.com/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Pricing](https://developers.google.com/custom-search/v1/overview#pricing)

---

**Your Google Custom Search API is now ready to find real skincare products!** 🎉

Once you provide your API key and Search Engine ID, Dermalens will search for actual products from major retailers instead of using mock data.

