#!/usr/bin/env python3
"""
Basic test for face scan analysis endpoint - no numpy dependencies
"""
import requests
import json

def test_basic():
    """Test the basic endpoint"""
    print("🧪 Testing basic endpoint...")
    
    try:
        response = requests.post(
            'http://localhost:8000/test-analyze-skin-multi-angle',
            timeout=10
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Basic test successful!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Basic test failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Basic test error: {e}")

if __name__ == "__main__":
    test_basic()
