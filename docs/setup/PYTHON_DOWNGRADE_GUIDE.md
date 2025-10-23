# Python 3.13 → 3.11 Downgrade Guide

## Why Downgrade?
- Python 3.13 is too new for Windows + numpy compatibility
- Numpy crashes on Python 3.13 with MINGW build
- Python 3.11 is stable and fully compatible with all dependencies

## 📋 **Step-by-Step Instructions**

### **Step 1: Download Python 3.11**

1. Go to: https://www.python.org/downloads/release/python-3119/
2. Scroll to "Files" section
3. Download: **Windows installer (64-bit)** 
   - File: `python-3.11.9-amd64.exe`

### **Step 2: Install Python 3.11**

1. Run the installer
2. ✅ **IMPORTANT**: Check "Add Python 3.11 to PATH"
3. Click "Install Now"
4. Wait for installation to complete

### **Step 3: Verify Installation**

Open a NEW PowerShell window and run:
```powershell
python --version
```

Should show: `Python 3.11.9`

If it still shows Python 3.13:
```powershell
py -3.11 --version
```

### **Step 4: Reinstall Dependencies**

Navigate to your project:
```powershell
cd C:\Users\shilo\Dermalens\apps\api
```

Reinstall all packages with Python 3.11:
```powershell
# Option A: If python command points to 3.11
python -m pip install --upgrade pip
pip install -r requirements.txt

# Option B: If you need to use py launcher
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install -r requirements.txt
```

### **Step 5: Test the API**

```powershell
cd C:\Users\shilo\Dermalens\apps\api
python main.py
```

Should now start without numpy crashes!

## 🔄 **Alternative: Use Virtual Environment**

You can keep both Python versions and use virtual environments:

```powershell
# Create virtual environment with Python 3.11
py -3.11 -m venv venv311

# Activate it
.\venv311\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py
```

## ⚠️ **If You Need to Keep Python 3.13**

You can have both versions installed:
- Python 3.11 for this project
- Python 3.13 for other projects

Use the `py` launcher to choose:
```powershell
py -3.11 script.py  # Use Python 3.11
py -3.13 script.py  # Use Python 3.13
```

## ✅ **Success Indicators**

After downgrade, you should see:
- ✅ No numpy MINGW warnings
- ✅ API starts successfully
- ✅ All imports work
- ✅ `/health` endpoint responds

## 🆘 **Troubleshooting**

### Issue: Python still shows 3.13
**Solution**: Close and reopen PowerShell, or use `py -3.11`

### Issue: pip not found
**Solution**: `python -m pip install --upgrade pip`

### Issue: Requirements install fails
**Solution**: Install packages individually:
```powershell
pip install fastapi uvicorn
pip install numpy==1.24.3
pip install pillow
pip install google-cloud-aiplatform
```

## 📞 **Need Help?**
If you encounter any issues during downgrade, let me know which step is failing!

