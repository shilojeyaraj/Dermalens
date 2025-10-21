# Dermalens - Reorganized Codebase

## 🎯 **Overview**

The Dermalens codebase has been completely reorganized for better maintainability, easier navigation, and improved developer experience. This document explains the new structure and how to work with it.

## 🏗️ **New Directory Structure**

```
Dermalens/
├── 📁 apps/                          # Application entry points
│   ├── 📁 web/                       # Next.js frontend application
│   │   ├── 📁 app/                   # Next.js app directory
│   │   ├── 📁 components/            # React components
│   │   ├── 📁 lib/                   # Web utilities
│   │   └── 📄 package.json
│   └── 📁 api/                       # FastAPI backend application
│       ├── 📁 ai/                    # AI/ML services
│       ├── 📁 core/                  # Core application logic
│       ├── 📁 database/              # Database related
│       ├── 📁 infrastructure/       # External integrations
│       ├── 📁 monitoring/            # Performance monitoring
│       ├── 📄 main.py               # API entry point
│       └── 📄 requirements.txt
├── 📁 packages/                      # Shared packages
│   ├── 📁 shared/                    # Shared utilities
│   ├── 📁 types/                     # TypeScript types
│   └── 📁 config/                    # Configuration files
├── 📁 docs/                          # Documentation
│   ├── 📁 api/                       # API documentation
│   ├── 📁 guides/                    # User guides
│   ├── 📁 architecture/              # System architecture
│   └── 📁 deployment/                # Deployment guides
├── 📁 tests/                         # All tests
│   ├── 📁 unit/                      # Unit tests
│   ├── 📁 integration/               # Integration tests
│   └── 📁 e2e/                       # End-to-end tests
├── 📁 data/                          # Data and models
│   ├── 📁 models/                    # ML models
│   ├── 📁 training/                  # Training data
│   └── 📁 samples/                   # Sample data
└── 📄 README.md
```

## 🚀 **Quick Start**

### **1. Start the Backend API**
```bash
cd apps/api
pip install -r requirements.txt
python main.py
```

### **2. Start the Frontend Web App**
```bash
cd apps/web
npm install
npm run dev
```

### **3. Access the Application**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔍 **Finding Files**

### **AI Services** (`apps/api/ai/`)
- **Vertex AI**: `vertex_ai_service.py`
- **Recommendations**: `ai_recommendation_engine.py`
- **Gemini**: `gemini_analysis_service.py`
- **Skin Analysis**: `skin_analysis_service.py`
- **Comprehensive Analysis**: `comprehensive_analysis_service.py`
- **Enhanced Analysis**: `enhanced_comprehensive_analysis_service.py`

### **Infrastructure** (`apps/api/infrastructure/`)
- **Caching**: `caching.py`
- **Elasticsearch**: `elasticsearch_service.py`
- **Google Search**: `google_search_service.py`
- **Data Pipeline**: `fivetran_connector.py`
- **Validation**: `validation_service.py`

### **Monitoring** (`apps/api/monitoring/`)
- **Performance**: `performance.py`

### **Database** (`apps/api/database/`)
- **Connection**: `connection.py`

### **Core** (`apps/api/core/`)
- **Authentication**: `auth.py`

### **Configuration** (`packages/config/`)
- **Settings**: `settings.py`

### **Web Components** (`apps/web/components/`)
- **UI Components**: `ui/`
- **Face Upload**: `face-upload-dialog.tsx`
- **Routine Dialog**: `skincare-routine-dialog.tsx`
- **Product Card**: `product-card.tsx`
- **User Profile**: `user-profile-dialog.tsx`

## 📚 **Documentation**

### **User Guides** (`docs/guides/`)
- **Setup Guide**: `SETUP_GUIDE.md`
- **Enhanced AI Implementation**: `ENHANCED_AI_IMPLEMENTATION_GUIDE.md`
- **Multi-Agent vs Single-Agent**: `MULTI_AGENT_VS_SINGLE_AGENT_GUIDE.md`
- **Gemini Migration**: `GEMINI_MIGRATION_GUIDE.md`
- **Google API Setup**: `GOOGLE_API_QUICK_START.md`
- **Database Setup**: `DATABASE_SETUP.md`
- **Production Setup**: `production_setup.md`

