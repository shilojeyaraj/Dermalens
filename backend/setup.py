#!/usr/bin/env python3
"""
Setup script for Dermalens Skin Analysis Backend
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def main():
    print("Dermalens Skin Analysis Backend Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Create necessary directories
    directories = [
        "models",
        "training_data",
        "temp_uploads",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create subdirectories for training data
    skin_conditions = [
        "acne", "hyperpigmentation", "dark_spots", "wrinkles",
        "dry_skin", "oily_skin", "sensitive_skin", "normal_skin",
        "blackheads", "whiteheads", "rosacea", "eczema"
    ]
    
    for condition in skin_conditions:
        os.makedirs(f"training_data/{condition}", exist_ok=True)
    
    print("✓ Created training data directories for all skin conditions")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Download OpenCV Haar Cascade (if needed)
    print("Checking OpenCV installation...")
    try:
        import cv2
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if os.path.exists(cascade_path):
            print("✓ OpenCV face cascade found")
        else:
            print("⚠ OpenCV face cascade not found - this may cause issues")
    except ImportError:
        print("✗ OpenCV not properly installed")
    
    # Create environment file
    env_content = """# Dermalens Backend Environment Variables
# Copy this file to .env and fill in your values

# Google Store API (if you have one)
GOOGLE_STORE_API_KEY=your_api_key_here
GOOGLE_STORE_API_URL=https://www.googleapis.com/books/v1/volumes

# Model settings
MODEL_PATH=models/skin_classifier.pth
CONFIDENCE_THRESHOLD=0.3

# API settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS settings
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("✓ Created .env.example file")
    
    # Create a simple test script
    test_script = """#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import initialize_models
    print("Testing model initialization...")
    initialize_models()
    print("✓ Models initialized successfully")
    print("✓ Backend setup is working correctly!")
except Exception as e:
    print(f"✗ Error during testing: {e}")
    sys.exit(1)
"""
    
    with open("test_setup.py", "w") as f:
        f.write(test_script)
    
    print("✓ Created test script")
    
    print("\n" + "=" * 40)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and configure your settings")
    print("2. Add training images to the training_data/[condition] folders")
    print("3. Run 'python train_model.py' to train the skin classifier")
    print("4. Run 'python main.py' to start the API server")
    print("5. Run 'python test_setup.py' to verify everything works")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
