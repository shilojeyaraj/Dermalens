#!/usr/bin/env python3
"""
Test script for Gemini integration
Run this to verify everything is working correctly
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_services():
    """Test all Gemini services"""
    print("🧪 Testing Gemini Integration...")
    print("=" * 50)
    
    # Test 1: Basic Gemini Service
    print("\n1️⃣ Testing Gemini Service Initialization...")
    try:
        from gemini_analysis_service import get_gemini_service
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        gemini_service = get_gemini_service(gemini_key)
        print("✅ Gemini service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini service: {e}")
        return False
    
    # Test 2: Text Generation
    print("\n2️⃣ Testing Text Generation...")
    try:
        report_result = gemini_service.generate_personalized_report(
            user_profile={
                "skin_type": "oily",
                "concerns": ["acne", "blackheads"],
                "age": 25,
                "sensitivity_level": "moderate"
            },
            analysis_results=[],
            detected_conditions=["acne", "oily_skin"]
        )
        
        if report_result["success"]:
            print("✅ Text generation successful")
            print(f"📝 Report preview: {str(report_result['report'])[:100]}...")
        else:
            print(f"❌ Text generation failed: {report_result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Text generation error: {e}")
        return False
    
    # Test 3: Routine Generation
    print("\n3️⃣ Testing Routine Generation...")
    try:
        routine_result = gemini_service.generate_skincare_routine(
            conditions=["acne", "oily_skin"],
            products=[
                {
                    "name": "CeraVe Foaming Cleanser",
                    "brand": "CeraVe",
                    "price": 16.99,
                    "type": "cleanser"
                },
                {
                    "name": "The Ordinary Niacinamide",
                    "brand": "The Ordinary", 
                    "price": 12.90,
                    "type": "serum"
                }
            ],
            user_profile={
                "skin_type": "oily",
                "concerns": ["acne"]
            }
        )
        
        if routine_result["success"]:
            print("✅ Routine generation successful")
            print(f"📋 Routine preview: {str(routine_result['routine'])[:100]}...")
        else:
            print(f"❌ Routine generation failed: {routine_result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Routine generation error: {e}")
        return False
    
    # Test 4: Image Analysis (Mock)
    print("\n4️⃣ Testing Image Analysis (Mock)...")
    try:
        # Create a mock image (1x1 pixel)
        from PIL import Image
        import io
        
        mock_image = Image.new('RGB', (1, 1), color='red')
        img_byte_arr = io.BytesIO()
        mock_image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        analysis_result = gemini_service.analyze_skin_image(
            image_data=img_byte_arr,
            user_profile={"skin_type": "normal"}
        )
        
        if analysis_result["success"]:
            print("✅ Image analysis successful")
            print(f"🔍 Analysis preview: {str(analysis_result['analysis'])[:100]}...")
        else:
            print(f"❌ Image analysis failed: {analysis_result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
        return False
    
    # Test 5: Comprehensive Analysis Service
    print("\n5️⃣ Testing Comprehensive Analysis Service...")
    try:
        from comprehensive_analysis_service import ComprehensiveSkinAnalysisService
        
        comprehensive_service = ComprehensiveSkinAnalysisService()
        print("✅ Comprehensive analysis service initialized")
        print(f"🤖 AI service type: {type(comprehensive_service.ai).__name__}")
    except Exception as e:
        print(f"❌ Comprehensive service error: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    print("=" * 50)
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test services status
        response = requests.get("http://localhost:8000/api/services-status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Services status endpoint working")
            print(f"🔧 Gemini status: {status.get('gemini', {}).get('enabled', False)}")
        else:
            print(f"❌ Services status failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")
        print("💡 Make sure the server is running: python main.py")

def main():
    """Main test function"""
    print("🔬 Dermalens Gemini Integration Test")
    print("=" * 50)
    
    # Check environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found!")
        print("💡 Run: python setup_gemini_env.py")
        return
    
    # Run tests
    success = asyncio.run(test_gemini_services())
    
    if success:
        print("\n✅ All Gemini tests passed!")
        print("🚀 Your backend is ready to use Gemini 1.5 Pro")
        
        # Test API endpoints
        asyncio.run(test_api_endpoints())
    else:
        print("\n❌ Some tests failed!")
        print("🔧 Check your Gemini API key and configuration")

if __name__ == "__main__":
    main()
