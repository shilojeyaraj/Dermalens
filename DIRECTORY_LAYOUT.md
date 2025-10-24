# Dermalens Project Directory Layout

## 📁 **Current Project Structure**

This document provides the complete directory layout for the Dermalens AI skincare analysis application. Use this to reorganize and understand the project structure.

## 🏗️ **Root Directory Structure**

```
Dermalens/
├── 📁 app/                          # Next.js App Router (Root Level)
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
│
├── 📁 apps/                         # Applications Directory
│   ├── 📁 api/                      # Backend API (Main)
│   │   ├── 📁 __pycache__/         # Python Cache
│   │   ├── 📁 ai/                  # AI Services
│   │   │   ├── enhanced_comprehensive_analysis_service.py
│   │   │   ├── enhanced_product_recommendation_service.py
│   │   │   ├── enhanced_skin_analysis_service.py
│   │   │   ├── enhanced_skin_analysis_service_simple.py
│   │   │   ├── gemini_analysis_service.py
│   │   │   ├── skin_analysis_service.py
│   │   │   ├── vertex_ai_service.py
│   │   │   └── [4 more AI files]
│   │   ├── 📁 core/                 # Core Services
│   │   │   ├── auth_manager.py
│   │   │   └── validation_service.py
│   │   ├── 📁 database/             # Database Services
│   │   │   ├── database_manager.py
│   │   │   └── user_manager.py
│   │   ├── 📁 infrastructure/       # Infrastructure Services
│   │   │   ├── caching.py
│   │   │   ├── elasticsearch_service.py
│   │   │   ├── google_search_service.py
│   │   │   ├── monitoring.py
│   │   │   ├── performance_monitoring.py
│   │   │   └── redis_service.py
│   │   ├── 📁 monitoring/           # Monitoring Services
│   │   │   ├── analytics.py
│   │   │   └── performance.py
│   │   ├── 📁 services/             # Additional Services
│   │   ├── main.py                  # 🚀 MAIN API SERVER
│   │   ├── requirements.txt
│   │   ├── test_face_scan.py        # Face Scan Test
│   │   ├── basic_test.py           # Basic API Test
│   │   └── [8 more Python files]
│   │
│   └── 📁 web/                      # Web Application
│       ├── 📁 app/                  # Next.js App Router
│       ├── 📁 components/           # React Components
│       └── 📁 lib/                  # Utilities
│
├── 📁 auth_process/                 # Authentication Process
│   ├── 📁 backend/
│   │   └── 📁 scripts/             # SQL Scripts
│   ├── 📁 frontend/
│   │   └── 📁 src/                 # Auth Components
│   └── README.md
│
├── 📁 backend/                      # Legacy Backend (Deprecated)
│   ├── 📁 __pycache__/
│   ├── 📁 models/
│   ├── 📁 training_data/
│   ├── main.py                      # Legacy Main
│   ├── seed_elasticsearch_data.py   # Data Seeding
│   ├── requirements.txt
│   └── [20+ Python files]
│
├── 📁 components/                   # Shared UI Components
│   └── 📁 ui/                      # UI Components
│       ├── avatar.tsx
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── face-scan-avatar.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── separator.tsx
│       ├── slider.tsx
│       └── textarea.tsx
│
├── 📁 data/                        # Training Data & Models
│   ├── 📁 models/
│   │   └── skin_classifier.pth      # ML Model
│   ├── 📁 samples/
│   └── 📁 training/                # Training Images
│       ├── 📁 acne/
│       ├── 📁 blackheads/
│       ├── 📁 dark_spots/
│       ├── 📁 dry_skin/
│       ├── 📁 eczema/
│       ├── 📁 hyperpigmentation/
│       ├── 📁 normal_skin/
│       ├── 📁 oily_skin/
│       ├── 📁 rosacea/
│       ├── 📁 sensitive_skin/
│       ├── 📁 whiteheads/
│       └── 📁 wrinkles/
│
├── 📁 docs/                        # Documentation
│   ├── 📁 api/                     # API Documentation
│   │   ├── API_REFERENCE.md
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── 📁 architecture/
│   │   ├── 📁 deployment/
│   │   └── 📁 guides/              # 15 guide files
│   ├── 📁 auth/                    # Authentication Docs
│   │   ├── AUTH_FIX_SUMMARY.md
│   │   ├── CUSTOM_AUTH_MIGRATION_COMPLETE.md
│   │   ├── PASSWORD_VISIBILITY_FEATURE.md
│   │   ├── QUICK_SUPABASE_FIX.sql
│   │   └── SUPABASE_DEBUG_GUIDE.md
│   ├── 📁 deployment/              # Deployment Docs
│   │   ├── deploy_production.sh
│   │   ├── HTTPS_SETUP_GUIDE.md
│   │   └── PRODUCTION_READY_CHECKLIST.md
│   ├── 📁 development/             # Development Docs
│   │   ├── CLEARERROR_AND_BUTTON_STYLING_FIXED.md
│   │   ├── CLEARERROR_FIX_FINAL.md
│   │   ├── COMPLETE_APP_FLOW.md
│   │   ├── DEMO_VIDEO_SCRIPT.md
│   │   └── NAVIGATION_INDEX.md
│   ├── 📁 features/                # Feature Docs (9 files)
│   ├── 📁 frontend/                # Frontend Docs (7 files)
│   ├── 📁 progress/                # Progress Docs
│   │   ├── CODEBASE_OVERVIEW.md
│   │   ├── CODEBASE_REORGANIZATION_PLAN.md
│   │   ├── REORGANIZATION_SUMMARY.md
│   │   └── SETUP_STATUS.md
│   ├── 📁 setup/                   # Setup Docs
│   │   ├── PYTHON_DOWNGRADE_GUIDE.md
│   │   ├── QUICK_REFERENCE.md
│   │   ├── quick_start.bat
│   │   └── quick_start.sh
│   ├── 📁 status/                  # Status Docs (4 files)
│   ├── INDEX.md                    # Main Documentation Index
│   └── README.md
│
├── 📁 frontend/                    # Main Frontend Application
│   ├── 📁 app/                     # Next.js App Router
│   │   ├── 📁 dashboard/           # Dashboard Page
│   │   ├── 📁 scan/                # Face Scan Page
│   │   ├── 📁 signup/              # Signup Page
│   │   ├── 📁 login/               # Login Page
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── 📁 components/              # React Components (34 files)
│   │   ├── product-search.tsx
│   │   ├── product-filters.tsx
│   │   ├── real-product-card.tsx
│   │   ├── landing-page.tsx
│   │   └── [30 more components]
│   ├── 📁 contexts/                # React Contexts
│   │   ├── auth-context.tsx
│   │   └── user-context.tsx
│   ├── 📁 lib/                     # Utilities
│   ├── 📁 public/                 # Static Assets
│   │   ├── hero-left-profile.jpg
│   │   └── hero-right-profile.jpg
│   ├── 📁 node_modules/            # Dependencies
│   ├── package.json                # Frontend Dependencies
│   ├── package-lock.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── postcss.config.js
│   ├── skincarelogo.jpeg
│   └── requirements.txt
│
├── 📁 lib/                         # Shared Libraries
├── 📁 node_modules/                # Root Dependencies
├── 📁 packages/                    # Shared Packages
│   ├── 📁 config/
│   │   └── settings.py             # Configuration
│   ├── 📁 shared/
│   │   └── types.ts                # Shared Types
│   └── 📁 types/                   # TypeScript Types
│
├── 📁 scripts/                     # Build Scripts
├── 📁 tests/                       # Test Files
│   ├── 📁 e2e/                     # End-to-End Tests
│   ├── 📁 integration/             # Integration Tests
│   └── 📁 unit/                    # Unit Tests
│
├── 📁 venv/                        # Python Virtual Environment
│   ├── 📁 Include/
│   ├── 📁 Lib/
│   ├── 📁 Scripts/
│   ├── 📁 share/
│   └── pyvenv.cfg
│
├── 📄 Configuration Files
├── .gitignore                      # Git Ignore Rules
├── docker-compose.yml              # Docker Configuration
├── INSTRUCTIONS.md                 # Setup Instructions
├── README.md                       # Project Readme
├── variables.txt                   # Environment Variables
├── package.json                    # Root Package.json
├── package-lock.json
├── postcss.config.js
├── tailwind.config.js
├── requirements.txt                # Python Dependencies
├── skincarelogo.jpeg              # Logo File
├── Redis-x64-3.0.504.msi          # Redis Installer
└── test_face_scan.py              # Test Script
```