### **API Documentation** (`docs/api/`)
- **API Reference**: `API_REFERENCE.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`

## 🧪 **Testing**

### **Run All Tests**
```bash
cd tests
python -m pytest
```

### **Run Specific Test Types**
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# End-to-end tests
python -m pytest tests/e2e/
```

## 🔧 **Development Workflow**

### **1. Making Changes**
- Edit files in their organized locations
- Follow established patterns
- Update imports if you move files

### **2. Adding New Features**
- **AI Service**: Add to `apps/api/ai/`
- **Infrastructure**: Add to `apps/api/infrastructure/`
- **Component**: Add to `apps/web/components/`
- **Test**: Add to appropriate `tests/` subdirectory

### **3. Configuration Changes**
- Update `packages/config/settings.py`
- Update environment variables
- Update documentation

## 📊 **Data Management**

### **Models** (`data/models/`)
- ML model files (`.pth`, `.pkl`, etc.)
- Model weights and checkpoints

### **Training Data** (`data/training/`)
- Training datasets
- Image collections
- Labeled data

### **Samples** (`data/samples/`)
- Sample images
- Test data
- Demo content

## 🚀 **Deployment**

### **Development**
```bash
# Start all services
npm run dev:all
```

### **Production**
```bash
# Build and deploy
npm run build
npm run deploy
```

### **Docker**
```bash
# Build containers
docker-compose build

# Run services
docker-compose up
```

## 🔍 **Navigation Helpers**

### **Find AI Services**
```bash
find apps/api/ai/ -name "*.py" | grep -E "(analysis|recommendation|vertex|gemini)"
```

### **Find Components**
```bash
find apps/web/components/ -name "*.tsx" | grep -E "(dialog|card|upload)"
```

### **Find Documentation**
```bash
find docs/ -name "*.md" | grep -E "(guide|setup|api)"
```

## 🎯 **Benefits of New Organization**

### **✅ Better Maintainability**
- Related files grouped together
- Clear separation of concerns
- Consistent naming conventions

### **✅ Easier Navigation**
- Logical directory structure
- Clear file purposes
- Easy to find specific functionality

### **✅ Improved Scalability**
- Can split into microservices
- Clear boundaries between services
- Easy to add new features

### **✅ Better Team Collaboration**
- Clear ownership of directories
- Consistent patterns
- Easy onboarding for new developers

## 🔄 **Migration from Old Structure**

### **What Changed**
- **Backend files** moved from `backend/` to `apps/api/`
- **Frontend files** moved from `frontend/` to `apps/web/`
- **Components** consolidated in `apps/web/components/`
- **Documentation** organized in `docs/`
- **Tests** organized in `tests/`
- **Data** organized in `data/`

### **Import Updates Needed**
```python
# Old imports
from backend.vertex_ai_service import vertex_ai_service
from backend.config import VERTEX_AI_ENABLED

# New imports
from apps.api.ai.vertex_ai_service import vertex_ai_service
from packages.config.settings import VERTEX_AI_ENABLED
```

### **Configuration Updates**
```bash
# Old paths
python backend/main.py
cd frontend && npm run dev

# New paths
python apps/api/main.py
cd apps/web && npm run dev
```

## 📋 **Maintenance Tasks**

### **Regular Cleanup**
- Remove unused files
- Update documentation
- Clean up old configurations
- Update dependencies

### **Performance Monitoring**
- Check `apps/api/monitoring/performance.py`
- Review metrics and logs
- Optimize based on data

### **Security Updates**
- Update API keys in `packages/config/settings.py`
- Review authentication in `apps/api/core/auth.py`
- Check infrastructure security

## 🎉 **Getting Help**

### **Documentation**
- **Navigation**: `NAVIGATION_INDEX.md`
- **Guides**: `docs/guides/`
- **API**: `docs/api/`

### **Code Organization**
- **AI Services**: `apps/api/ai/`
- **Infrastructure**: `apps/api/infrastructure/`
- **Components**: `apps/web/components/`

### **Configuration**
- **Settings**: `packages/config/settings.py`
- **Environment**: `enhanced.env.example`

---

**Last Updated**: December 2024  
**Maintainer**: Dermalens Team  
**Version**: 2.0.0-reorganized
