"""
Test script to debug import issues
"""
import sys
import os

print("🔍 Testing imports...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    print("\n1. Testing basic imports...")
    import fastapi
    print("✅ FastAPI imported")
    
    print("\n2. Testing config import...")
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'config'))
    from settings import GOOGLE_CLOUD_PROJECT
    print("✅ Config imported")
    
    print("\n3. Testing AI service imports...")
    from ai.vertex_ai_service import vertex_ai_service
    print("✅ Vertex AI service imported")
    
    print("\n4. Testing other services...")
    from ai.enhanced_comprehensive_analysis_service import enhanced_comprehensive_analysis_service
    print("✅ Enhanced analysis service imported")
    
    from infrastructure.caching import intelligent_caching_service
    print("✅ Caching service imported")
    
    print("\n🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

