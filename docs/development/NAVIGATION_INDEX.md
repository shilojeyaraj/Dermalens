# Dermalens Codebase Navigation Index

## 🗂️ **Quick Navigation**

### **📱 Applications**
- **Web App**: `apps/web/` - Next.js frontend application
- **API**: `apps/api/` - FastAPI backend application

### **🤖 AI Services** (`apps/api/ai/`)
- `vertex_ai_service.py` - Google Vertex AI integration
- `ai_recommendation_engine.py` - AI-powered product recommendations
- `gemini_analysis_service.py` - Google Gemini analysis
- `openai_analysis_service.py` - OpenAI fallback service
- `skin_analysis_service.py` - Core skin analysis
- `comprehensive_analysis_service.py` - Comprehensive analysis
- `enhanced_comprehensive_analysis_service.py` - Enhanced analysis with AI

### **🏗️ Infrastructure** (`apps/api/infrastructure/`)
- `caching.py` - Intelligent caching system
- `elasticsearch_service.py` - Search and indexing
- `google_search_service.py` - Google Custom Search
- `fivetran_connector.py` - Data pipeline integration
- `validation_service.py` - Input validation

### **📊 Monitoring** (`apps/api/monitoring/`)
- `performance.py` - Performance monitoring and analytics

### **🗄️ Database** (`apps/api/database/`)
- `connection.py` - Database connection and management

### **🔧 Core** (`apps/api/core/`)
- `auth.py` - Authentication and authorization

### **⚙️ Configuration** (`packages/config/`)
- `settings.py` - Application configuration and environment variables

### **🌐 Web Components** (`apps/web/components/`)
- `ui/` - Reusable UI components
- `face-upload-dialog.tsx` - Face upload functionality
- `skincare-routine-dialog.tsx` - Routine display
- `product-card.tsx` - Product display
- `user-profile-dialog.tsx` - User profile management

### **📚 Documentation**
- **Guides**: `docs/guides/` - User guides and setup instructions
- **API**: `docs/api/` - API documentation
- **Architecture**: `docs/architecture/` - System architecture docs
- **Deployment**: `docs/deployment/` - Deployment guides

### **🧪 Testing**
- **Unit Tests**: `tests/unit/` - Unit tests
- **Integration Tests**: `tests/integration/` - Integration tests
- **E2E Tests**: `tests/e2e/` - End-to-end tests

### **📊 Data**
- **Models**: `data/models/` - ML models and weights
- **Training**: `data/training/` - Training datasets
- **Samples**: `data/samples/` - Sample data

## 🚀 **Quick Start**

### **Start the API**
```bash
cd apps/api
python main.py
```

### **Start the Web App**
```bash
cd apps/web
npm run dev
```

### **Run Tests**
```bash
cd tests
python -m pytest
```

## 🔍 **Finding Specific Functionality**

### **Looking for AI Analysis?**
- **Core Analysis**: `apps/api/ai/skin_analysis_service.py`
- **Enhanced Analysis**: `apps/api/ai/enhanced_comprehensive_analysis_service.py`
- **Vertex AI**: `apps/api/ai/vertex_ai_service.py`

### **Looking for Product Recommendations?**
- **AI Recommendations**: `apps/api/ai/ai_recommendation_engine.py`
- **Search Integration**: `apps/api/infrastructure/elasticsearch_service.py`
- **Google Search**: `apps/api/infrastructure/google_search_service.py`

### **Looking for Caching?**
- **Intelligent Caching**: `apps/api/infrastructure/caching.py`

### **Looking for Monitoring?**
- **Performance Monitoring**: `apps/api/monitoring/performance.py`

### **Looking for Database?**
- **Database Connection**: `apps/api/database/connection.py`

### **Looking for Authentication?**
- **Auth Service**: `apps/api/core/auth.py`

### **Looking for Configuration?**
- **Settings**: `packages/config/settings.py`

## 📁 **File Type Organization**

### **Python Files**
- **AI Services**: `apps/api/ai/*.py`
- **Infrastructure**: `apps/api/infrastructure/*.py`
- **Core**: `apps/api/core/*.py`
- **Database**: `apps/api/database/*.py`
- **Monitoring**: `apps/api/monitoring/*.py`

### **TypeScript/React Files**
- **Components**: `apps/web/components/*.tsx`
- **Pages**: `apps/web/app/*.tsx`
- **Utilities**: `apps/web/lib/*.ts`
- **Shared**: `packages/shared/*.ts`

### **Configuration Files**
- **Environment**: `packages/config/settings.py`
- **Dependencies**: `apps/api/requirements.txt`
- **Package**: `apps/web/package.json`

### **Documentation Files**
- **Guides**: `docs/guides/*.md`
- **API Docs**: `docs/api/*.md`
- **Architecture**: `docs/architecture/*.md`

## 🎯 **Common Tasks**

### **Add New AI Service**
1. Create file in `apps/api/ai/`
2. Import in `apps/api/main.py`
3. Add to configuration in `packages/config/settings.py`

### **Add New Component**
1. Create file in `apps/web/components/`
2. Import in your page/component
3. Add to shared types if needed

### **Add New Infrastructure Service**
1. Create file in `apps/api/infrastructure/`
2. Import in `apps/api/main.py`
3. Add configuration if needed

### **Add New Test**
1. Create file in appropriate `tests/` subdirectory
2. Follow naming convention: `test_*.py`
3. Import the service you're testing

## 🔧 **Development Workflow**

### **1. Make Changes**
- Edit files in their organized locations
- Follow the established patterns
- Update imports if you move files

### **2. Test Changes**
- Run unit tests: `python -m pytest tests/unit/`
- Run integration tests: `python -m pytest tests/integration/`
- Test the API: `curl http://localhost:8000/health`

### **3. Update Documentation**
- Update relevant docs in `docs/`
- Add new guides if needed
- Update this navigation index

### **4. Deploy**
- Follow deployment guides in `docs/deployment/`
- Use scripts in `scripts/` directory

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

## 🎉 **Benefits of This Organization**

### **✅ Easy to Find**
- Related files are grouped together
- Clear naming conventions
- Logical directory structure

### **✅ Easy to Maintain**
- Clear separation of concerns
- Consistent patterns
- Easy to add new features

### **✅ Easy to Scale**
- Can split into microservices
- Clear boundaries between services
- Easy to add new team members

### **✅ Easy to Test**
- Tests are organized by type
- Clear testing patterns
- Easy to run specific test suites

---

**Last Updated**: December 2024  
**Maintainer**: Dermalens Team
