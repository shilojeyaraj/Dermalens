# Dermalens Setup Guide

## What You Need to Install

### 1. Python Dependencies
Run this command in the `backend` folder:
```bash
pip install -r requirements.txt
```

### 2. Create .env File
Create a file named `.env` in the `backend` folder with this content:

```env
# Dermalens Backend Environment Variables

# Supabase Configuration
SUPABASE_URL=https://ezlevlxkxanlceofykrh.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NzYxNTksImV4cCI6MjA3NTM1MjE1OX0.oPovEwcfN-jhHPxFOczj3RkmCX2QZICQYnfmo6hQwhg
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6bGV2bHhreGFubGNlb2Z5a3JoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTc3NjE1OSwiZXhwIjoyMDc1MzUyMTU5fQ.SbhkLCmjqUDA1oBWLnXVzOeoiKYriiXe7AZ6L-9C2ag

# JWT Configuration
JWT_SECRET=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Model settings
MODEL_PATH=models/skin_classifier.pth
CONFIDENCE_THRESHOLD=0.3

# API settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS settings (for frontend integration)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Training settings
TRAINING_DATA_PATH=training_data
BATCH_SIZE=32
LEARNING_RATE=0.001
EPOCHS=50

# File Upload Configuration
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=image/jpeg,image/jpg,image/png,video/mp4
```

## Training Data Folders Created

I've created the following folders for your training images:

```
backend/training_data/
├── acne/                    # Put acne images here
├── hyperpigmentation/       # Put hyperpigmentation images here
├── dark_spots/             # Put dark spots images here
├── wrinkles/               # Put wrinkles images here
├── dry_skin/               # Put dry skin images here
├── oily_skin/              # Put oily skin images here
├── sensitive_skin/         # Put sensitive skin images here
├── normal_skin/            # Put normal skin images here
├── blackheads/             # Put blackheads images here
├── whiteheads/             # Put whiteheads images here
├── rosacea/                # Put rosacea images here
└── eczema/                 # Put eczema images here
```

## How to Use

### 1. Add Training Images
- Place your skin condition images in the appropriate folders
- Supported formats: PNG, JPG, JPEG
- Try to have at least 10-20 images per condition for good results

### 2. Train the Model
```bash
cd backend
python train_model.py
```

### 3. Start the API Server
```bash
cd backend
python main.py
```

### 4. Start the Frontend
```bash
# In the main project directory
npm run dev
```

## What Each Folder Is For

- **acne**: Images showing acne, pimples, breakouts
- **hyperpigmentation**: Dark spots, melasma, uneven skin tone
- **dark_spots**: Age spots, sun spots, post-inflammatory hyperpigmentation
- **wrinkles**: Fine lines, crow's feet, forehead lines
- **dry_skin**: Flaky, dehydrated, rough skin texture
- **oily_skin**: Shiny, greasy, large pores
- **sensitive_skin**: Redness, irritation, reactive skin
- **normal_skin**: Healthy, balanced skin
- **blackheads**: Open comedones, clogged pores
- **whiteheads**: Closed comedones, small bumps
- **rosacea**: Facial redness, visible blood vessels
- **eczema**: Atopic dermatitis, dry patches, inflammation

## Tips for Good Training Data

1. **Use clear, well-lit images**
2. **Include various angles and lighting conditions**
3. **Have a mix of mild and severe cases**
4. **Ensure images show the condition clearly**
5. **Try to have similar numbers of images per condition**

## Troubleshooting

- If you get import errors, make sure all dependencies are installed
- If training fails, check that you have images in the folders
- If the API doesn't start, check that port 8000 is available
- If the frontend can't connect, make sure the backend is running on port 8000
