#!/usr/bin/env python3
"""
Simple test for face scan analysis endpoint
"""
import requests
import base64
import io
from PIL import Image
import json

def create_test_image():
    """Create a simple test image"""
    # Create a simple test image
    img = Image.new('RGB', (1280, 720), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def test_simple():
    """Test the simple endpoint first"""
    print("🧪 Testing simple endpoint...")
    
    try:
        response = requests.post(
            'http://localhost:8000/test-analyze-skin-multi-angle',
            timeout=10
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simple test successful!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Simple test failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Simple test error: {e}")

def test_with_images():
    """Test with actual images"""
    print("🧪 Testing with images...")
    
    # Create test images
    test_images = []
    for i in range(3):  # Test with 3 images
        img_data = create_test_image()
        test_images.append(('files', (f'test_{i}.jpg', img_data, 'image/jpeg')))
    
    try:
        response = requests.post(
            'http://localhost:8000/test-analyze-skin-multi-angle-full',
            files=test_images,
            timeout=60
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image test successful!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Image test failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Image test error: {e}")

if __name__ == "__main__":
    test_simple()
    print("\n" + "="*50 + "\n")
    test_with_images()
