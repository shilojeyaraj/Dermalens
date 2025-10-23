"""
Startup script for Dermalens API
"""
import subprocess
import sys
import time
import os

def start_api():
    """Start the API with proper configuration"""
    print("🚀 Starting Dermalens API...")
    print("   📁 Working directory:", os.getcwd())
    print("   🐍 Python version:", sys.version)
    
    # Check if minimal_main.py exists
    if not os.path.exists("minimal_main.py"):
        print("❌ minimal_main.py not found!")
        return False
    
    try:
        # Start the API
        print("   🌐 Starting server on http://localhost:8000")
        print("   📖 API docs will be available at http://localhost:8000/docs")
        print("   ⏹️  Press Ctrl+C to stop")
        print("-" * 50)
        
        # Run the API
        subprocess.run([sys.executable, "minimal_main.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  API stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return False

if __name__ == "__main__":
    start_api()

