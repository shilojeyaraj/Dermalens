# Google Custom Search API - Quick Start

## ⚡ Quick Setup (5 Minutes)

### Step 1: Get Your API Key
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "API Key"
3. Copy the key (looks like: `AIzaSy...`)

### Step 2: Get Your Search Engine ID
1. Go to: https://programmablesearchengine.google.com/controlpanel/create
2. Enter "Dermalens" as name
3. Select "Search the entire web"
4. Click "Create"
5. Copy the Search Engine ID (looks like: `a1b2c3d4e...`)

### Step 3: Add to `.env` File

Open `backend/.env` and add:

```env
GOOGLE_API_KEY=AIzaSy_YOUR_KEY_HERE
GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e_YOUR_ID_HERE
GOOGLE_SEARCH_ENABLED=True
```

### Step 4: Install Dependencies

```bash
cd backend
pip install google-api-python-client
```

### Step 5: Test It!

```bash
python
```

```python
from google_search_service import google_search_service

# Test if enabled
print(google_search_service.is_enabled())  # Should print: True

# Search for products
results = google_search_service.search_products("moisturizer for dry skin")
print(results["products"][0]["name"])  # Should show a product name
```

## ✅ You're Done!

The Google Custom Search API is now integrated. Your backend will automatically:
- Search for real skincare products
- Filter by user allergies
- Rank by relevance
- Show top recommendations

## 📊 API Limits

- **Free**: 100 searches/day
- **Paid**: $5 per 1,000 additional searches

For typical usage (10-20 users/day), the free tier is sufficient!

## 🔧 Configuration Options

All in your `.env` file:

```env
GOOGLE_SEARCH_MAX_RESULTS=10        # Results per search
GOOGLE_SEARCH_SAFE_SEARCH=active    # Filter inappropriate content
GOOGLE_SEARCH_COUNTRY=us            # Country for results
GOOGLE_SEARCH_LANGUAGE=en           # Language preference
```

## 🚨 Troubleshooting

**Not working?**
1. Check API key is correct
2. Verify Search Engine ID
3. Make sure `GOOGLE_SEARCH_ENABLED=True`
4. Enable "Custom Search API" in Google Cloud Console

**Need help?** See the full guide: `GOOGLE_SEARCH_API_SETUP.md`

## 🎯 What Happens Next

When users upload images:
1. AI detects skin conditions
2. Google Search finds real products
3. Products filtered by user allergies
4. Top recommendations displayed

**Your app now searches real skincare products from Sephora, Ulta, Dermstore, and more!** 🎉

