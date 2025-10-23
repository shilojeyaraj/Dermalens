# Dermalens Codebase Reorganization Plan

## 🎯 **Current Issues**

1. **Scattered files** - Services, docs, and configs mixed together
2. **Duplicate structures** - Multiple frontend/backend folders
3. **Poor discoverability** - Hard to find specific functionality
4. **Mixed concerns** - AI services, database, docs all in one place
5. **Inconsistent naming** - Some files have prefixes, others don't

## 🏗️ **Proposed New Structure**

```
Dermalens/
├── 📁 apps/                          # Application entry points
│   ├── 📁 web/                       # Main web application
│   │   ├── 📁 app/                   # Next.js app directory
│   │   ├── 📁 components/            # React components
│   │   ├── 📁 lib/                   # Utilities and helpers
│   │   └── 📄 package.json
│   └── 📁 api/                       # Backend API
│       ├── 📁 core/                  # Core application logic
│       ├── 📁 services/              # Business logic services
│       ├── 📁 ai/                    # AI/ML services
│       ├── 📁 infrastructure/       # External integrations
│       ├── 📁 database/              # Database related
│       ├── 📁 monitoring/            # Performance monitoring
│       └── 📄 main.py
├── 📁 packages/                      # Shared packages
│   ├── 📁 shared/                    # Shared utilities
│   ├── 📁 types/                     # TypeScript types
│   └── 📁 config/                    # Configuration files
├── 📁 docs/                          # Documentation
│   ├── 📁 api/                       # API documentation
│   ├── 📁 guides/                    # User guides
│   ├── 📁 architecture/              # System architecture
│   └── 📁 deployment/                # Deployment guides
├── 📁 scripts/                       # Build and deployment scripts
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

## 🔄 **Migration Plan**

### **Phase 1: Create New Structure**
1. Create new directory structure
2. Move files to appropriate locations
3. Update import paths
4. Update configuration files

### **Phase 2: Clean Up**
1. Remove duplicate files
2. Consolidate similar functionality
3. Update documentation
4. Test all functionality

### **Phase 3: Optimize**
1. Add proper indexing
2. Create navigation helpers
3. Add search functionality
4. Optimize build processes

## 📋 **File Mapping**

### **Backend Files → New Structure**

| Current Location | New Location | Reason |
|------------------|--------------|---------|
| `backend/main.py` | `apps/api/main.py` | Main API entry point |
| `backend/enhanced_main.py` | `apps/api/main.py` | Enhanced version becomes main |
| `backend/vertex_ai_service.py` | `apps/api/ai/vertex_ai_service.py` | AI service |
| `backend/ai_recommendation_engine.py` | `apps/api/ai/recommendation_engine.py` | AI service |
| `backend/intelligent_caching_service.py` | `apps/api/infrastructure/caching.py` | Infrastructure |
| `backend/performance_monitoring_service.py` | `apps/api/monitoring/performance.py` | Monitoring |
| `backend/database.py` | `apps/api/database/connection.py` | Database |
| `backend/auth.py` | `apps/api/core/auth.py` | Core functionality |
| `backend/config.py` | `packages/config/settings.py` | Shared config |
| `backend/requirements.txt` | `apps/api/requirements.txt` | API dependencies |

### **Frontend Files → New Structure**

| Current Location | New Location | Reason |
|------------------|--------------|---------|
| `frontend/app/` | `apps/web/app/` | Next.js app directory |
| `frontend/components/` | `apps/web/components/` | React components |
| `frontend/lib/` | `apps/web/lib/` | Web utilities |
| `components/` | `apps/web/components/` | Root components |
| `lib/utils.ts` | `packages/shared/utils.ts` | Shared utilities |

### **Documentation Files → New Structure**

| Current Location | New Location | Reason |
|------------------|--------------|---------|
| `backend/*.md` | `docs/guides/` | User guides |
| `docs/` | `docs/api/` | API documentation |
| `README.md` | `README.md` | Root documentation |

## 🎯 **Benefits of New Structure**

### **1. Clear Separation of Concerns**
- **Apps**: Application entry points
- **Packages**: Shared code
- **Docs**: All documentation
- **Tests**: All testing code
- **Data**: All data and models

### **2. Easy Navigation**
- **AI services**: `apps/api/ai/`
- **Database**: `apps/api/database/`
- **Monitoring**: `apps/api/monitoring/`
- **Components**: `apps/web/components/`

### **3. Better Maintainability**
- Related files grouped together
- Clear import paths
- Easier to find and modify code
- Better for team collaboration

### **4. Scalability**
- Easy to add new services
- Clear patterns for new features
- Better for microservices architecture
- Easier to split into separate repositories

## 🚀 **Implementation Steps**

### **Step 1: Create Directory Structure**
```bash
mkdir -p apps/web/app
mkdir -p apps/web/components
mkdir -p apps/web/lib
mkdir -p apps/api/core
mkdir -p apps/api/services
mkdir -p apps/api/ai
mkdir -p apps/api/infrastructure
mkdir -p apps/api/database
mkdir -p apps/api/monitoring
mkdir -p packages/shared
mkdir -p packages/types
mkdir -p packages/config
mkdir -p docs/api
mkdir -p docs/guides
mkdir -p docs/architecture
mkdir -p docs/deployment
mkdir -p scripts
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/e2e
mkdir -p data/models
mkdir -p data/training
mkdir -p data/samples
```

### **Step 2: Move Files**
```bash
# Move backend files
mv backend/main.py apps/api/main.py
mv backend/enhanced_main.py apps/api/main.py
mv backend/vertex_ai_service.py apps/api/ai/
mv backend/ai_recommendation_engine.py apps/api/ai/
mv backend/intelligent_caching_service.py apps/api/infrastructure/
mv backend/performance_monitoring_service.py apps/api/monitoring/
mv backend/database.py apps/api/database/
mv backend/auth.py apps/api/core/
mv backend/config.py packages/config/

# Move frontend files
mv frontend/app apps/web/app
mv frontend/components apps/web/components
mv frontend/lib apps/web/lib
mv components/* apps/web/components/
mv lib/utils.ts packages/shared/

# Move documentation
mv backend/*.md docs/guides/
mv docs/* docs/api/
```

### **Step 3: Update Import Paths**
```python
# Update imports in Python files
from apps.api.ai.vertex_ai_service import vertex_ai_service
from apps.api.infrastructure.caching import intelligent_caching_service
from packages.config.settings import VERTEX_AI_ENABLED
```

### **Step 4: Update Configuration**
```json
// Update package.json files
{
  "name": "@dermalens/web",
  "dependencies": {
    "@dermalens/shared": "workspace:*"
  }
}
```

## 📊 **File Organization by Category**

### **🤖 AI Services** (`apps/api/ai/`)
- `vertex_ai_service.py` - Vertex AI integration
- `recommendation_engine.py` - AI recommendations
- `gemini_analysis_service.py` - Gemini analysis
- `openai_analysis_service.py` - OpenAI fallback
- `skin_analysis_service.py` - Skin analysis
- `comprehensive_analysis_service.py` - Comprehensive analysis
- `enhanced_comprehensive_analysis_service.py` - Enhanced analysis

### **🏗️ Infrastructure** (`apps/api/infrastructure/`)
- `caching.py` - Intelligent caching
- `elasticsearch_service.py` - Search service
- `google_search_service.py` - Google search
- `fivetran_connector.py` - Data pipeline
- `validation_service.py` - Input validation

### **📊 Monitoring** (`apps/api/monitoring/`)
- `performance.py` - Performance monitoring
- `health.py` - Health checks
- `metrics.py` - Metrics collection
- `alerts.py` - Alerting system

### **🗄️ Database** (`apps/api/database/`)
- `connection.py` - Database connection
- `models.py` - Data models
- `migrations/` - Database migrations
- `seeds/` - Seed data

### **🔧 Core** (`apps/api/core/`)
- `auth.py` - Authentication
- `middleware.py` - API middleware
- `exceptions.py` - Custom exceptions
- `utils.py` - Core utilities

### **🌐 Web Components** (`apps/web/components/`)
- `ui/` - UI components
- `forms/` - Form components
- `dialogs/` - Dialog components
- `pages/` - Page components

### **📚 Documentation** (`docs/`)
- `guides/` - User guides
- `api/` - API documentation
- `architecture/` - System architecture
- `deployment/` - Deployment guides

## 🎯 **Next Steps**

1. **Create the new structure**
2. **Move files systematically**
3. **Update all import paths**
4. **Test functionality**
5. **Update documentation**
6. **Clean up old files**

This reorganization will make the codebase much more maintainable and easier to navigate!
