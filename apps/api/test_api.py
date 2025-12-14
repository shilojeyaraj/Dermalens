"""
Test script for the Dermalens API
"""
import requests
import time
import subprocess
import sys
import os

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Dermalens API...")
    
    # Test endpoints
    endpoints = [
        "/",
        "/health", 
        "/test",
        "/config"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data.get('message', data.get('status', 'OK'))}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection failed - API not running")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    
    print("\n📊 Test complete!")

if __name__ == "__main__":
    test_api()
