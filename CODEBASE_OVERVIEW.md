# Dermalens Codebase Overview

## Project Description
Dermalens is an AI-powered skincare analysis application that uses computer vision to analyze skin conditions from uploaded images/videos and provides personalized product recommendations and skincare routines.

## Architecture Overview

### Backend (Python/FastAPI)
**Location**: `backend/` folder
**Technology Stack**: 
- FastAPI (web framework)
- PyTorch (deep learning)
- OpenCV (computer vision)
- Python 3.8+

#### Key Files:
- `main.py` - Main FastAPI application with all endpoints
- `train_model.py` - Model training script
- `requirements.txt` - Python dependencies
- `models/skin_classifier.pth` - Pre-trained PyTorch model
- `training_data/` - Organized folders for skin condition images

#### API Endpoints:
1. **POST `/analyze-skin`** - Main endpoint for skin analysis
   - Accepts image/video uploads
   - Returns detected skin conditions, product recommendations, and skincare routine
   
2. **POST `/search-products`** - Search products by skin conditions
3. **POST `/generate-routine`** - Generate personalized skincare routine
4. **GET `/health`** - Health check endpoint

#### AI Model:
- **Custom CNN Architecture**: 4-layer convolutional network
- **Input**: 224x224 RGB images
- **Output**: 12 skin condition classes
- **Classes**: acne, hyperpigmentation, dark_spots, wrinkles, dry_skin, oily_skin, sensitive_skin, normal_skin, blackheads, whiteheads, rosacea, eczema

#### Key Features:
- Face detection using OpenCV Haar cascades
- Multi-face support in images/videos
- Confidence-based filtering
- Mock product database (ready for Google Store API integration)
- Automated skincare routine generation

### Frontend (Next.js/React)
**Location**: `frontend/` folder
**Technology Stack**:
- Next.js 14.2.33
- React 18.3.1
- TypeScript
- Tailwind CSS
- Radix UI components

#### Key Files:
- `app/page.tsx` - Landing page
- `app/login/page.tsx` - Login page
- `app/signup/page.tsx` - Signup page
- `app/layout.tsx` - Root layout with fonts
- `components/ui/` - Reusable UI components
- `tailwind.config.js` - Tailwind configuration

#### Pages:
1. **Home Page** (`/`) - Landing page with app overview and navigation
2. **Login Page** (`/login`) - User authentication
3. **Signup Page** (`/signup`) - User registration

#### UI Components:
- Modern, responsive design
- Gradient backgrounds
- Card-based layouts
- Form validation
- Loading states

## Current Status

### ✅ What's Working:
- Backend API server (FastAPI)
- AI model architecture and training pipeline
- Frontend development server (Next.js)
- Basic authentication pages
- CORS configuration for frontend-backend communication
- Organized training data structure

### 🔄 What Needs Integration:
- Frontend-backend API calls
- User authentication system
- Image upload functionality
- Results display components
- Product recommendation UI

### 📁 Project Structure:
```
Dermalens/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── train_model.py          # Model training
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   └── skin_classifier.pth # Trained model
│   ├── training_data/          # Organized by skin condition
│   │   ├── acne/
│   │   ├── hyperpigmentation/
│   │   ├── dark_spots/
│   │   ├── wrinkles/
│   │   ├── dry_skin/
│   │   ├── oily_skin/
│   │   ├── sensitive_skin/
│   │   ├── normal_skin/
│   │   ├── blackheads/
│   │   ├── whiteheads/
│   │   ├── rosacea/
│   │   └── eczema/
│   └── .env                    # Environment variables
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Home page
│   │   ├── login/page.tsx     # Login page
│   │   ├── signup/page.tsx    # Signup page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/ui/         # UI components
│   ├── package.json           # Node dependencies
│   ├── tailwind.config.js     # Tailwind config
│   └── tsconfig.json          # TypeScript config
└── CODEBASE_OVERVIEW.md       # This file
```

## Getting Started

### Backend Setup:
```bash
cd backend
pip install -r requirements.txt
python main.py  # Starts server on http://localhost:8000
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev  # Starts server on http://localhost:3000
```

## Next Steps for Development

1. **Connect Frontend to Backend**:
   - Add API client functions
   - Create image upload component
   - Display analysis results

2. **Enhance Authentication**:
   - Implement actual user registration/login
   - Add session management
   - Create user profiles

3. **Improve AI Model**:
   - Add more training data
   - Fine-tune model parameters
   - Implement model versioning

4. **Add Features**:
   - Product comparison
   - Routine tracking
   - Progress monitoring
   - Social features

## Technical Notes

- **CORS**: Configured for localhost:3000 (frontend) to communicate with localhost:8000 (backend)
- **Model**: Currently uses mock data for products, ready for Google Store API integration
- **File Upload**: Supports both images and videos
- **Error Handling**: Comprehensive error handling in both frontend and backend
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## Dependencies

### Backend:
- FastAPI, Uvicorn (web server)
- PyTorch, Torchvision (AI/ML)
- OpenCV (computer vision)
- Pillow (image processing)
- NumPy (numerical computing)

### Frontend:
- Next.js, React (framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Radix UI (component library)
- Lucide React (icons)

This codebase provides a solid foundation for a complete skincare analysis application with room for expansion and enhancement.
