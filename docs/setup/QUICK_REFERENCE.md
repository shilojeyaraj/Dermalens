# Dermalens Quick Reference Guide

## 🚀 **Quick Commands**

### **Start Development**
```bash
# Backend API
cd apps/api && python main.py

# Frontend Web App
cd apps/web && npm run dev

# Both (if you have a script)
npm run dev:all
```

### **Run Tests**
```bash
# All tests
cd tests && python -m pytest

# Specific test type
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

### **Check Health**
```bash
# API Health
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics
```

## 📁 **File Locations**

### **AI Services**
```
apps/api/ai/
├── vertex_ai_service.py              # Google Vertex AI
├── ai_recommendation_engine.py       # AI recommendations
├── gemini_analysis_service.py        # Google Gemini
├── skin_analysis_service.py          # Core analysis
└── enhanced_comprehensive_analysis_service.py  # Enhanced analysis
```

### **Infrastructure**
```
apps/api/infrastructure/
├── caching.py                        # Intelligent caching
├── elasticsearch_service.py          # Search service
├── google_search_service.py          # Google search
└── fivetran_connector.py            # Data pipeline
```

### **Web Components**
```
apps/web/components/
├── ui/                               # UI components
├── face-upload-dialog.tsx           # Face upload
├── skincare-routine-dialog.tsx      # Routine display
├── product-card.tsx                 # Product display
└── user-profile-dialog.tsx         # User profile
```

### **Configuration**
```
packages/config/
└── settings.py                       # All settings
```

## 🔍 **Find Files Quickly**

### **Looking for AI Analysis?**
- **Core**: `apps/api/ai/skin_analysis_service.py`
- **Enhanced**: `apps/api/ai/enhanced_comprehensive_analysis_service.py`
- **Vertex AI**: `apps/api/ai/vertex_ai_service.py`

### **Looking for Recommendations?**
- **AI Engine**: `apps/api/ai/ai_recommendation_engine.py`
- **Search**: `apps/api/infrastructure/elasticsearch_service.py`

### **Looking for Caching?**
- **Service**: `apps/api/infrastructure/caching.py`

### **Looking for Monitoring?**
- **Performance**: `apps/api/monitoring/performance.py`

### **Looking for Database?**
- **Connection**: `apps/api/database/connection.py`

### **Looking for Auth?**
- **Service**: `apps/api/core/auth.py`

## 📚 **Documentation**

### **Setup Guides**
- **Main Setup**: `docs/guides/SETUP_GUIDE.md`
- **Enhanced AI**: `docs/guides/ENHANCED_AI_IMPLEMENTATION_GUIDE.md`
- **Multi-Agent**: `docs/guides/MULTI_AGENT_VS_SINGLE_AGENT_GUIDE.md`

### **API Documentation**
- **Reference**: `docs/api/API_REFERENCE.md`
- **Deployment**: `docs/api/DEPLOYMENT_GUIDE.md`

## 🛠️ **Common Tasks**

### **Add New AI Service**
1. Create file in `apps/api/ai/`
2. Import in `apps/api/main.py`
3. Add config in `packages/config/settings.py`

### **Add New Component**
1. Create file in `apps/web/components/`
2. Import in your page
3. Add types if needed

### **Add New Test**
1. Create file in `tests/unit/`, `tests/integration/`, or `tests/e2e/`
2. Follow naming: `test_*.py`
3. Import the service you're testing

### **Update Configuration**
1. Edit `packages/config/settings.py`
2. Update environment variables
3. Restart services

## 🔧 **Development Tips**

### **Import Paths**
```python
# AI Services
from apps.api.ai.vertex_ai_service import vertex_ai_service
from apps.api.ai.ai_recommendation_engine import ai_recommendation_engine

# Infrastructure
from apps.api.infrastructure.caching import intelligent_caching_service
from apps.api.infrastructure.elasticsearch_service import elasticsearch_service

# Core
from apps.api.core.auth import auth_manager
from apps.api.database.connection import db_manager

# Configuration
from packages.config.settings import VERTEX_AI_ENABLED
```

### **Component Imports**
```typescript
// Web components
import { FaceUploadDialog } from '@/components/face-upload-dialog'
import { SkincareRoutineDialog } from '@/components/skincare-routine-dialog'
import { ProductCard } from '@/components/product-card'

// Shared utilities
import { utils } from '@/packages/shared/utils'
```

## 🚨 **Troubleshooting**

### **Import Errors**
```bash
# Check if file exists
ls apps/api/ai/vertex_ai_service.py

# Check import path
python -c "from apps.api.ai.vertex_ai_service import vertex_ai_service"
```

### **Service Not Starting**
```bash
# Check configuration
cat packages/config/settings.py

# Check environment
echo $VERTEX_AI_ENABLED

# Check logs
tail -f logs/dermalens.log
```

### **Component Not Found**
```bash
# Check component exists
ls apps/web/components/face-upload-dialog.tsx

# Check import path
grep -r "FaceUploadDialog" apps/web/
```

## 📊 **Performance Monitoring**

### **Check Metrics**
```bash
# API metrics
curl http://localhost:8000/metrics

# Health status
curl http://localhost:8000/health

# Cache stats
curl http://localhost:8000/cache/stats
```

### **Monitor Services**
```bash
# Check service health
curl http://localhost:8000/health | jq '.services'

# Check performance
curl http://localhost:8000/metrics/summary
```

## 🎯 **Best Practices**

### **File Organization**
- Keep related files together
- Use clear, descriptive names
- Follow established patterns
- Update imports when moving files

### **Development**
- Test changes locally first
- Update documentation
- Follow coding standards
- Use version control properly

### **Configuration**
- Use environment variables
- Keep secrets secure
- Document all settings
- Test configuration changes

---

**Need Help?** Check `NAVIGATION_INDEX.md` for detailed navigation or `README_REORGANIZED.md` for complete documentation.
