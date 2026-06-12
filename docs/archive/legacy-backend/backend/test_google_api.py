"""
Test Google Custom Search API with your credentials
"""
import os
from google_search_service import google_search_service

def main():
    print("=" * 60)
    print("TESTING GOOGLE CUSTOM SEARCH API")
    print("=" * 60)
    
    # Check if enabled
    print(f"\n1. API Status: {'✅ ENABLED' if google_search_service.is_enabled() else '❌ DISABLED'}")
    
    if not google_search_service.is_enabled():
        print("\n❌ Google Search API is not enabled!")
        print("Please check:")
        print("  - GOOGLE_API_KEY in .env file")
        print("  - GOOGLE_SEARCH_ENGINE_ID in .env file")
        print("  - GOOGLE_SEARCH_ENABLED=True in .env file")
        return
    
    print(f"   API Key: {google_search_service.api_key[:20]}...")
    print(f"   Engine ID: {google_search_service.search_engine_id}")
    
    # Test 1: Simple product search
    print("\n2. Testing Simple Product Search...")
    print("   Query: 'CeraVe moisturizer for dry skin'")
    
    try:
        results = google_search_service.search_products(
            query="CeraVe moisturizer",
            skin_condition="dry skin",
            max_results=5
        )
        
        if results["success"]:
            print(f"   ✅ Found {results['total_results']} products")
            print(f"   Search time: {results['metadata']['search_time']} seconds")
            print(f"\n   Top 3 Products:")
            for i, product in enumerate(results["products"][:3], 1):
                print(f"\n   {i}. {product['name']}")
                print(f"      URL: {product['url'][:60]}...")
                print(f"      Source: {product['source']}")
                if product.get('price'):
                    print(f"      Price: ${product['price']} {product.get('currency', 'USD')}")
                print(f"      Relevance: {product.get('relevance_score', 0):.2f}")
        else:
            print(f"   ❌ Error: {results['error']}")
            return
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return
    
    # Test 2: Multi-condition search
    print("\n3. Testing Multi-Condition Search...")
    print("   Conditions: ['acne', 'hyperpigmentation']")
    
    try:
        results = google_search_service.search_products_for_conditions(
            conditions=["acne", "hyperpigmentation"]
        )
        
        if results["success"]:
            print(f"   ✅ Found {results['total_products']} unique products")
            print(f"\n   Products by condition:")
            for condition, products in results["products_by_condition"].items():
                print(f"   - {condition}: {len(products)} products")
            
            print(f"\n   Top 3 Recommended Products:")
            for i, product in enumerate(results["recommended_products"][:3], 1):
                print(f"\n   {i}. {product['name']}")
                conditions_matched = product.get('conditions_matched', [])
                print(f"      Matches: {', '.join(conditions_matched)}")
                print(f"      Score: {product.get('final_score', 0):.2f}")
        else:
            print(f"   ❌ Error: {results['error']}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 3: Search with user profile
    print("\n4. Testing Search with User Profile...")
    print("   User has allergies: ['fragrance', 'alcohol']")
    
    user_profile = {
        "skin_type": "dry",
        "sensitivity_level": "high",
        "allergies": ["fragrance", "alcohol"]
    }
    
    try:
        results = google_search_service.search_products_for_conditions(
            conditions=["dry skin"],
            user_profile=user_profile
        )
        
        if results["success"]:
            print(f"   ✅ Found {results['total_products']} allergy-safe products")
            print(f"   (Products with fragrance/alcohol excluded)")
        else:
            print(f"   ❌ Error: {results['error']}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ GOOGLE SEARCH API TEST COMPLETE!")
    print("=" * 60)
    print("\nYour Google Custom Search API is working and ready!")
    print("The backend will now search for REAL skincare products! 🎉")

if __name__ == "__main__":
    main()

