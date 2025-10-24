#!/usr/bin/env python3
"""
Test script for face scan analysis endpoint
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

def test_face_scan():
    """Test the face scan analysis endpoint"""
    print("🧪 Testing face scan analysis endpoint...")
    
    # Create test images
    test_images = []
    for i in range(3):  # Test with 3 images
        img_data = create_test_image()
        test_images.append(('files', (f'test_{i}.jpg', img_data, 'image/jpeg')))
    
    # Prepare headers
    headers = {
        'Authorization': 'Bearer test-token'
    }
    
    try:
        # Make request
        print(f"📤 Sending request with {len(test_images)} images...")
        response = requests.post(
            'http://localhost:8000/analyze-skin-multi-angle',
            headers=headers,
            files=test_images,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_face_scan()