## 🎯 **Key Directories Explained**

### **🚀 Main Application Entry Points**
- **`apps/api/main.py`** - Main backend API server (FastAPI)
- **`frontend/app/`** - Main frontend application (Next.js)
- **`frontend/app/scan/page.tsx`** - Face scan functionality
- **`frontend/app/dashboard/page.tsx`** - User dashboard

### **🤖 AI & Analysis Services**
- **`apps/api/ai/`** - All AI services (skin analysis, product recommendations)
- **`apps/api/infrastructure/`** - Infrastructure services (Elasticsearch, Redis, etc.)
- **`data/training/`** - ML training data for skin condition classification

### **🎨 Frontend Components**
- **`frontend/components/`** - Reusable React components
- **`components/ui/`** - Shared UI components (buttons, cards, etc.)
- **`frontend/app/`** - Next.js pages and layouts

### **📚 Documentation**
- **`docs/`** - Comprehensive project documentation
- **`docs/api/`** - API documentation and guides
- **`docs/features/`** - Feature-specific documentation

### **🔧 Configuration & Setup**
- **`packages/config/settings.py`** - Application configuration
- **`INSTRUCTIONS.md`** - Setup instructions
- **`variables.txt`** - Environment variables template

## 🚨 **Important Notes for Reorganization**

