#!/usr/bin/env python3
"""
Test script for the real product search service
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from real_product_search_service import get_real_product_search_service

# Direct configuration
GOOGLE_WEB_SEARCH_API_KEY = "AIzaSyAtT3Jon9cWkbfnNLR91F9J810vvjzu8JY"
GOOGLE_SEARCH_ENGINE_ID = "c0918e3def8a94b63"

async def test_product_search():
    """Test the real product search service"""
    print("🔍 Testing Real Product Search Service")
    print("=" * 50)
    
    # Check if API keys are configured
    if not GOOGLE_WEB_SEARCH_API_KEY:
        print("❌ Google API key not configured")
        return
    
    if not GOOGLE_SEARCH_ENGINE_ID:
        print("❌ Google Search Engine ID not configured")
        return
    
    print(f"✅ API Key: {GOOGLE_WEB_SEARCH_API_KEY[:10]}...")
    print(f"✅ Search Engine ID: {GOOGLE_SEARCH_ENGINE_ID}")
    print()
    
    # Initialize the service
    try:
        service = get_real_product_search_service(
            GOOGLE_WEB_SEARCH_API_KEY,
            GOOGLE_SEARCH_ENGINE_ID
        )
        print("✅ Product search service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return
    
    # Test search queries
    test_conditions = ["acne", "dry skin", "anti-aging"]
    test_skin_type = "combination"
    
    print(f"\n🔍 Testing search for conditions: {test_conditions}")
    print(f"🎯 Skin type: {test_skin_type}")
    print()
    
    try:
        # Search for products
        products = await service.search_skincare_products(
            conditions=test_conditions,
            skin_type=test_skin_type,
            limit=5
        )
        
        print(f"✅ Found {len(products)} products")
        print()
        
        # Display results
        for i, product in enumerate(products, 1):
            print(f"📦 Product {i}:")
            print(f"   Name: {product.get('name', 'N/A')}")
            print(f"   Brand: {product.get('brand', 'N/A')}")
            print(f"   Price: {product.get('price', 'N/A')}")
            print(f"   Category: {product.get('category', 'N/A')}")
            print(f"   Rating: {product.get('rating', 'N/A')}")
            print(f"   Reviews: {product.get('review_count', 'N/A')}")
            print(f"   Image: {'✅' if product.get('image_url') else '❌'}")
            print(f"   Ingredients: {', '.join(product.get('ingredients', [])[:3])}")
            print(f"   Benefits: {', '.join(product.get('key_benefits', [])[:2])}")
            print(f"   Source: {product.get('source', 'N/A')}")
            print()
        
        # Test individual extraction methods
        print("🧪 Testing extraction methods:")
        print("-" * 30)
        
        # Test price extraction
        test_text = "CeraVe Foaming Facial Cleanser - $14.99 - 4.5 stars (1,200 reviews)"
        price = service._extract_price(test_text, "")
        print(f"💰 Price extraction: '{test_text}' → {price}")
        
        # Test rating extraction
        rating = service._extract_rating(test_text, "")
        print(f"⭐ Rating extraction: '{test_text}' → {rating}")
        
        # Test review count extraction
        review_count = service._extract_review_count(test_text, "")
        print(f"📊 Review count extraction: '{test_text}' → {review_count}")
        
        # Test ingredient extraction
        description = "Contains hyaluronic acid, ceramides, and niacinamide for hydration"
        ingredients = service._extract_ingredients(description, "Cleanser")
        print(f"🧪 Ingredient extraction: '{description}' → {ingredients}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_product_search())

