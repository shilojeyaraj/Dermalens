# Why main.py Breaks But minimal_main.py Works

## 🔍 **Root Cause**

The `main.py` file **CRASHES SILENTLY** when importing AI services that depend on numpy. The crash happens because:

### **The Problem Chain:**
1. `main.py` imports `vertex_ai_service`
2. `vertex_ai_service` imports numpy, PIL, and Google Cloud libraries  
3. **Numpy crashes** due to experimental MINGW build on Windows + Python 3.13
4. The crash is SILENT - no error message, just termination
5. Only the numpy warnings are printed before the crash

### **Why minimal_main.py Works:**
- **Zero dependencies** on AI services
- No numpy imports
- Only uses FastAPI standard library
- No Google Cloud SDK imports

## 🔧 **What's Breaking in main.py**

### **File: `apps/api/ai/vertex_ai_service.py`**
```python
# Line 13-14: These cause the crash
import numpy as np
from PIL import Image

# Lines 18-22: These also require complex dependencies
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
from google.cloud.aiplatform.gapic.schema import predict, streaming_predict
from google.cloud import storage
from google.cloud import bigquery

# Line 25: Redis dependency
import redis.asyncio as redis
```

## ⚠️ **The Numpy Problem on Windows**

Your system has:
- **Python 3.13** (very new)
- **Windows 64-bit**
- **Numpy built with MINGW-W64** (experimental)

The warning says:
```
Warning: Numpy built with MINGW-W64 on Windows 64 bits is experimental,
and only available for testing. You are advised not to use it for production.
CRASHES ARE TO BE EXPECTED - PLEASE REPORT THEM TO NUMPY DEVELOPERS
```

After the warnings, numpy **CRASHES THE ENTIRE PYTHON PROCESS** silently.

## ✅ **Solutions**

### **Option 1: Use Minimal API (Current Workaround)**
```bash
cd apps/api
python minimal_main.py
```
- Works immediately
- No AI features
- Good for testing frontend/backend communication

### **Option 2: Downgrade Python to 3.11**
Python 3.13 is too new and has poor numpy support on Windows.

```bash
# Install Python 3.11 instead
# Then reinstall dependencies
pip install -r requirements.txt
```

### **Option 3: Use a Different Numpy Build**
```bash
pip uninstall numpy
pip install numpy==1.24.3  # Stable version for Windows
```

### **Option 4: Use WSL/Linux**
Run the API in Windows Subsystem for Linux where numpy works properly.

###  **Option 5: Create a Hybrid Version** (Recommended)
Use main.py but disable AI services temporarily:

```python
# Set these in .env
VERTEX_AI_ENABLED=False
ENSEMBLE_ENABLED=False
FEATURE_INTELLIGENT_CACHING=False
```

Then modify imports to be conditional.

## 📊 **Comparison**

| Feature | minimal_main.py | main.py (broken) |
|---------|----------------|------------------|
| **Starts** | ✅ Yes | ❌ No (crashes) |
| **Dependencies** | Minimal | Heavy |
| **AI Services** | ❌ No | ✅ Yes (if working) |
| **Database** | ❌ No | ✅ Yes |
| **Auth** | ❌ No | ✅ Yes |
| **Vertex AI** | ❌ No | ✅ Yes (if working) |
| **Production Ready** | ❌ No | ✅ Yes (on Linux) |

## 🎯 **Recommended Next Steps**

1. **Short term**: Use `minimal_main.py` for development
2. **Medium term**: Downgrade to Python 3.11
3. **Long term**: Deploy on Linux/Docker where numpy works properly

## 📝 **Technical Details**

The crash happens at:
```
apps/api/ai/vertex_ai_service.py:13
  import numpy as np
    ↓
numpy/__init__.py
    ↓
numpy/core/getlimits.py:52
  self.precision = int(-log10(self.eps))
    ↓
CRASH (invalid value in float operation)
```

The numpy MINGW build on Windows has issues with certain float operations
that cause the entire process to terminate without raising a Python exception.


