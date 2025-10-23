# Google Custom Search API Configuration for Product Images

## Current Issue
- Products showing 404 errors for images
- Need to fetch real product images from the web
- Should search multiple brands (CeraVe, The Ordinary, Neutrogena, etc.)

## Solution: Configure Google Custom Search

### Step 1: Update Your Search Engine Settings

1. **Go to:** https://programmablesearchengine.google.com/
2. **Sign in** with your Google account
3. **Find your search engine ID:** `96653b7de4a3d49fe`
4. **Click "Edit"**

### Step 2: Enable Image Search

In the search engine settings:

1. **Basic Tab:**
   - Name: "Skincare Products Search"
   - What to search: **"Search the entire web"** (not specific sites)
   - SafeSearch: ON

2. **Setup → Basics:**
   - Enable "Image search"
   - Enable "Search the entire web"

3. **Look and Feel:**
   - Can customize if needed

### Step 3: Update Backend Code

The backend already supports image search, but let me verify it's fetching images:

```python
# In google_search_service.py
def search_products(self, query: str, max_results: int = 10):
    # Should include searchType='image' for image results
    # Or parse image URLs from regular search results
```

### Step 4: API Configuration

Your current `.env` has:
```
GOOGLE_API_KEY=AIzaSyAtT3Jon9cWkbfnNLR91F9J810vvjzu8JY
GOOGLE_SEARCH_ENGINE_ID=96653b7de4a3d49fe
```

These are correct! The issue is the search needs to:
1. Return product images
2. Extract image URLs from results
3. Pass them to the frontend

## Alternative: Use Direct Image URLs

If Google Search doesn't return good images, we can:

### Option A: Use Placeholder Images
Create placeholder images in `frontend/public/products/`:
- default-cleanser.jpg
- default-serum.jpg
- default-moisturizer.jpg
- etc.

### Option B: Use Free Stock Photos
From Unsplash or similar:
```typescript
const placeholderImages = {
  'cleanser': 'https://images.unsplash.com/photo-cleanser-bottle',
  'serum': 'https://images.unsplash.com/photo-serum-bottle',
  // etc.
}
```

### Option C: Scrape Brand Websites
Configure Google Search to specifically search:
- cerave.com
- theordinary.com
- neutrogena.com
- laroche-posay.com
- etc.

## Recommended Approach

### For Now (Quick Fix):
Use placeholder images in the products data:

```typescript
const products = [
  {
    name: "CeraVe Hydrating Cleanser",
    image: "/placeholder-cleanser.jpg", // Generic placeholder
    price: "$14.99",
    brand: "CeraVe"
  }
]
```

### For Production (Best Solution):
1. **Configure Google Custom Search** to search entire web
2. **Modify backend** to extract image URLs from search results:

```python
def search_products_with_images(self, query: str):
    # Regular search
    results = self.service.cse().list(
        q=query,
        cx=self.search_engine_id,
        num=10
    ).execute()
    
    # For each result, try to get product image
    for item in results.get('items', []):
        # Check if pagemap has images
        if 'pagemap' in item and 'cse_image' in item['pagemap']:
            image_url = item['pagemap']['cse_image'][0]['src']
            item['image'] = image_url
    
    return results
```

3. **Or use Google Image Search API**:
```python
# Separate image search
def get_product_image(self, product_name: str):
    results = self.service.cse().list(
        q=product_name,
        cx=self.search_engine_id,
        searchType='image',
        num=1
    ).execute()
    
    if 'items' in results:
        return results['items'][0]['link']
    return None
```

## Quick Action Items

1. ✅ **Frontend is working** - Just missing images
2. ⚠️ **Google Search Engine** - Update to "Search entire web" + enable images
3. ⚠️ **Backend** - Modify to extract/return image URLs
4. 💡 **Temporary** - Use placeholder images until API returns real ones

## For Your Question:

**Do you need a new search engine?**
- **NO** - Your current one (`96653b7de4a3d49fe`) is fine!
- **Just update its settings** to:
  - Search entire web (not specific sites)
  - Enable image search
  - Include multiple domains

**The API key you have is already working!** We just need to:
1. Configure the search engine properly
2. Update backend to extract image URLs from results
3. Pass those URLs to the frontend

Would you like me to:
1. Create placeholder images for now?
2. Update the backend to better extract product images?
3. Both?