### **⚠️ Duplicate/Conflicting Directories**
1. **Multiple `app/` directories**: Root level and `frontend/app/`
2. **Multiple `main.py` files**: `apps/api/main.py` (active) vs `backend/main.py` (legacy)
3. **Multiple `package.json` files**: Root and frontend directories
4. **Multiple `requirements.txt` files**: Root, `apps/api/`, and `frontend/`

### **🎯 Recommended Clean Structure**
```
Dermalens/
├── 📁 backend/                     # All backend code
│   ├── 📁 api/                     # FastAPI application
│   ├── 📁 ai/                      # AI services
│   ├── 📁 infrastructure/           # Infrastructure services
│   └── main.py                     # Main server
├── 📁 frontend/                    # All frontend code
│   ├── 📁 app/                     # Next.js pages
│   ├── 📁 components/              # React components
│   └── 📁 lib/                     # Utilities
├── 📁 docs/                        # Documentation
├── 📁 data/                        # Training data & models
├── 📁 tests/                       # Test files
└── 📄 Configuration files
```

## 🔧 **Setup Instructions for Your Friend**

1. **Clone the repository**
2. **Navigate to the project directory**
3. **Follow the structure in this document**
4. **Use `apps/api/main.py` as the main backend server**
5. **Use `frontend/` as the main frontend application**
6. **Ignore the legacy `backend/` directory**
7. **Check `INSTRUCTIONS.md` for detailed setup steps**

## 📞 **Support Files**
- **`INSTRUCTIONS.md`** - Complete setup guide
- **`variables.txt`** - Environment variables needed
- **`docs/INDEX.md`** - Documentation index
- **`README.md`** - Project overview

---

**💡 Tip**: Focus on the `apps/api/` and `frontend/` directories as they contain the active application code. The legacy `backend/` directory can be ignored or removed.
