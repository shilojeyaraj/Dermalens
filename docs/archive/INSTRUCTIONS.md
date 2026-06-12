# Dermalens Setup Instructions

## Prerequisites
- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Git
- A code editor (VS Code recommended)

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Dermalens
```

### 2. Backend Setup (Python API)
```bash
# Navigate to backend directory
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see variables.txt)

# Start the backend server
python main.py
```

### 3. Frontend Setup (React/Next.js)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables Setup

### Required API Keys (see variables.txt for details):
1. **Supabase** (Database & Auth)
   - SUPABASE_URL
   - SUPABASE_ANON_KEY
   - SUPABASE_SERVICE_ROLE_KEY

2. **Google Gemini AI**
   - GEMINI_API_KEY

3. **Google Custom Search** (Product Search)
   - GOOGLE_SEARCH_API_KEY
   - GOOGLE_SEARCH_ENGINE_ID

4. **Elasticsearch** (Product Database)
   - ELASTICSEARCH_URL

5. **OpenAI** (Optional - for enhanced AI features)
   - OPENAI_API_KEY

## Database Setup

### Supabase Setup:
1. Create a new project at https://supabase.com
2. Go to Settings > API to get your keys
3. Run the SQL scripts in `auth_process/backend/scripts/` to set up tables

### Elasticsearch Setup:
1. Install Elasticsearch locally or use a cloud service
2. Update ELASTICSEARCH_URL in .env
3. Run the seed script to populate with sample products:
```bash
cd backend
python seed_elasticsearch_data.py
```

## Features Overview

### Core Features:
- **User Authentication**: Sign up, login, password reset
- **Profile Management**: User profiles with skin type and concerns
- **Face Scan Analysis**: Multi-angle camera scan with AI analysis
- **Product Recommendations**: Personalized skincare product suggestions
- **Skincare Routines**: AI-generated morning/evening routines

### AI Analysis:
- Multi-angle face scanning (center, left, right profiles)
- Skin condition detection (acne, wrinkles, dark spots, etc.)
- Image quality assessment (lighting, blur, face coverage)
- Profile-based recommendations when scan is skipped

### Product Search:
- Elasticsearch-powered product database
- Brand filtering and sorting
- Real product URLs and pricing
- Trending products display

## Troubleshooting

### Common Issues:

1. **Camera not working**:
   - Ensure HTTPS in production
   - Check browser permissions
   - Try different browsers

2. **API errors**:
   - Check all environment variables are set
   - Verify API keys are valid
   - Check backend logs for specific errors

3. **Database connection issues**:
   - Verify Supabase credentials
   - Check Elasticsearch is running
   - Ensure all tables are created

4. **Face scan analysis fails**:
   - Check Gemini API key
   - Verify image quality (good lighting, clear face)
   - Check backend logs for multipart form data issues

### Development Tips:
- Use browser dev tools to check console logs
- Backend logs show detailed analysis progress
- Test with different lighting conditions
- Use the "Skip Scan" option to test profile-based recommendations

## File Structure
```
Dermalens/
├── apps/api/                 # Backend Python API
├── frontend/                 # React/Next.js frontend
├── auth_process/            # Authentication setup
├── docs/                    # Documentation
└── INSTRUCTIONS.md          # This file
```

## Support
- Check the docs/ folder for detailed guides
- Review API documentation at http://localhost:8000/docs
- Check backend logs for error details
