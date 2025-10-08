@echo off
echo Dermalens Backend Installation
echo =============================

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating .env file...
if not exist .env (
    echo # Dermalens Backend Environment Variables > .env
    echo. >> .env
    echo # Google Store API (optional - currently using mock data) >> .env
    echo GOOGLE_STORE_API_KEY=your_api_key_here >> .env
    echo GOOGLE_STORE_API_URL=https://www.googleapis.com/books/v1/volumes >> .env
    echo. >> .env
    echo # Model settings >> .env
    echo MODEL_PATH=models/skin_classifier.pth >> .env
    echo CONFIDENCE_THRESHOLD=0.3 >> .env
    echo. >> .env
    echo # API settings >> .env
    echo API_HOST=0.0.0.0 >> .env
    echo API_PORT=8000 >> .env
    echo DEBUG=True >> .env
    echo. >> .env
    echo # CORS settings (for frontend integration) >> .env
    echo ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000 >> .env
    echo. >> .env
    echo # Training settings >> .env
    echo TRAINING_DATA_PATH=training_data >> .env
    echo BATCH_SIZE=32 >> .env
    echo LEARNING_RATE=0.001 >> .env
    echo EPOCHS=50 >> .env
    echo .env file created successfully!
) else (
    echo .env file already exists, skipping...
)

echo.
echo Creating additional directories...
if not exist models mkdir models
if not exist temp_uploads mkdir temp_uploads
if not exist logs mkdir logs

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Add training images to the training_data folders
echo 2. Run: python train_model.py (to train the model)
echo 3. Run: python main.py (to start the API server)
echo.
pause
